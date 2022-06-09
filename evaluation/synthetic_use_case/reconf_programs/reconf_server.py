import sys

from evaluation.synthetic_use_case.assemblies.server_assembly import ServerAssembly
import yaml


def get_assembly_parameters(args):
    config_file_path = args[1]
    with open(config_file_path, "r") as f:
        loaded_config = yaml.safe_load(f)
    # uptime_duration = float(args[2])
    uptime_duration = 20
    return loaded_config, uptime_duration


def deploy(sc, nb_deps_tot):
    sc.add_component("server", sc.server)
    for dep_num in range(nb_deps_tot):
        sc.connect("server", f"serviceu_ip{dep_num}", f"dep{dep_num}", "ip")
        sc.connect("server", f"serviceu{dep_num}", f"dep{dep_num}", "service")
    sc.push_b("server", "deploy")
    sc.wait_all()


def update(sc):
    sc.push_b("server", "suspend")
    sc.wait_all(wait_for_refusing_provide=True)
    sc.push_b("server", "deploy")
    sc.wait_all()


def execute_reconf(config_dict, duration, is_asynchrone=True):
    sc = ServerAssembly(config_dict, is_asynchrone=is_asynchrone)
    sc.set_verbosity(2)
    deploy(sc, config_dict["nb_deps_tot"])
    update(sc)
    sc.execute_reconfiguration_program(duration)


if __name__ == '__main__':
    sys.stdout = open("output.txt", "w")
    config_dict, duration = get_assembly_parameters(sys.argv)
    execute_reconf(config_dict, duration, is_asynchrone=True)
