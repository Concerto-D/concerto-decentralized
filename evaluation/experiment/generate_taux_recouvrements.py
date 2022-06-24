import json
import os
import random
import time
from datetime import datetime
from itertools import product
from os.path import exists
from typing import List, Dict
import matplotlib
import yaml
from matplotlib import pyplot as plt


def generate_uptimes_by_params(
        freqs_awake_list: List[int],
        time_awakening: List[int],
        nb_deps_list: List[int],
) -> Dict:
    """
    TODO: reprendre le nom des variables (time, nb_deps, etc)
    returns: Dict de la forme:
    {(nb_de_reveils, temps_awoken, nb_OU_deps): {taux_1: [temps_reveils_list_ou1, temps_reveils_list_ou2, ...], ...}, ...}
    """
    uptimes_by_params = {}
    # Compute each possible combination between parameters
    for freq, duration, nb_deps in product(freqs_awake_list, time_awakening, nb_deps_list):

        covering_perc_values = {(0.02, 0.05): None, (0.20, 0.30): None, (0.50, 0.60): None}
        # We want to have uptimes for each choosen percentage value
        # TODO: voir si ça prend trop de temps on met une condition d'arrêt
        while not all(uptimes is not None for uptimes in covering_perc_values.values()):
            # On écarte de plus en plus la plage sur laquelle choisir les uptimes
            for step in range(duration, duration+2000, 20):
                uptimes_list = compute_uptimes_for_params(freq, nb_deps, step, duration)

                # Check if uptimes overlap fits into category
                covering_uptimes = []
                for dep_num, dep_times in enumerate(uptimes_list):
                    cov_perc_list = compute_covering_time_dep(dep_num, freq, duration, uptimes_list)
                    covering_uptimes.append(round(sum(cov_perc_list)/len(cov_perc_list), 2))
                global_means_coverage = round(sum(covering_uptimes) / len(covering_uptimes), 2)
                for cover_val in covering_perc_values.keys():
                    # TODO Mettre des intervals plus larges, entre 0.1 et 0.2, au lieu d'une valeur fixe
                    if covering_perc_values[cover_val] is None and cover_val[0] <= global_means_coverage < cover_val[1]:
                        print(f"Found for {(freq, duration, nb_deps)} {cover_val}")
                        covering_perc_values[cover_val] = uptimes_list

        uptimes_by_params[(freq, duration, nb_deps)] = covering_perc_values

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


def plot_uptimes(uptimes_by_params, datetime_now_formatted: str):
    # Configure to plot on images instead of screen
    matplotlib.use('Agg')

    line_number = 5      # Line number to plot uptimes, one line per OU
    figure_number = 0    # Figure number to plot

    # Create dir to store images
    plot_results_dir = f"evaluation/experiment/generated_covering_taux/{datetime_now_formatted}"
    os.makedirs(plot_results_dir)

    # For each combination of param, plot figure by covering percentage
    for params, uptimes_to_plot in uptimes_by_params.items():
        # Create dir to storage images for specific param combination
        freq, duration, nb_deps = params
        dir_to_save_name = f"{plot_results_dir}/{freq}_{duration}_{nb_deps}"
        os.makedirs(dir_to_save_name)

        # Create image for each covering percentage
        for perc, all_uptimes in uptimes_to_plot.items():
            plt.figure(figure_number)
            if all_uptimes is None: continue
            for uptimes_ou in all_uptimes:
                color_number = 0
                for uptime_tuple in uptimes_ou:
                    uptime, duration = uptime_tuple
                    start = uptime
                    end = uptime + duration
                    plt.plot([start, end], [line_number, line_number], 'br'[color_number])
                    color_number = not color_number
                line_number -= 0.5  # Decrease to print next OU
            plt.plot([1, 3], [8, 8], 'w')   # Used to get lines closer together (else it is spread vertically)
            plt.savefig(f"{dir_to_save_name}/{int(perc[0] * 100)}-{int(perc[1] * 100)}_percent_coverage.png")
            plt.close(figure_number)
            figure_number += 1
            line_number = 5


def main():
    # Compute uptimes
    freqs_awake_list = [30]            # Valeurs fixées
    time_awakening = [30, 60]          # Valeurs fixées
    nb_deps_list = [12]                # Valeurs fixées
    uptimes_by_params = generate_uptimes_by_params(freqs_awake_list, time_awakening, nb_deps_list)
    print("finished")

    datetime_now_formatted = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Plot uptimes
    plot_uptimes(uptimes_by_params, datetime_now_formatted)

    # Save uptimes
    with open(f"evaluation/experiment/generated_covering_taux/{datetime_now_formatted}/uptimes.json", "w") as f:
        json.dump({str(k): {str(perc): uptimes for perc, uptimes in v.items()} for k,v in uptimes_by_params.items()}, f)  # TODO: to refacto (que ce soit plus clair)


if __name__ == '__main__':
    main()
