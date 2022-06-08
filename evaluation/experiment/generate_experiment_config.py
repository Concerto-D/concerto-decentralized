from typing import Dict
from random import uniform
import jinja2

nb_deps_tot = 2


def generate_server_transitions_time(min_value: float = 0., max_value: float = 10.) -> Dict:
    server_t_sa = uniform(min_value, max_value)
    server_t_sc = [uniform(min_value, max_value) for i in range(nb_deps_tot)]
    server_t_sr = uniform(min_value, max_value)
    server_t_ss = [uniform(min_value, max_value) for i in range(nb_deps_tot)]
    server_t_sp = [uniform(min_value, max_value) for i in range(nb_deps_tot)]
    return {
        "server_t_sa": server_t_sa,
        "server_t_sc": server_t_sc,
        "server_t_sr": server_t_sr,
        "server_t_ss": server_t_ss,
        "server_t_sp": server_t_sp,
    }


def generate_deps_transitions_time(min_value: float = 0., max_value: float = 10.) -> Dict:
    deps_t_di = [uniform(min_value, max_value) for i in range(nb_deps_tot)]
    deps_t_dr = [uniform(min_value, max_value) for i in range(nb_deps_tot)]
    deps_t_du = [uniform(min_value, max_value) for i in range(nb_deps_tot)]
    return {
        "deps_t_di": deps_t_di,
        "deps_t_dr": deps_t_dr,
        "deps_t_du": deps_t_du,
    }


def generate_node_uptimes(
        total_wake_up: int = 10,
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
        time_to_wake_up = next_time_to_wake_up + freq
        uptime = uptime_duration + uniform(-variable_uptime, variable_uptime)
        node_awake_times_list.append((time_to_wake_up, uptime))
        next_time_to_wake_up += freq + uptime

    return node_awake_times_list


def generate_server_uptimes():
    return {
        "server_awake_times_list": generate_node_uptimes()
    }


def generate_deps_uptimes():
    return {
        "deps_awake_times_lists": [generate_node_uptimes() for _ in range(nb_deps_tot)]
    }


def generate_reconf_configuration():
    configuration = {}
    configuration.update(generate_server_transitions_time())
    configuration.update(generate_deps_transitions_time())
    configuration.update(generate_server_uptimes())
    configuration.update(generate_deps_uptimes())

    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader('evaluation/experiment/templates'))
    template = template_env.get_template("experiment_config.yaml.j2")
    rendered_template = template.render(
        nb_deps_tot=nb_deps_tot,
        **configuration
    )

    hash_file = str(abs(hash(rendered_template)))
    path_file = f"evaluation/experiment/generated_configurations/experiment_config_{hash_file}.yml"
    with open(path_file, "w") as f:
        f.write(rendered_template)

    return path_file


if __name__ == '__main__':
    file_name = generate_reconf_configuration()
    print(f"Config generated at {file_name}")
