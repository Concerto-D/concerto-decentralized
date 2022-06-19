import time

import zenoh

from concerto import zenoh_communication
from concerto.utility import Printer

config = {}

CONN = "CONN"
DECONN = "DECONN"
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"


"""
inventory: each component should be associated with an ip/port
"""
inventory = {}


def get_nb_dependency_users(component_name: str, dependency_name: str, is_asynchronous=True) -> int:
    return


def send_nb_dependency_users(nb: int, component_name: str, dependency_name: str, is_asynchronous=True):
    return


def get_refusing_state(component_name: str, dependency_name: str, is_asynchronous=True) -> int:
    return


def send_refusing_state(value: int, component_name: str, dependency_name: str, is_asynchronous=True):
    return


def get_data_dependency(component_name: str, dependency_name: str, is_asynchronous=True):
    return


def write_data_dependency(component_name: str, dependency_name: str, data, is_asynchronous=True):
    return


def send_syncing_conn(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str, is_asynchronous=True):
    return


def is_conn_synced(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str, is_asynchronous=True):
    return


def set_component_state(state: [ACTIVE, INACTIVE], component_name: str, id_sync: int, is_asynchronous=True):
    return


def get_remote_component_state(component_name: str, id_sync: int, is_asynchronous=True) -> [ACTIVE, INACTIVE]:
    return
