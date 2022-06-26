import json
import math
import os
import shutil
import time
import traceback
from datetime import datetime
from os.path import exists
from pathlib import Path
from threading import Thread
from typing import List

import yaml
from execo_engine import sweep, ParamSweeper

from evaluation.experiment import concerto_d_g5k, generate_transitions_time


finished_nodes = []
results = {}
sleeping_times_nodes = {}


def execute_reconf_in_g5k(roles, assembly_name, reconf_config_file_path, duration, dep_num, node_num, experiment_num):
    timestamp_log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Execute reconf
    sleeping_times_nodes[assembly_name]["total_sleeping_time"] += time.time() - sleeping_times_nodes[assembly_name]["current_down_time"]
    concerto_d_g5k.execute_reconf(roles[assembly_name], reconf_config_file_path, duration, timestamp_log_dir, dep_num, experiment_num)
    sleeping_times_nodes[assembly_name]["current_down_time"] = time.time()

    # Fetch and compute results
    concerto_d_g5k.fetch_times_log_file(roles[assembly_name], assembly_name, dep_num, timestamp_log_dir)
    compute_results(assembly_name, concerto_d_g5k.build_times_log_path(assembly_name, dep_num, timestamp_log_dir))

    # Finish reconf for assembly name if its over
    concerto_d_g5k.fetch_finished_reconfiguration_file(roles[assembly_name], assembly_name, dep_num)
    if exists(f"concerto/{concerto_d_g5k.build_finished_reconfiguration_path(assembly_name, dep_num)}"):
        print("reconf finished")
        finished_nodes.append(node_num)


def compute_results(assembly_name: str, timestamp_log_file: str):
    with open(f"evaluation/experiment/results_experiment/logs_files_assemblies/{timestamp_log_file}", "r") as f:
        loaded_results = yaml.safe_load(f)

    if assembly_name not in results.keys():
        results[assembly_name] = {
            "total_uptime_duration": 0,
            "total_loading_state_duration": 0,
            "total_deploy_duration": 0,
            "total_update_duration": 0,
            "total_saving_state_duration": 0
        }

    results[assembly_name]["total_uptime_duration"] += loaded_results["sleep_time"] - loaded_results["up_time"]
    results[assembly_name]["total_loading_state_duration"] += loaded_results["end_loading_state"] - loaded_results["start_loading_state"]
    if "end_saving_state" in loaded_results.keys() and "start_saving_state" in loaded_results.keys():
        results[assembly_name]["total_saving_state_duration"] += loaded_results["end_saving_state"] - loaded_results["start_saving_state"]
    if "start_deploy" in loaded_results.keys() and "end_deploy" in loaded_results.keys():
        results[assembly_name]["total_deploy_duration"] += loaded_results["end_deploy"] - loaded_results["start_deploy"]
    if "start_update" in loaded_results.keys() and "end_update" in loaded_results.keys():
        results[assembly_name]["total_update_duration"] += loaded_results["end_update"] - loaded_results["start_update"]


def find_next_uptime(uptimes_nodes):
    min_uptime = (0, (math.inf, math.inf))
    for node_num, uptimes_values in enumerate(uptimes_nodes):
        for uptime in uptimes_values:
            if uptime[0] < min_uptime[1][0]:
                min_uptime = (node_num, uptime)

    return min_uptime


def schedule_and_run_uptimes_from_config(roles, uptimes_nodes_tuples: List, reconfig_config_file_path, experiment_num):
    """
    TODO: Faire une liste ordonnée globale pour tous les assemblies, puis attendre (enlever les calculs
    qui prennent un peu de temps)
    TODO: à changer ? loader un json via yaml.load
    """
    print("SCHEDULING START")
    expe_time_start = time.time()
    uptimes_nodes = [list(uptimes) for uptimes in uptimes_nodes_tuples]
    all_threads = []
    print("UPTIMES TO TREAT")
    for node_num, uptimes in enumerate(uptimes_nodes):
        print(f"node_num: {node_num}, uptimes: {uptimes}")
    finished_nodes.clear()
    while any(len(uptimes) > 0 for uptimes in uptimes_nodes):
        # Find the next reconf to launch (closest in time)
        node_num, next_uptime = find_next_uptime(uptimes_nodes)
        if node_num in finished_nodes:
            print(f"{node_num} finished its reconfiguration, clearing all subsequent uptimes")
            uptimes_nodes[node_num].clear()
        elif next_uptime[0] <= time.time() - expe_time_start:
            # Init the thread that will handle the reconf
            duration = next_uptime[1]
            dep_num = None if node_num == 0 else node_num - 1
            name = "server" if node_num == 0 else f"dep{node_num - 1}"
            thread = Thread(target=execute_reconf_in_g5k, args=(roles, name, reconfig_config_file_path, duration, dep_num, node_num, experiment_num))

            # Start reconf and remove it from uptimes
            thread.start()
            all_threads.append(thread)
            uptimes_nodes[node_num].remove(next_uptime)
        else:
            # Wait until its time to launch the reconf
            n = (expe_time_start + next_uptime[0]) - time.time()
            print(f"sleeping {n} seconds")
            time.sleep(n)

    # Wait for non finished threads
    for th in all_threads:
        th.join()

    print("ALL UPTIMES HAVE BEEN PROCESSED")


