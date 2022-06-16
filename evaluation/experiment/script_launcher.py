import json
import math
import os
import sys
import time
from os.path import exists
from pathlib import Path
from threading import Thread
from typing import Dict, List

import yaml
from execo_engine import sweep, ParamSweeper

from evaluation.experiment import concerto_d_g5k, generate_taux_recouvrements
from evaluation.experiment.concerto_d_g5k import provider


finished_nodes = []
reconfiguration_times = {
    "server": 0,
    "dep0": 0,
    "dep1": 0
}


def execute_reconf_in_g5k(roles, assembly_name, reconf_config_file_path, duration, dep_num, node_num, expe_time_start):
    time_start = time.time()
    concerto_d_g5k.execute_reconf(roles[assembly_name], reconf_config_file_path, duration, dep_num)
    reconfiguration_times[assembly_name] += time.time() - time_start
    concerto_d_g5k.fetch_finished_reconfiguration_file(roles[assembly_name], assembly_name, dep_num)
    if exists(str(Path(concerto_d_g5k.build_finished_reconfiguration_path(assembly_name, dep_num)).resolve())):
        print("reconf finished")
        finished_nodes.append(node_num)


def find_next_uptime(uptimes_nodes):
    min_uptime = (0, (math.inf, math.inf))
    for node_num, uptimes_values in enumerate(uptimes_nodes):
        for uptime in uptimes_values:
            if uptime[0] < min_uptime[1][0]:
                min_uptime = (node_num, uptime)

    return min_uptime


def schedule_and_run_uptimes_from_config(roles, uptimes_nodes_tuples: List, reconfig_config_file_path):
    """
    TODO: Faire une liste ordonnée globale pour tous les assemblies, puis attendre (enlever les calculs
    qui prennent un peu de temps)
    """
    expe_time_start = time.time()
    uptimes_nodes = [list(uptimes) for uptimes in uptimes_nodes_tuples]
    all_threads = []
    while any(len(uptimes) > 0 for uptimes in uptimes_nodes):
        # Find the next reconf to launch (closest in time)
        node_num, next_uptime = find_next_uptime(uptimes_nodes)
        if node_num in finished_nodes:
            uptimes_nodes[node_num].clear()
        elif next_uptime[0] <= time.time() - expe_time_start:
            # Init the thread that will handle the reconf
            duration = next_uptime[1]
            dep_num = None if node_num == 0 else node_num - 1
            name = "server" if node_num == 0 else f"dep{node_num - 1}"
            thread = Thread(target=execute_reconf_in_g5k, args=(roles, name, reconfig_config_file_path, duration, dep_num, node_num, expe_time_start))

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


def compute_end_reconfiguration_time(uptimes_nodes):
    max_uptime_value = 0
    for uptimes_node in uptimes_nodes:
        for uptime in uptimes_node:
            if uptime[0] + uptime[1] > max_uptime_value:
                max_uptime_value = uptime[0] + uptime[1]

    return max_uptime_value


def launch_experiment(uptimes_params_nodes, transitions_times, cluster):
    # Provision infrastructure
    params, uptimes_nodes = uptimes_params_nodes
    print(params, uptimes_nodes)
    roles, networks = concerto_d_g5k.reserve_nodes_for_concerto_d(nb_concerto_d_nodes=len(uptimes_nodes), nb_zenoh_routers=1, cluster=cluster)
    print(roles, networks)

    # Create configuration file
    transitions_to_dump = {"server": dict(transitions_times[0])}
    for dep_num in range(1, len(uptimes_nodes)):
        transitions_to_dump[f"dep{dep_num-1}"] = dict(transitions_times[dep_num])

    hash_file = str(abs(hash(transitions_times)))[:4]
    reconf_config_file = f"configuration_{hash_file}.json"
    with open(str(Path(reconf_config_file).resolve()), "w") as f:
        json.dump({"nb_deps_tot": len(uptimes_nodes) - 1, "transitions_time": transitions_to_dump}, f, indent=4)

    # Deploy concerto_d nodes
    concerto_d_g5k.install_apt_deps(roles["concerto_d"])
    concerto_d_g5k.deploy_concerto_d(roles["server"], reconf_config_file)
    # TODO: to refacto
    os.remove(f"finished_reconfiguration/dep_assembly_0")
    os.remove(f"finished_reconfiguration/dep_assembly_1")
    os.remove(f"finished_reconfiguration/server_assembly")

    # Deploy zenoh routers
    max_uptime_value = compute_end_reconfiguration_time(uptimes_nodes)
    concerto_d_g5k.deploy_zenoh_routers(roles["zenoh_routers"])
    concerto_d_g5k.execute_zenoh_routers(roles["zenoh_routers"], max_uptime_value)

    # Run experiment
    schedule_and_run_uptimes_from_config(roles, uptimes_nodes, reconf_config_file)

    # Save results
    reconfig_config_file_path = "reconfiguration_times_"
    reconfig_config_file_path += "_".join(map(str, params))
    reconfig_config_file_path += f"_{hash_file}_"
    reconfig_config_file_path += cluster

    with open(reconfig_config_file_path, "w") as f:
        json.dump(reconfiguration_times, f, indent=4)

    # Get logs
    # concerto_d_g5k.get_logs_from_concerto_d_node(roles["server"], ["server", *[f"dep{i}" for i in range(nb_deps_tot)]])


def compute_sweeper():
    uptimes_to_test, transitions_times_list, clusters_list = generate_taux_recouvrements.generate_taux()
    sweeps = sweep({
        "uptimes": uptimes_to_test,
        "transitions_times": transitions_times_list,
        "cluster": clusters_list
    })

    sweeper = ParamSweeper(
        persistence_dir=str(Path("sweeps").resolve()), sweeps=sweeps, save_sweeps=True
    )
    parameter = sweeper.get_next()
    while parameter:
        try:
            launch_experiment(parameter["uptimes"], parameter["transitions_times"], parameter["cluster"])
            sweeper.done(parameter)
        except Exception as e:
            sweeper.skip(parameter)
            print(e)
        finally:
            parameter = sweeper.get_next()


if __name__ == '__main__':
    compute_sweeper()
    # main()