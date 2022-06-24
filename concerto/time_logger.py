import time
from datetime import datetime
from pathlib import Path
from typing import Optional

LOG_DIR_NAME = "/tmp"
LOG_DIR_TIMESTAMP = ""
ASSEMBLY_NAME = ""


class TimeToSave:
    UP_TIME = "up_time"
    START_LOADING_STATE = "start_loading_state"
    END_LOADING_STATE = "end_loading_state"
    START_DEPLOY = "start_deploy"
    END_DEPLOY = "end_deploy"
    START_UPDATE = "start_update"
    END_UPDATE = "end_update"
    START_SAVING_STATE = "start_saving_state"
    END_SAVING_STATE = "end_saving_state"
    SLEEP_TIME = "sleep_time"


def init_time_log_dir(assembly_name: str, timestamp_log_dir: Optional[str] = None):
    global LOG_DIR_TIMESTAMP
    global ASSEMBLY_NAME
    LOG_DIR_TIMESTAMP = timestamp_log_dir if timestamp_log_dir is not None else datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ASSEMBLY_NAME = assembly_name
    Path(f"{LOG_DIR_NAME}/{ASSEMBLY_NAME}_{LOG_DIR_TIMESTAMP}.yaml").touch()


def log_time_value(time_to_save_name: str):
    with open(f"{LOG_DIR_NAME}/{ASSEMBLY_NAME}_{LOG_DIR_TIMESTAMP}.yaml", "a") as f:
        f.write(f"{time_to_save_name}: {time.time()}\n")


def start_deploy():
    log_time_value(TimeToSave.START_DEPLOY)


def end_deploy():
    log_time_value(TimeToSave.END_DEPLOY)


def start_update():
    log_time_value(TimeToSave.START_UPDATE)


def end_update():
    log_time_value(TimeToSave.END_UPDATE)