def compute_end_reconfiguration_time(uptimes_nodes):
    max_uptime_value = 0
    for uptimes_node in uptimes_nodes:
        for uptime in uptimes_node:
            if uptime[0] + uptime[1] > max_uptime_value:
                max_uptime_value = uptime[0] + uptime[1]

    return max_uptime_value


def launch_experiment(uptimes_params_nodes, transitions_times, cluster, experiment_num):
    # Provision infrastructure
    print("------ Provisionning infrastructure --------")
    params, uptimes_nodes = uptimes_params_nodes
    print(params)
    # TODO: Need to do the reservation previsouly but still to precise roles and stuff, to change
    roles, networks = concerto_d_g5k.reserve_nodes_for_concerto_d(nb_concerto_d_nodes=len(uptimes_nodes), nb_zenoh_routers=1, cluster=cluster)
    print(roles, networks)

    # Create transitions time file
    # TODO: Mettre synchrone/asynchrone/Muse
    # TODO: Mettre les deux expériences (cf présentation) (donc ce qui est mesuré dans les deux expériences)
    # TODO: générer les fichiers en amont et uniquement passer leurs chemin au ParamSweeper
    hash_file, reconf_config_file = generate_transitions_time_file(transitions_times, uptimes_nodes)

    # Reinitialize finished configuration states
    reinitialize_finished_config_state(uptimes_nodes)

    # Deploy zenoh routers
    print("------- Deploy zenoh routers -------")
    max_uptime_value = compute_end_reconfiguration_time(uptimes_nodes)
    concerto_d_g5k.install_zenoh_router(roles["zenoh_routers"])
    concerto_d_g5k.execute_zenoh_routers(roles["zenoh_routers"], max_uptime_value)

    # Reset results logs
    for assembly_name in results.keys():
        results[assembly_name] = {
            "total_uptime_duration": 0,
            "total_loading_state_duration": 0,
            "total_deploy_duration": 0,
            "total_update_duration": 0,
            "total_saving_state_duration": 0
        }

    # Run experiment
    print("------- Run experiment ----------")
    nodes_names = ["server"] + [f"dep{i}" for i in range(len(uptimes_nodes) - 1)]
    for name in nodes_names:
        sleeping_times_nodes[name] = {
            "total_sleeping_time": 0,
            "current_down_time": time.time(),
        }

    schedule_and_run_uptimes_from_config(roles, uptimes_nodes, reconf_config_file, experiment_num)

    for name in nodes_names:
        results[name]["total_sleeping_time"] = sleeping_times_nodes[name]["total_sleeping_time"]

    # Save results
    save_results(cluster, hash_file, params, reconf_config_file, uptimes_nodes, experiment_num)

    print("------ End of experiment ---------")


def save_results(cluster, hash_file, params, reconf_config_file, uptimes_nodes, expe_num):
    # Dans le nom: timestamp
    reconfig_config_file_path = "_".join(map(str, params))
    reconfig_config_file_path += f"_{hash_file}_"
    reconfig_config_file_path += cluster
    reconfig_config_file_path += f"_expe_{expe_num}"
    full_path = f"evaluation/experiment/results_experiment/results_{reconfig_config_file_path}"
    print(f"Saving results in {full_path}")
    with open(full_path, "w") as f:
        json.dump(results, f, indent=4)
    # Save config expe + results
    datetime_now_formatted = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dir_to_save_path = f"/home/anomond/all_expe_results/{reconfig_config_file_path}_{datetime_now_formatted}"
    os.makedirs(dir_to_save_path)
    # Save uptimes
    with open(f"{dir_to_save_path}/uptimes.json", "w") as f:
        json.dump({
            "params": params,
            "uptimes": uptimes_nodes
        }, f)
    # Save transitions time
    shutil.copy(reconf_config_file, f"{dir_to_save_path}/transitions_times.json")
    # Save experience results
    shutil.copy(full_path, f"{dir_to_save_path}/results_{reconfig_config_file_path}.json")
    # Save file with finished reconfigurations
    shutil.copytree("concerto/finished_reconfigurations", f"{dir_to_save_path}/finished_reconfigurations")


