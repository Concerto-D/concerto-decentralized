import time
from datetime import datetime
from pathlib import Path

LOG_DIR_NAME = "tmp"
LOG_DIR_TIMESTAMP = ""
ASSEMBLY_NAME = ""


class TimeToSave:
    UP_TIME = "up_time"
    START_LOADING_STATE = "start_loading_state"
    END_LOADING_STATE = "end_loading_state"
    START_RECONF = "start_reconf"
    END_RECONF = "end_reconf"
    START_SAVING_STATE = "start_saving_state"
    END_SAVING_STATE = "end_saving_state"
    SLEEP_TIME = "sleep_time"


def init_time_log_dir(assembly_name: str):
    global LOG_DIR_TIMESTAMP
    global ASSEMBLY_NAME
    LOG_DIR_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ASSEMBLY_NAME = assembly_name
    Path(f"{LOG_DIR_NAME}/{ASSEMBLY_NAME}_{LOG_DIR_TIMESTAMP}.yaml").touch()


def log_time_value(time_to_save_name: TimeToSave):
    with open(f"{LOG_DIR_NAME}/{ASSEMBLY_NAME}_{LOG_DIR_TIMESTAMP}.yaml", "a") as f:
        f.write(f"{time_to_save_name}: {time.time()}\n")
