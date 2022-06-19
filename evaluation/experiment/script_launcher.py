import json
import math
import os
import sys
import time
import traceback
from os.path import exists
from pathlib import Path
from threading import Thread
from typing import Dict, List

import yaml
from execo_engine import sweep, ParamSweeper

from evaluation.experiment import concerto_d_g5k, generate_taux_recouvrements, assembly_parameters
from evaluation.experiment.concerto_d_g5k import provider


finished_nodes = []

# Suivre le même principe pour le temps passé à dormir et à se réveillé
# Mesurer le temps requis pour sauvegarder l'état
reconfiguration_times = {
    "server": 0,
    "dep0": 0,
    "dep1": 0
}

# TODO: logger ce qu'on veut mesurer directement dans l'appli, puis récupérer les résultats
# A sauvegarder:
    # Réveil
    # Début chargement de l'état
    # Fin chargement de l'état
    # Début reconf
    # Fin de la reconf en cours
    # Début sauvegarde
    # Fin sauvegarde
    # Endormissement
# Puis calculs locaux sur ma machine
# Pour la sauvegarde:
    # Enregistrer sur le /tmp des noeuds, puis les récupérer avant de détruire la réservation (à voir)
    # Timestamp pour faire la distinction entre les expés + numéro des OUs


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

    print("ALL UPTIMES HAVE BEEN PROCESSED")


def compute_end_reconfiguration_time(uptimes_nodes):
    max_uptime_value = 0
    for uptimes_node in uptimes_nodes:
        for uptime in uptimes_node:
            if uptime[0] + uptime[1] > max_uptime_value:
                max_uptime_value = uptime[0] + uptime[1]

    return max_uptime_value


def launch_experiment(uptimes_params_nodes, transitions_times, cluster):
    # Provision infrastructure
    print("------ Provisionning infrastructure --------")
    params, uptimes_nodes = uptimes_params_nodes
    print(params, uptimes_nodes)
    roles, networks = concerto_d_g5k.reserve_nodes_for_concerto_d(nb_concerto_d_nodes=len(uptimes_nodes), nb_zenoh_routers=1, cluster=cluster)
    print(roles, networks)

    # Create configuration file
    print("------ Creating configuration file for reconfiguration programs --------")
    transitions_to_dump = {"server": dict(transitions_times[0])}
    for dep_num in range(1, len(uptimes_nodes)):
        transitions_to_dump[f"dep{dep_num-1}"] = dict(transitions_times[dep_num])

    hash_file = str(abs(hash(transitions_times)))[:4]
    reconf_config_file = f"configuration_{hash_file}.json"
    path_file = str(Path(reconf_config_file).resolve())
    with open(path_file, "w") as f:
        json.dump({"nb_deps_tot": len(uptimes_nodes) - 1, "transitions_time": transitions_to_dump}, f, indent=4)
    print(f"Config file saved in {path_file}")

    # Deploy concerto_d nodes
    print("------- Deploy concerto_d nodes ------")
    concerto_d_g5k.install_apt_deps(roles["concerto_d"])
    concerto_d_g5k.deploy_concerto_d(roles["server"], reconf_config_file)

    print("------- Removing previous finished_configurations files -------")
    # TODO: to refacto
    path_dep_0 = str(Path(f"finished_reconfigurations/dep_assembly_0").resolve())
    path_dep_1 = str(Path(f"finished_reconfigurations/dep_assembly_1").resolve())
    path_server = str(Path(f"finished_reconfigurations/server_assembly").resolve())
    if exists(path_dep_0):
        print(f"Removing {path_dep_0}")
        os.remove(path_dep_0)
    if exists(path_dep_1):
        print(f"Removing {path_dep_1}")
        os.remove(path_dep_1)
    if exists(path_server):
        print(f"Removing {path_server}")
        os.remove(path_server)

    # Deploy zenoh routers
    print("------- Deploy zenoh routers -------")
    max_uptime_value = compute_end_reconfiguration_time(uptimes_nodes)
    concerto_d_g5k.deploy_zenoh_routers(roles["zenoh_routers"])
    concerto_d_g5k.execute_zenoh_routers(roles["zenoh_routers"], max_uptime_value)

    # Run experiment
    print("------- Run experiment ----------")
    schedule_and_run_uptimes_from_config(roles, uptimes_nodes, reconf_config_file)

    # Save results
    # Dans le nom: timestamp
    reconfig_config_file_path = "reconfiguration_times_"
    reconfig_config_file_path += "_".join(map(str, params))
    reconfig_config_file_path += f"_{hash_file}_"
    reconfig_config_file_path += cluster

    print(f"Saving results in {reconfig_config_file_path}")
    with open(reconfig_config_file_path, "w") as f:
        json.dump(reconfiguration_times, f, indent=4)

    print("------ End of experiment ---------")
    # Get logs
    # concerto_d_g5k.get_logs_from_concerto_d_node(roles["server"], ["server", *[f"dep{i}" for i in range(nb_deps_tot)]])


def get_uptimes_to_test():
    # Fonction à remplir manuellement
    return [{
        (4, 20, 2): {0.1: (((25.195508847767325, 20), (163.41746947738693, 20), (281.6755192989782, 20), (371.8995510611459, 20)), ((64.74845465532238, 20), (147.2203654964685, 20), (265.8913222945456, 20), (359.9003031908631, 20)), ((75.5248356709052, 20), (110.38250838979351, 20), (227.25382536115265, 20), (336.7081900036671, 20))), 0.2: (((45.05244289773501, 20), (293.0319321004896, 20), (384.51929586803834, 20), (627.4006813648807, 20)), ((90.05618397146786, 20), (297.57791370535176, 20), (465.0435149454596, 20), (573.4871624556267, 20)), ((78.31490599244175, 20), (196.3528189492837, 20), (384.8190800572006, 20), (638.3959349210597, 20))), 0.4: (((28.15693067757011, 20), (108.04211234926512, 20), (172.32010193843712, 20), (245.83563728411406, 20)), ((0.27315015181298197, 20), (89.25035170996583, 20), (177.42769770689023, 20), (245.22155274570838, 20)), ((33.575992902361165, 20), (84.66136967070449, 20), (145.90457587979586, 20), (249.46867269034328, 20))), 0.6: (((6.793465155408676, 20), (61.43187825009504, 20), (100.81675296230114, 20), (150.45265288903047, 20)), ((15.147687939068383, 20), (50.152802336443976, 20), (108.91606619243265, 20), (154.76497466653035, 20)), ((14.864090261108526, 20), (59.742918321138355, 20), (108.84521451367577, 20), (164.806344555012, 20)))},

    }]


def create_and_run_sweeper():
    # Generate transitions
    nb_generations = 4
    max_deps = 20
    transitions_times_list = assembly_parameters.generate_transitions_times(max_deps, nb_generations)

    clusters_list = ["econome"]  # Nantes
    uptimes_to_test = get_uptimes_to_test()

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
            print("----- Launching experiment with parameters ---------")
            print(parameter)
            print("----------------------------------------------------")
            launch_experiment(parameter["uptimes"], parameter["transitions_times"], parameter["cluster"])
            sweeper.done(parameter)
        except Exception as e:
            sweeper.skip(parameter)
            print("Experiment FAILED")
            traceback.print_exc()
        finally:
            parameter = sweeper.get_next()


if __name__ == '__main__':
    create_and_run_sweeper()