def reinitialize_finished_config_state(uptimes_nodes):
    print("------- Removing previous finished_configurations files -------")
    path_server = f"concerto/finished_reconfigurations/server_assembly"
    if exists(path_server):
        print(f"Removing {path_server}")
        os.remove(path_server)
    for i in range(len(uptimes_nodes) - 1):
        path_dep = f"concerto/finished_reconfigurations/dep_assembly_{i}"
        if exists(path_dep):
            print(f"Removing {path_dep}")
            os.remove(path_dep)


def generate_transitions_time_file(transitions_times, uptimes_nodes):
    print("------ Creating configuration file for reconfiguration programs --------")
    transitions_to_dump = {"server": dict(transitions_times[0])}
    for dep_num in range(1, len(uptimes_nodes)):
        transitions_to_dump[f"dep{dep_num - 1}"] = dict(transitions_times[dep_num])
    hash_file = str(abs(hash(transitions_times)))[:4]
    reconf_config_file = f"evaluation/experiment/generated_transitions_time/configuration_{hash_file}.json"
    with open(reconf_config_file, "w") as f:
        json.dump({"nb_deps_tot": len(uptimes_nodes) - 1, "transitions_time": transitions_to_dump}, f, indent=4)
    print(f"Config file saved in {reconf_config_file}")
    return hash_file, reconf_config_file


def get_uptimes_to_test():
    """
    Remplir manuellement le chemin du fichier avec les uptimes, et les taux retournés
    """
    with open(f"evaluation/experiment/generated_covering_taux/2022-06-26_14-50-58/uptimes.json") as f:
        loaded_uptimes = json.load(f)

    for params, values in loaded_uptimes.items():
        for perc, uptimes_nodes in values.items():
            li = []
            for uptimes_node in uptimes_nodes:
                li += tuple(tuple(uptime) for uptime in uptimes_node),
            values[perc] = tuple(li)

    return [
        ((30, 30, 12, (0.02, 0.05)), loaded_uptimes[str((30, 30, 12))][str((0.02, 0.05))]),
        ((30, 30, 12, (0.20, 0.30)), loaded_uptimes[str((30, 30, 12))][str((0.20, 0.30))]),
        ((30, 30, 12, (0.50, 0.60)), loaded_uptimes[str((30, 30, 12))][str((0.50, 0.60))]),
        ((30, 60, 12, (0.02, 0.05)), loaded_uptimes[str((30, 60, 12))][str((0.02, 0.05))]),
        ((30, 60, 12, (0.20, 0.30)), loaded_uptimes[str((30, 60, 12))][str((0.20, 0.30))]),
        ((30, 60, 12, (0.50, 0.60)), loaded_uptimes[str((30, 60, 12))][str((0.50, 0.60))]),
    ]


def create_and_run_sweeper():
    # Generate transitions
    nb_generations = 4
    max_deps = 20
    transitions_times_list = generate_transitions_time.generate_transitions_times(max_deps, nb_generations)

    clusters_list = ["uvb"]
    uptimes_to_test = get_uptimes_to_test()

    sweeps = sweep({
        "uptimes": uptimes_to_test,
        "transitions_times": transitions_times_list,
        "cluster": clusters_list,
        "experiment_num": [1, 2]
    })

    sweeper = ParamSweeper(
        persistence_dir=str(Path("evaluation/experiment/sweeps").resolve()), sweeps=sweeps, save_sweeps=True
    )
    parameter = sweeper.get_next()
    while parameter:
        try:
            print("----- Launching experiment ---------")
            launch_experiment(parameter["uptimes"], parameter["transitions_times"], parameter["cluster"], parameter["experiment_num"])
            sweeper.done(parameter)
        except Exception as e:
            sweeper.skip(parameter)
            print("Experiment FAILED")
            traceback.print_exc()
        finally:
            parameter = sweeper.get_next()


if __name__ == '__main__':
    create_and_run_sweeper()
