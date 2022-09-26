import time

import zenoh

from concerto.debug_logger import log_once

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
    res = workspace.get(f"/nb_users/{component_name}/{dependency_name}")
    return int(res[0].value.get_content()) if len(res) > 0 else 0


@zenoh_session
def send_nb_dependency_users(nb: int, component_name: str, dependency_name: str, workspace=None):
    workspace.put(f"/nb_users/{component_name}/{dependency_name}", str(nb))


@zenoh_session
def get_refusing_state(component_name: str, dependency_name: str, workspace=None) -> int:
    res = workspace.get(f"/refusing/{component_name}/{dependency_name}")
    return bool(int(res[0].value.get_content())) if len(res) > 0 else False


@zenoh_session
def send_refusing_state(value: int, component_name: str, dependency_name: str, workspace=None):
    workspace.put(f"/refusing/{component_name}/{dependency_name}", int(value))


@zenoh_session
def get_data_dependency(component_name: str, dependency_name: str, workspace=None):
    res = workspace.get(f"/data/{component_name}/{dependency_name}")
    return res[0].value.get_content() if len(res) > 0 else ""


@zenoh_session
def write_data_dependency(component_name: str, dependency_name: str, data, workspace=None):
    workspace.put(f"/data/{component_name}/{dependency_name}", data)


@zenoh_session
def send_syncing_conn(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str, workspace=None):
    workspace.put(f"/{action}/{syncing_component}/{component_to_sync}/{dep_provide}/{dep_use}", action)


@zenoh_session
def is_conn_synced(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str, workspace=None):
    result = workspace.get(f"/{action}/{component_to_sync}/{syncing_component}/{dep_provide}/{dep_use}")
    return len(result) > 0 and result[0].value.get_content() == action


@zenoh_session
def set_component_state(state: [ACTIVE, INACTIVE], component_name: str, workspace=None):
    workspace.put(f"/wait/{component_name}", state)


@zenoh_session
def get_remote_component_state(component_name: str, workspace=None) -> [ACTIVE, INACTIVE]:
    result = workspace.get(f"/wait/{component_name}")
    log_once.debug(f"Wait for component state of {component_name}...")
    if len(result) <= 0:
        return ACTIVE
    else:
        return result[0].value.get_content()
