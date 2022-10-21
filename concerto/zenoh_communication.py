import time

import zenoh

from concerto.debug_logger import log_once, log

config = {}

CONN = "CONN"
DECONN = "DECONN"
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"


class _ZenohSession:
    _session = None


def _get_zenoh_session():
    if _ZenohSession._session is None:
        _ZenohSession._session = zenoh.Zenoh(config)
    return _ZenohSession._session


def zenoh_session(func):
    """
    Décorateur permettant d'ouvrir et de fermer automatiquement une session Zenoh
    """
    def create_and_close_session(*args, **kwargs):
        session = _get_zenoh_session()
        workspace = session.workspace()
        result = func(*args, **kwargs, workspace=workspace)
        return result

    return create_and_close_session


@zenoh_session
def get_nb_dependency_users(component_name: str, dependency_name: str, workspace=None) -> int:
    zenoh_topic = f"/nb_users/{component_name}/{dependency_name}"
    res = workspace.get(zenoh_topic)
    int_res = int(res[0].value.get_content()) if len(res) > 0 else 0
    log_once.debug(f"Get nb dependency users on {zenoh_topic}, result: {int_res}")
    return int_res


@zenoh_session
def send_nb_dependency_users(nb: int, component_name: str, dependency_name: str, workspace=None):
    zenoh_topic = f"/nb_users/{component_name}/{dependency_name}"
    log_once.debug(f"Put nb dependency users {str(nb)} on {zenoh_topic}")
    workspace.put(zenoh_topic, str(nb))


@zenoh_session
def get_refusing_state(component_name: str, dependency_name: str, workspace=None) -> int:
    zenoh_topic = f"/refusing/{component_name}/{dependency_name}"
    res = workspace.get(zenoh_topic)
    bool_res = bool(int(res[0].value.get_content())) if len(res) > 0 else False
    log_once.debug(f"Get refusing state on {zenoh_topic}, result: {bool_res}")
    return bool_res


@zenoh_session
def send_refusing_state(value: int, component_name: str, dependency_name: str, workspace=None):
    zenoh_topic = f"/refusing/{component_name}/{dependency_name}"
    log_once.debug(f"Send refusing state {int(value)} on {zenoh_topic}")
    workspace.put(zenoh_topic, int(value))


@zenoh_session
def get_data_dependency(component_name: str, dependency_name: str, workspace=None):
    zenoh_topic = f"/data/{component_name}/{dependency_name}"
    res = workspace.get(zenoh_topic)
    str_res = res[0].value.get_content() if len(res) > 0 else ""
    log_once.debug(f"Get data dependency on {zenoh_topic}, result: {str_res}")
    return str_res


@zenoh_session
def write_data_dependency(component_name: str, dependency_name: str, data, workspace=None):
    zenoh_topic = f"/data/{component_name}/{dependency_name}"
    log_once.debug(f"Write date dependency {data} on {zenoh_topic}")
    workspace.put(zenoh_topic, data)


@zenoh_session
def send_syncing_conn(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str, workspace=None):
    zenoh_topic = f"/{action}/{syncing_component}/{component_to_sync}/{dep_provide}/{dep_use}"
    log_once.debug(f"Send synced connection {action} on {zenoh_topic}")
    workspace.put(zenoh_topic, action)


@zenoh_session
def is_conn_synced(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str, workspace=None):
    zenoh_topic = f"/{action}/{component_to_sync}/{syncing_component}/{dep_provide}/{dep_use}"
    result = workspace.get(zenoh_topic)
    if len(result) > 0:
        str_result = result[0].value.get_content()
    else:
        str_result = ""
    log_once.debug(f"Check synced connection on {zenoh_topic}, result: {str_result}")
    return str_result == action


@zenoh_session
def set_component_state(state: [ACTIVE, INACTIVE], component_name: str, reconfiguration_name: str, workspace=None):
    zenoh_topic = f"/wait/{reconfiguration_name}/{component_name}"
    log_once.debug(f"Put component state {state} on {zenoh_topic}")
    workspace.put(zenoh_topic, state)


@zenoh_session
def get_remote_component_state(component_name: str, reconfiguration_name: str, workspace=None) -> [ACTIVE, INACTIVE]:
    zenoh_topic = f"/wait/{reconfiguration_name}/{component_name}"
    result = workspace.get(zenoh_topic)
    if len(result) > 0:
        str_result = result[0].value.get_content()
    else:
        str_result = ACTIVE
    log_once.debug(f"Wait component state on {zenoh_topic}, result: {str_result}")
    return str_result
