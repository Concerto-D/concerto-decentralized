import sys

from evaluation.synthetic_use_case.assemblies.dep_assembly import DepAssembly
import yaml


def get_assembly_parameters(args):
    dep_num = int(args[1])
    config_file_path = args[2]
    with open(config_file_path, "r") as f:
        loaded_config = yaml.safe_load(f)
    uptime_duration = float(args[3])
    return dep_num, loaded_config, uptime_duration


def deploy(sc, dep_num):
    sc.add_component(f"dep{dep_num}", sc.dep)
    sc.connect(f"dep{dep_num}", "ip", "server", f"serviceu_ip{dep_num}")
    sc.connect(f"dep{dep_num}", "service", "server", f"serviceu{dep_num}")
    sc.push_b(f"dep{dep_num}", "deploy")
    sc.wait_all()


def update(sc, dep_num):
    sc.push_b(f"dep{dep_num}", "update")
    sc.push_b(f"dep{dep_num}", "deploy")
    sc.wait_all()


def execute_reconf(dep_num, config_dict, duration, is_asynchrone=True):
    sc = DepAssembly(dep_num, config_dict, is_asynchrone=is_asynchrone)
    sc.set_verbosity(2)
    deploy(sc, dep_num)
    update(sc, dep_num)
    sc.execute_reconfiguration_program(duration)


if __name__ == '__main__':
    dep_num, config_dict, duration = get_assembly_parameters(sys.argv)
    sys.stdout = open(f"logs/output_dep{dep_num}", "a+")
    sys.stderr = sys.stdout
    execute_reconf(dep_num, config_dict, duration, is_asynchrone=True)
