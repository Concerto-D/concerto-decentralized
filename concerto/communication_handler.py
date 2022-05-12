import time

import zenoh

config = {}

CONN = "CONN"
DECONN = "DECONN"
SLEEPING_TIME = 1


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
    res = workspace.get(f"/{component_name}/{dependency_name}")
    return int(res[0].value.get_content())


@zenoh_session
def send_nb_dependency_users(nb: int, component_name: str, dependency_name: str, workspace=None):
    workspace.put(f"/{component_name}/{dependency_name}", str(nb))


@zenoh_session
def send_syncing_conn(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str, workspace=None):
    # TODO Un seul topic pour conn et decon
    workspace.put(f"/{action}/{syncing_component}/{component_to_sync}/{dep_provide}/{dep_use}", action)


@zenoh_session
def wait_conn_to_sync(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str, workspace=None):
    # TODO Un seul topic pour conn et decon
    result = []
    while len(result) <= 0 or result[0].value.get_content() != action:
        result = workspace.get(f"/{action}/{component_to_sync}/{syncing_component}/{dep_provide}/{dep_use}")
        time.sleep(SLEEPING_TIME)
