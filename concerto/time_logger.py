import time
from datetime import datetime
from pathlib import Path
from typing import Optional

LOG_DIR_NAME = "/tmp"
LOG_DIR_TIMESTAMP = ""
ASSEMBLY_NAME = ""


started_timestamps_set = set()


def create_timestamp_metric(timestamp_type, is_instruction_method=False):
    """
    If the node raise Exception saying it goes to sleep, then take the measure and
    exit the program
    """
    def _create_timestamp_metric(func):
        def wrapper(*args, **kwargs):
            print(args, kwargs)
            if not is_instruction_method:
                log_args, log_kwargs = (), {}
            else:
                log_args, log_kwargs = args[1:], kwargs   # args[1:] to ignore self

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
    Path(f"{LOG_DIR_NAME}/{ASSEMBLY_NAME}_{LOG_DIR_TIMESTAMP}.yaml").touch()


def log_time_value(timestamp_type: str, timestamp_period: str, *args, **kwargs):
    timestamp_name = register_time_value(timestamp_type, timestamp_period, *args, **kwargs)
    global started_timestamps_set
    if timestamp_period == TimestampPeriod.START:
        started_timestamps_set.add(timestamp_name)
    else:
        started_timestamps_set.remove(timestamp_name)


def register_time_value(timestamp_type: str, timestamp_period: str, *args, **kwargs):
    parameters_args = "-".join(args)
    parameters_kwargs = "-".join(map(str, kwargs.values()))
    timestamp_name = timestamp_type
    if parameters_args != "":
        timestamp_name += f"_{parameters_args}"
    if parameters_kwargs != "":
        timestamp_name += f"_{parameters_kwargs}"

    timestamp_to_save = f"{timestamp_name}_{timestamp_period}"
    register_log_time_value(timestamp_to_save)

    return timestamp_name


def register_log_time_value(timestamp_to_save: str):
    with open(f"{LOG_DIR_NAME}/{ASSEMBLY_NAME}_{LOG_DIR_TIMESTAMP}.yaml", "a") as f:
        f.write(f"{timestamp_to_save}: {time.time()}\n")


def register_end_all_time_values():
    for timestamp_name in started_timestamps_set:
        register_log_time_value(timestamp_name + "_" + TimestampPeriod.END)



