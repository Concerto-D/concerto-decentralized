import sys
import time
from threading import Thread
from typing import Dict

import yaml

from evaluation.experiment import concerto_d_g5k
from evaluation.synthetic_use_case.reconf_programs import reconf_server, reconf_dep

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


def execute_server_reconf_in_thread(expe_time_start, reconf_config, duration, is_asynchrone):
    print("server reconf starting at : ", time.time() - expe_time_start)
    time_start = time.time()
    reconf_server.execute_reconf(reconf_config, duration, is_asynchrone)
    tracking_thread['server']['total_running_time'] += time.time() - time_start


def execute_dep_reconf_in_thread(expe_time_start, dep_num, reconf_config, duration, is_asynchrone):
    print(f"dep{dep_num} reconf starting at : ", time.time() - expe_time_start)
    time_start = time.time()
    reconf_dep.execute_reconf(dep_num, reconf_config, duration, is_asynchrone)
    tracking_thread[f"dep{dep_num}"]['total_running_time'] += time.time() - time_start


def execute_reconf_in_g5k(roles, assembly_name, expe_time_start, reconf_config_file_path, duration, dep_num):
    print(f"{assembly_name} reconf starting at : ", time.time() - expe_time_start)
    time_start = time.time()
    concerto_d_g5k.execute_reconf(roles, reconf_config_file_path, assembly_name, duration, dep_num)
    tracking_thread[assembly_name]['total_running_time'] += time.time() - time_start


def schedule_and_run_uptimes_from_config(roles, reconf_config: Dict, reconfig_config_file_path):
    def search_min_uptime(uptime_assembly):
        return min(uptime_assembly.values(), key=lambda x: x[0][0])

    uptimes = reconf_config['uptimes']
    expe_time_start = time.time()
    while sum(len(uptimes[name]) for name in uptimes.keys()) > 0:
        print({key: values} for key, values in uptimes.items() if len(values) > 0)
        name, values = min(({key: values} for key, values in uptimes.items() if len(values) > 0), key=search_min_uptime)
        print(f"let's go {name}")
        next_uptime = values[0]
        if next_uptime[0] < time.time() - expe_time_start:
            duration = next_uptime[1]
            # if name == "server":
            #     thread = Thread(target=execute_server_reconf_in_thread, args=(expe_time_start, reconf_config, duration, False))
            # else:
            #     dep_num = int(name.replace("dep",""))
            #     thread = Thread(target=execute_dep_reconf_in_thread, args=(expe_time_start, dep_num, reconf_config, duration, False))
            dep_num = None if name == "server" else int(name.replace("dep",""))
            thread = Thread(target=execute_reconf_in_g5k, args=(roles, name, expe_time_start, reconfig_config_file_path, duration, dep_num))
            thread.start()
            uptimes[name].remove(next_uptime)
        else:
            n = (expe_time_start + next_uptime[0]) - time.time()
            print(f"sleeping {n} seconds")
            time.sleep(n)


if __name__ == '__main__':
    reconf_config_file_path = sys.argv[1]
    with open(reconf_config_file_path, "r") as f:
        reconf_config = yaml.safe_load(f)

    # nb_deps_tot = reconf_config["nb_deps_tot"]
    nb_deps_tot = 2
    roles, networks = concerto_d_g5k.reserve_nodes_for_concerto_d(nb_deps_tot=nb_deps_tot, nb_zenoh_routers=0)
    print(roles, networks)
    # concerto_d_g5k.deploy_concerto_d(roles["concerto_d"], reconf_config_file_path)
    # concerto_d_g5k.deploy_zenoh_routers(roles["zenoh_routers"])
    # concerto_d_g5k.execute_zenoh_routers(roles["zenoh_routers"])
    # concerto_d_g5k.deploy_concerto_d(roles["concerto_d"], reconf_config_file_path)
    # schedule_and_run_uptimes_from_config(roles, reconf_config, reconf_config_file_path)
    concerto_d_g5k.execute_reconf(roles["server"], reconf_config_file_path, 20, None)
    concerto_d_g5k.execute_reconf(roles["dep0"], reconf_config_file_path, 20, 0)
    concerto_d_g5k.execute_reconf(roles["dep1"], reconf_config_file_path, 20, 1)
