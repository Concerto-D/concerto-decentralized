import random
from itertools import product
from typing import List, Dict, Tuple


def generate_uptimes_for_dependencies(
        freqs_awake_list: List[int],
        time_awakening: List[int],
        nb_deps_list: List[int],
) -> Dict:
    """
    returns: Dict de la forme:
    {(nb_de_reveils, temps_awoken, nb_deps): {dep_num: [temps_reveils]}}
    """
    uptimes_by_params = {}
    # Compute each possible combination between parameters
    for freq, time, nb_deps in product(freqs_awake_list, time_awakening, nb_deps_list):

        covering_perc_values = {0.1: None, 0.2: None, 0.4: None, 0.6: None, 1: None}
        while not all(uptimes is not None for uptimes in covering_perc_values.values()):
            # On écarte de plus en plus la plage sur laquelle choisir les uptimes
            for step in range(time, time+600, 20):
                uptimes_list = compute_uptimes_for_params(freq, nb_deps, step, time)
                covering_uptimes = []
                for dep_num, dep_times in enumerate(uptimes_list):
                    cov_perc_list = compute_covering_time_dep(dep_num, freq, time, uptimes_list)
                    covering_uptimes.append(round(sum(cov_perc_list)/len(cov_perc_list), 2))
                global_means_coverage = round(sum(covering_uptimes) / len(covering_uptimes), 2)
                for cover_val in covering_perc_values.keys():
                    if covering_perc_values[cover_val] is None and cover_val - cover_val*0.1 <= global_means_coverage <= cover_val + cover_val*0.1:
                        covering_perc_values[cover_val] = uptimes_list

        uptimes_by_params[(freq, time, nb_deps)] = covering_perc_values

    return uptimes_by_params


def compute_uptimes_for_params(freq, nb_deps, step_uptime, time):
    uptimes_list = [[] for _ in range(nb_deps + 1)]
    offset = 10
    for up_num in range(freq):
        for dep_num in range(nb_deps + 1):  # Add 1 to the nb_deps to add the server
            time_to_awake = random.uniform(step_uptime * up_num + offset * up_num, step_uptime * (up_num + 1) - time + offset * up_num)
            uptimes_list[dep_num].append((time_to_awake, time))
    return tuple(tuple(uptimes) for uptimes in uptimes_list)


def compute_covering_time_dep(dep_num: int, freq: int, time_awoken: float, all_dep_uptimes):
    uptimes_dep = all_dep_uptimes[dep_num]
    all_other_uptimes = [all_dep_uptimes[i] for i in range(len(all_dep_uptimes)) if dep_num != i]
    overlaps_list = []
    for other_uptimes_dep in all_other_uptimes:
        covering_time = 0
        for uptime_dep in uptimes_dep:
            for other_uptime_dep in other_uptimes_dep:
                overlap = min(uptime_dep[0] + time_awoken, other_uptime_dep[0] + time_awoken) - max(uptime_dep[0], other_uptime_dep[0])
                covering_time += overlap if overlap > 0 else 0

        percentage_overlap = covering_time/(time_awoken*freq)
        overlaps_list.append(percentage_overlap)

    return overlaps_list


def generate_server_transitions_time(nb_deps: int, min_value: float = 0., max_value: float = 10.) -> Tuple:
    server_t_sa = round(random.uniform(min_value, max_value), 2)
    server_t_sc = tuple(round(random.uniform(min_value, max_value), 2) for i in range(nb_deps))
    server_t_sr = round(random.uniform(min_value, max_value), 2)
    server_t_ss = tuple(round(random.uniform(min_value, max_value), 2) for i in range(nb_deps))
    server_t_sp = tuple(round(random.uniform(min_value, max_value), 2) for i in range(nb_deps))
    return tuple({
        "t_sa": server_t_sa,
        "t_sc": server_t_sc,
        "t_sr": server_t_sr,
        "t_ss": server_t_ss,
        "t_sp": server_t_sp,
    }.items())


def generate_deps_transitions_time(dep_num: int, min_value: float = 0., max_value: float = 10.) -> Tuple:
    deps_t_di = round(random.uniform(min_value, max_value), 2)
    deps_t_dr = round(random.uniform(min_value, max_value), 2)
    deps_t_du = round(random.uniform(min_value, max_value), 2)
    return tuple({
        "id": dep_num,
        "t_di": deps_t_di,
        "t_dr": deps_t_dr,
        "t_du": deps_t_du,
    }.items())


def generate_transitions_times(nb_deps_exp: int, nb_generations: int):
    all_generations_transitions_times = []
    for _ in range(nb_generations):
        generations_tt = [generate_server_transitions_time(nb_deps_exp)]
        for dep_num in range(nb_deps_exp):
            generations_tt.append(generate_deps_transitions_time(dep_num))
        all_generations_transitions_times.append(tuple(generations_tt))
    return all_generations_transitions_times


def generate_taux():
    freqs_awake_list = [4, 8]      # Valeurs fixées
    time_awakening = [20, 40]      # Valeurs fixées
    nb_deps_list = [2, 5, 10, 20]  # Valeurs fixées
    clusters_list = ["econome"]    # Nantes
    print("---------- Wake up times by parameters -------------------")
    uptimes_by_params = generate_uptimes_for_dependencies(freqs_awake_list, time_awakening, nb_deps_list)
    print("done")

    # print("--------- Uptime to test -----------------")
    uptimes_to_test = [((8, 20, 2, 0.6), uptimes_by_params[(8, 20, 2)][0.6]), ((8, 40, 2, 0.6), uptimes_by_params[(8, 40, 2)][0.6])]
    # print(*config_to_test, sep="\n")
    # print()

    nb_generations = 4
    # print(f"---------- Generate {nb_generations} transitions times ----------")
    transitions_times_list = generate_transitions_times(max(nb_deps_list), nb_generations)
    # print(*transitions_times_list, sep="\n")

    # print("f---------- Where to launch expe -----------")

    return uptimes_to_test, transitions_times_list, clusters_list


if __name__ == '__main__':
    c,t, cl = generate_taux()
    print(c)

