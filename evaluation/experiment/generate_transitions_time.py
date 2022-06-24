import random
from typing import Tuple


def generate_server_transitions_time(nb_deps: int, min_value: float = 10., max_value: float = 60.) -> Tuple:
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


def generate_deps_transitions_time(dep_num: int, min_value: float = 10., max_value: float = 60.) -> Tuple:
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
