import math
import sys
import time
from threading import Thread
from typing import Dict

import yaml

from evaluation.experiment import concerto_d_g5k

tracking_thread = {
    "server": {
        "total_running_time": 0,
        "total_sleeping_time": 0
    },
    "dep0": {
        "total_running_time": 0,
        "total_sleeping_time": 0
    },
    "dep1": {
        "total_running_time": 0,
        "total_sleeping_time": 0
    },
}


def execute_reconf_in_g5k(roles, assembly_name, expe_time_start, reconf_config_file_path, duration, dep_num):
    print(f"{assembly_name} reconf starting at : ", time.time() - expe_time_start)
    time_start = time.time()
    concerto_d_g5k.execute_reconf(roles[assembly_name], reconf_config_file_path, duration, dep_num)
    tracking_thread[assembly_name]['total_running_time'] += time.time() - time_start


def find_next_uptime(uptimes_dict):
    min_uptime = ("", [math.inf, math.inf])
    for name, values in uptimes_dict:
        for v in values:
            if v[0] < min_uptime[1][0]:
                min_uptime = (name, v)

    return min_uptime


def schedule_and_run_uptimes_from_config(roles, reconf_config: Dict, reconfig_config_file_path):
    """
    TODO: Faire une liste ordonnée globale pour tous les assemblies, puis attendre (enlever les calculs
    qui prennent un peu de temps)
    """
    uptimes = reconf_config['uptimes']
    expe_time_start = time.time()
    while sum(len(uptimes[name]) for name in uptimes.keys()) > 0:
        # Find the next reconf to launch (closest in time)
        name, next_uptime = find_next_uptime(uptimes.items())
        print("MINIMAL UPTIME: ", name, next_uptime)
        if next_uptime[0] <= time.time() - expe_time_start:
            # Init the thread that will handle the reconf
            duration = next_uptime[1]
            dep_num = None if name == "server" else int(name.replace("dep",""))
            thread = Thread(target=execute_reconf_in_g5k, args=(roles, name, expe_time_start, reconfig_config_file_path, duration, dep_num))

            # Start reconf and remove it from uptimes
            thread.start()
            # thread.join()
            # l += thread,
            uptimes[name].remove(next_uptime)
        else:
            # Wait until its time to launch the reconf
            n = (expe_time_start + next_uptime[0]) - time.time()
            print(f"sleeping {n} seconds")
            time.sleep(n)

    # for t in l:
    #     t.join()


def compute_end_reconfiguration_time(uptimes):
    max_uptime_value = 0
    for uptimes_list in uptimes.values():
        for value in uptimes_list:
            if value[0] + value[1] > max_uptime_value:
                max_uptime_value = value[0] + value[1]

    return max_uptime_value


if __name__ == '__main__':
    reconf_config_file_path = sys.argv[1]
    with open(reconf_config_file_path, "r") as f:
        reconf_config = yaml.safe_load(f)

    # Reserve G5K nodes for concerto_d and zenoh
    nb_deps_tot = reconf_config["nb_deps_tot"]
    nb_zenoh_routers = reconf_config["nb_zenoh_routers"]
    roles, networks = concerto_d_g5k.reserve_nodes_for_concerto_d(nb_deps_tot=nb_deps_tot, nb_zenoh_routers=nb_zenoh_routers)
    print(roles, networks)

    # Deploy concerto_d nodes
    # concerto_d_g5k.install_apt_deps(roles["concerto_d"])
    # concerto_d_g5k.deploy_concerto_d(roles["server"], reconf_config_file_path)

    # Deploy zenoh routers
    # max_uptime_value = compute_end_reconfiguration_time(reconf_config["uptimes"])
    # concerto_d_g5k.deploy_zenoh_routers(roles["zenoh_routers"])
    # concerto_d_g5k.execute_zenoh_routers(roles["zenoh_routers"], max_uptime_value)

    # Run experiment
    schedule_and_run_uptimes_from_config(roles, reconf_config, reconf_config_file_path)

    # Get logs
    # concerto_d_g5k.get_logs_from_concerto_d_node(roles["server"], ["server", *[f"dep{i}" for i in range(nb_deps_tot)]])

    # for i in range(7):
    #     thread1 = Thread(target=concerto_d_g5k.execute_reconf, args=(roles["server"], reconf_config_file_path, 20, None))
    #     thread1.start()
    #     time.sleep(uniform(1, 4))
    #     thread2 = Thread(target=concerto_d_g5k.execute_reconf, args=(roles["dep0"], reconf_config_file_path, 20, 0))
    #     thread2.start()
    #     time.sleep(uniform(1, 4))
    #     thread3 = Thread(target=concerto_d_g5k.execute_reconf, args=(roles["dep1"], reconf_config_file_path, 20, 1))
    #     thread3.start()
    #
    #     thread1.join()
    #     thread2.join()
    #     thread3.join()

        # concerto_d_g5k.execute_reconf(roles["server"], reconf_config_file_path, 20, None)
        # concerto_d_g5k.execute_reconf(roles["dep0"], reconf_config_file_path, 20, 0)
        # concerto_d_g5k.execute_reconf(roles["dep1"], reconf_config_file_path, 20, 1)
    print(tracking_thread)
    print("---- FINNNNN DE LEXPPEEE ------")