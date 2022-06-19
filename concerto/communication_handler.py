import time

import zenoh

from concerto import zenoh_communication
from concerto.utility import Printer

config = {}

CONN = "CONN"
DECONN = "DECONN"
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"


def get_nb_dependency_users(component_name: str, dependency_name: str, is_asynchronous=True) -> int:
    if is_asynchronous:
        return zenoh_communication.get_nb_dependency_users(component_name, dependency_name)


def send_nb_dependency_users(nb: int, component_name: str, dependency_name: str, is_asynchronous=True):
    if is_asynchronous:
        zenoh_communication.send_nb_dependency_users(nb, component_name, dependency_name)


def get_refusing_state(component_name: str, dependency_name: str, is_asynchronous=True) -> int:
    if is_asynchronous:
        return zenoh_communication.get_refusing_state(component_name, dependency_name)


def send_refusing_state(value: int, component_name: str, dependency_name: str, is_asynchronous=True):
    if is_asynchronous:
        zenoh_communication.send_refusing_state(value, component_name, dependency_name)


def get_data_dependency(component_name: str, dependency_name: str, is_asynchronous=True):
    if is_asynchronous:
        return zenoh_communication.get_data_dependency(component_name, dependency_name)


def write_data_dependency(component_name: str, dependency_name: str, data, is_asynchronous=True):
    if is_asynchronous:
        zenoh_communication.write_data_dependency(component_name, dependency_name)


def send_syncing_conn(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str, is_asynchronous=True):
    if is_asynchronous:
        zenoh_communication.send_syncing_conn(syncing_component, component_to_sync, dep_provide, dep_use, action)


def is_conn_synced(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str, is_asynchronous=True):
    if is_asynchronous:
        return zenoh_communication.is_conn_synced(syncing_component, component_to_sync, dep_provide, dep_use, action)


def set_component_state(state: [ACTIVE, INACTIVE], component_name: str, id_sync: int, is_asynchronous=True):
    if is_asynchronous:
        zenoh_communication.set_component_state(state, component_name, id_sync)


def get_remote_component_state(component_name: str, id_sync: int, is_asynchronous=True) -> [ACTIVE, INACTIVE]:
    if is_asynchronous:
        return zenoh_communication.get_remote_component_state(component_name, id_sync)
