import random
import sys
from typing import Dict, List
from random import uniform
import jinja2


def generate_number_deps_tot(min_value: int = 0, max_value: int = 10) -> Dict:
    return {
        "nb_deps_tot": random.randint(min_value, max_value)
    }


def generate_server_transitions_time(nb_deps_tot: int, min_value: float = 0., max_value: float = 10.) -> Dict:
    server_t_sa = round(uniform(min_value, max_value), 2)
    server_t_sc = [round(uniform(min_value, max_value), 2) for i in range(nb_deps_tot)]
    server_t_sr = round(uniform(min_value, max_value), 2)
    server_t_ss = [round(uniform(min_value, max_value), 2) for i in range(nb_deps_tot)]
    server_t_sp = [round(uniform(min_value, max_value), 2) for i in range(nb_deps_tot)]
    return {
        "server_t_sa": server_t_sa,
        "server_t_sc": server_t_sc,
        "server_t_sr": server_t_sr,
        "server_t_ss": server_t_ss,
        "server_t_sp": server_t_sp,
    }


def generate_deps_transitions_time(nb_deps_tot: int, min_value: float = 0., max_value: float = 10.) -> Dict:
    deps_t_di = [round(uniform(min_value, max_value), 2) for i in range(nb_deps_tot)]
    deps_t_dr = [round(uniform(min_value, max_value), 2) for i in range(nb_deps_tot)]
    deps_t_du = [round(uniform(min_value, max_value), 2) for i in range(nb_deps_tot)]
    return {
        "deps_t_di": deps_t_di,
        "deps_t_dr": deps_t_dr,
        "deps_t_du": deps_t_du,
    }


def generate_node_uptimes(
        total_wake_up: int = 2,
        frequency: float = 100,
        variable_frequency: float = 70.,
        uptime_duration: float = 40.,
        variable_uptime: float = 20.):
    """
    TODO: à revoir au niveau des paramètres
    """
    next_time_to_wake_up = 0
    node_awake_times_list = []
    for i in range(total_wake_up):
        freq = frequency + uniform(-variable_frequency, variable_frequency)
        time_to_wake_up = round(next_time_to_wake_up + freq, 2)
        uptime = round(uptime_duration + uniform(-variable_uptime, variable_uptime), 2)
        node_awake_times_list.append((time_to_wake_up, uptime))
        next_time_to_wake_up += freq + uptime

    return node_awake_times_list


def generate_server_uptimes():
    return {
        "server_awake_times_list": generate_node_uptimes(total_wake_up=3, frequency=100, uptime_duration=40, variable_uptime=20, variable_frequency=70)
    }


def generate_deps_uptimes(nb_deps_tot):
    return {
        "deps_awake_times_lists": [generate_node_uptimes(total_wake_up=3, frequency=100, uptime_duration=40, variable_uptime=20, variable_frequency=70) for _ in range(nb_deps_tot)]
    }


def compute_recouvrement_between_nodes(uptimes_list: List[Dict]):
    # Get all possibles combinaisons for overlapping: [[(a1,b1), (a2,b2)], [(a3,b3), (a4,b4)], [(a5,b5), (a6,b6)]]
    #                                         become: [((a1,b1),(a3,b3)), ((a1,b1),(a4,b4)), ((a1,b1),(a5,b5)), ((a1,b1),(a6,b6)),
    #                                                 ((a2,b2),(a3,b3)), ((a2,b2),(a4,b4)), ((a2,b2),(a5,b5)), ((a2,b2),(a6,b6)),
    #                                                 ((a3,b3),(a5,b5)), ((a3,b3),(a6,b6)),
    #                                                 ((a4,b4),(a5,b5)), ((a4,b4),(a6,b6))]
    all_combinations = []
    for i in range(len(uptimes_list)):
        for j in range(i+1, len(uptimes_list)):
            for k in range(len(uptimes_list[i])):
                for l in range(len(uptimes_list[j])):
                    all_combinations.append((uptimes_list[i][k], uptimes_list[j][l]))

    # Compute total awakening time
    total_time = 0
    for node in uptimes_list:
        total_time += sum(uptime[1] for uptime in node)

    # Compute every overlap
    total_overlap = 0
    for node1, node2 in all_combinations:
        # Get the time (t) and duration (d) for node1 and node2
        t1, d1 = node1
        t2, d2 = node2

        overlap = min(t1+d1, t2+d2) - max(t1, t2)
        if overlap < 0:
            overlap = 0

        total_overlap += overlap

    print(uptimes_list)
    print(f"total time : {round(total_time, 2)}s")
    print(f"total overlap : {round(total_overlap, 2)}s")
    recouvrement = round(total_overlap*100/total_time, 2)
    print(f"recouvrement : {recouvrement}%")

    return recouvrement


def generate_reconf_configuration(file_suffix: str):
    # Generating random values for experience variables
    configuration = {}
    nb_deps_tot_dict = generate_number_deps_tot(min_value=2, max_value=2)
    nb_deps_tot = nb_deps_tot_dict["nb_deps_tot"]
    configuration.update(nb_deps_tot_dict)
    configuration.update(generate_server_transitions_time(nb_deps_tot))
    configuration.update(generate_deps_transitions_time(nb_deps_tot))
    configuration.update(generate_server_uptimes())
    configuration.update(generate_deps_uptimes(nb_deps_tot))

    # Computing means covering percentage for all uptimes
    uptimes_list = [configuration['server_awake_times_list']] + configuration['deps_awake_times_lists']
    recouvrement = compute_recouvrement_between_nodes(uptimes_list)

    # Generate configuration file
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader('evaluation/experiment/templates'))
    template = template_env.get_template("experiment_config.yaml.j2")
    rendered_template = template.render(**configuration)
    hash_file = str(abs(hash(rendered_template)))
    if file_suffix == "":
        file_suffix = hash_file
    path_file = f"evaluation/experiment/generated_configurations/experiment_config_{file_suffix}.yml"
    with open(path_file, "w") as f:
        f.write(rendered_template)

    return path_file


if __name__ == '__main__':
    file_suffix = sys.argv[1] if len(sys.argv) > 1 else ""
    file_name = generate_reconf_configuration(file_suffix)
    print(f"Config generated at {file_name}")
