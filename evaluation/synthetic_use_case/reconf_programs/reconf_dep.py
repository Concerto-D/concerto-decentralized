import logging
import sys

from concerto import time_logger
from concerto.time_logger import TimeToSave
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


def execute_reconf(dep_num, config_dict, duration, sleep_when_blocked=True):
    # TODO: où on commence à voir le temps de reconf ?
    time_logger.log_time_value(TimeToSave.START_RECONF)
    sc = DepAssembly(dep_num, config_dict, sleep_when_blocked=sleep_when_blocked)
    sc.set_verbosity(2)
    deploy(sc, dep_num)
    update(sc, dep_num)
    sc.execute_reconfiguration_program(duration)


if __name__ == '__main__':
    # TODO: avoir une fonction globale pour gérer reconf_dep et reconf_server
    dep_num, config_dict, duration = get_assembly_parameters(sys.argv)
    time_logger.init_time_log_dir(f"dep{dep_num}")
    time_logger.log_time_value(TimeToSave.UP_TIME)
    logging.basicConfig(filename=f"logs/logs_dep{dep_num}.txt", format='%(asctime)s %(message)s', filemode="a+")
    execute_reconf(dep_num, config_dict, duration, sleep_when_blocked=False)
    time_logger.log_time_value(TimeToSave.SLEEP_TIME)
