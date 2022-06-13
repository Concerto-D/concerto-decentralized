from itertools import product
from random import uniform
from typing import List, Dict


def is_uptime_colliding_with_another(uptimes_list: List[float], time_to_awake: float, awakening_time: float):
    is_colliding = False
    for existing_time in uptimes_list:
        if min(existing_time + awakening_time, time_to_awake + awakening_time) - max(existing_time, time_to_awake) > 0:
            is_colliding = True

    return is_colliding


def generate_uptimes_for_dependencies(
        freqs_awake_list: List[int],
        time_awakening: List[int],
        nb_deps_list: List[int],
        step_freq: int,
        no_collisions: bool = True
) -> Dict:
    """
    returns: Dict de la forme:
    {(nb_de_reveils, temps_awoken, nb_deps): {dep_num: [temps_reveils]}}
    """
    uptimes_by_params = {}
    # Compute each possible combination between parameters
    for freq, time, nb_deps in product(freqs_awake_list, time_awakening, nb_deps_list):
        uptimes_dict = {}

        # For each dependency, pick randomly an uptime, freq times.
        for i in range(nb_deps):
            uptimes_dict[i] = []
            for _ in range(freq):
                time_to_awake = uniform(0, step_freq-time)

                # Ensure that there is no overlap in uptimes
                while no_collisions and is_uptime_colliding_with_another(uptimes_dict[i], time_to_awake, time):
                    time_to_awake = uniform(0, step_freq-time)

                uptimes_dict[i].append(time_to_awake)

        uptimes_by_params[(freq, time, nb_deps)] = uptimes_dict

    return uptimes_by_params


def compute_covering_time_dep(dep_num: int, freq: int, time_awoken: float, all_dep_uptimes: List[List[float]]):
    uptimes_dep: List[float] = all_dep_uptimes[dep_num]
    all_other_uptimes: List[List[float]] = [all_dep_uptimes[i] for i in range(len(all_dep_uptimes)) if dep_num != i]
    overlaps_list = []
    for other_uptimes_dep in all_other_uptimes:
        covering_time = 0
        for uptime_dep in uptimes_dep:
            for other_uptime_dep in other_uptimes_dep:
                overlap = min(uptime_dep + time_awoken, other_uptime_dep + time_awoken) - max(uptime_dep, other_uptime_dep)
                covering_time += overlap if overlap > 0 else 0

        percentage_overlap = covering_time/(time_awoken*freq)
        overlaps_list.append(percentage_overlap)

    return overlaps_list


def compute_means_covering_by_params(uptimes_by_params: Dict):
    # Calcul recouvrement moyen par OU, et recouvrement moyen global
    covering_by_params = {}
    for params, times_per_dep in uptimes_by_params.items():
        freq, time, nb_deps = params
        covering_by_params[params] = {}
        for dep_num, dep_times in times_per_dep.items():
            cov_perc_list = compute_covering_time_dep(dep_num, freq, time, [*times_per_dep.values()])
            covering_by_params[params][dep_num] = round(sum(cov_perc_list)/len(cov_perc_list), 2)

    return covering_by_params


def compute_global_means_covering(covering_by_params: Dict):
    global_means_coverage = {}
    for params, times_per_dep in covering_by_params.items():
        coverage_deps = covering_by_params[params]
        global_means_coverage[params] = round(sum(coverage_deps.values()) / len(coverage_deps.values()), 2)

    return global_means_coverage


def main():
    nb_deps_list = [2, 5, 10, 15, 20]
    freqs_awake_list = [1, 2, 3, 4, 5, 6, 7]
    time_awakening = [1, 3, 5]
    step_freq = 60
    print("---------- Wake up times by parameters -------------------")
    uptimes_by_params = generate_uptimes_for_dependencies(freqs_awake_list, time_awakening, nb_deps_list, step_freq)
    print(*[{k: v} for k, v in uptimes_by_params.items()], sep="\n")

    print("---------- Means coverage per deps -------------------")
    covering_by_params = compute_means_covering_by_params(uptimes_by_params)
    print(*[{k: v} for k, v in covering_by_params.items()], sep="\n")

    print("---------- Global means coverage between all deps -------------------")
    global_means_coverage = compute_global_means_covering(covering_by_params)
    print(*sorted([{k: v} for k, v in global_means_coverage.items()], key=lambda x: [*x.values()][0]), sep="\n")


if __name__ == '__main__':
    main()

