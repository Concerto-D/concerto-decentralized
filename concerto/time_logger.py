import time
from datetime import datetime
from typing import Optional

import yaml

from concerto import global_variables
from concerto.debug_logger import log

LOG_DIR_TIMESTAMP = ""
ASSEMBLY_NAME = ""


all_timestamps_dict = {}


def create_timestamp_metric(timestamp_type, is_instruction_method=False):
    """
    If the node raise Exception saying it goes to sleep, then take the measure and
    exit the program
    """
    def _create_timestamp_metric(func):
        def wrapper(*args, **kwargs):
            if not is_instruction_method:
                log_args, log_kwargs = (), {}
            else:
                current_instruction_num = str(global_variables.current_nb_instructions_done)
                log_args, log_kwargs = (current_instruction_num, *args[1:]), dict(kwargs)   # args[1:] to ignore self

            log_time_value(timestamp_type, TimestampPeriod.START, *log_args, **log_kwargs)
            result = func(*args, **kwargs)
            log_time_value(timestamp_type, TimestampPeriod.END, *log_args, **log_kwargs)
            return result
        return wrapper
    return _create_timestamp_metric


class TimestampType:

    BEHAVIOR = "behavior"

    class TimestampEvent:
        TYPE = "event"

        UPTIME = f"{TYPE}_uptime"
        LOADING_STATE = f"{TYPE}_loading_state"
        SAVING_STATE = f"{TYPE}_saving_state"
        DEPLOY = f"{TYPE}_deploy"
        UPDATE = f"{TYPE}_update"

    class TimestampInstruction:
        TYPE = "instruction"

        ADD = f"{TYPE}_add"
        DEL = f"{TYPE}_del"
        CONN = f"{TYPE}_conn"
        DCONN = f"{TYPE}_dcon"
        PUSH_B = f"{TYPE}_push_b"
        WAIT = f"{TYPE}_wait"
        WAITALL = f"{TYPE}_waitall"


class TimestampPeriod:
    START = "start"
    END = "end"


def init_time_log_dir(assembly_name: str, timestamp_log_dir: Optional[str] = None):
    global LOG_DIR_TIMESTAMP
    global ASSEMBLY_NAME
    LOG_DIR_TIMESTAMP = timestamp_log_dir if timestamp_log_dir is not None else datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ASSEMBLY_NAME = assembly_name


def log_time_value(timestamp_type: str, timestamp_period: str, *args, **kwargs):
    register_time_value(timestamp_type, timestamp_period, *args, **kwargs)


def register_time_value(timestamp_type: str, timestamp_period: str, *args, **kwargs):
    parameters_args = "-".join(args)
    parameters_kwargs = "-".join(map(str, kwargs.values()))
    timestamp_name = timestamp_type
    if parameters_args != "":
        timestamp_name += f"_{parameters_args}"
    if parameters_kwargs != "":
        timestamp_name += f"_{parameters_kwargs}"

    if timestamp_period == TimestampPeriod.START:
        if timestamp_name in all_timestamps_dict.keys():
            raise Exception(f"Register time value start error: {timestamp_name} for {TimestampPeriod.START} already registered")
        all_timestamps_dict[timestamp_name] = {}
        all_timestamps_dict[timestamp_name][TimestampPeriod.START] = time.time()

    else:
        if timestamp_name not in all_timestamps_dict.keys():
            raise Exception(f"Register time value end error: {timestamp_name} never registered")
        if TimestampPeriod.END in all_timestamps_dict[timestamp_name]:
            raise Exception(f"Register time value start error: {timestamp_name} for {TimestampPeriod.END} already registered")
        all_timestamps_dict[timestamp_name][TimestampPeriod.END] = time.time()

    return timestamp_name


# TODO rename functions
def register_timestamps_in_file():
    log.debug(f"DUMPING FILE: {global_variables.execution_expe_dir}/{ASSEMBLY_NAME}_{LOG_DIR_TIMESTAMP}.yaml")
    with open(f"{global_variables.execution_expe_dir}/{ASSEMBLY_NAME}_{LOG_DIR_TIMESTAMP}.yaml", "w") as f:
        yaml.safe_dump(all_timestamps_dict, f)


def register_end_all_time_values():
    for timestamp_name, timestamp_values in all_timestamps_dict.items():
        if TimestampPeriod.END not in timestamp_values.keys():
            all_timestamps_dict[timestamp_name][TimestampPeriod.END] = time.time()



