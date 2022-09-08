import json
import os
import time
from os.path import exists

import yaml
import requests

from concerto.debug_logger import log
from concerto import global_variables

config = {}

CONN = "CONN"
DECONN = "DECONN"
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"


"""
inventory: each component should be associated with an ip/port
"""
INVENTORY_FILE_PATH = "inventory.yaml"
COMMUNICATION_CACHE_FILE = f"{global_variables.execution_expe_dir}/communication_cache"
inventory = {}
communications_cache = {}


def parse_inventory_file():
    log.debug(f"Loading inventory from {INVENTORY_FILE_PATH}")
    with open(INVENTORY_FILE_PATH, "r") as f:
        loaded_yaml = yaml.safe_load(f)
        for ass_comp_name, host in loaded_yaml.items():
            inventory[ass_comp_name] = host


def save_communication_cache(assembly_name):
    log.debug(f"Saving communication cache here {COMMUNICATION_CACHE_FILE}")
    os.makedirs(COMMUNICATION_CACHE_FILE, exist_ok=True)
    with open(f"{COMMUNICATION_CACHE_FILE}/{assembly_name}.json", "w") as f:
        json.dump(communications_cache, f)


def load_communication_cache(assembly_name):
    file_name = f"{COMMUNICATION_CACHE_FILE}/{assembly_name}.json"
    log.debug(f"Loading communication cache from {file_name}")
    if not exists(file_name):
        return

    with open(file_name, "r") as f:
        loaded_json = json.load(f)
        for key_cache, value in loaded_json.items():
            communications_cache[key_cache] = value

    os.remove(file_name)


def clear_communication_cache(assembly_name):
    """TODO: ne pas clear tout le cache, car besoin certainement des infos sur les connexions si on fait des deconn"""
    log.debug("Go from one reconf to another: CLEARING CACHE")
    communications_cache.clear()
    file_name = f"{COMMUNICATION_CACHE_FILE}/{assembly_name}.json"
    if exists(file_name):
        os.remove(file_name)


def _is_url_accessible(url):
    try:
        requests.head(url)
        return True
    except requests.exceptions.ConnectionError:
        log.debug(f"{url} is not available at this moment")
        return False


def get_results_from_request(key_cache, url, default_value, params=None):
    try:
        if _is_url_accessible(url):
            result = requests.get(url, params=params).text
            communications_cache[key_cache] = result
        else:
            result = communications_cache[key_cache] if key_cache in communications_cache.keys() else default_value
    except requests.exceptions.ConnectionError:
        result = communications_cache[key_cache] if key_cache in communications_cache.keys() else default_value
    return result


# TODO: refacto les routes
def get_nb_dependency_users(component_name: str, dependency_name: str) -> int:
    log.debug(f"Request: get_nb_dependency_users({component_name}, {dependency_name})")
    endpoint_name = "get_nb_dependency_users"
    target_host = inventory[component_name]
    url = f"http://{target_host}/{endpoint_name}/{component_name}/{dependency_name}"
    key_cache = endpoint_name + component_name + dependency_name
    result = int(get_results_from_request(key_cache, url, 0))
    log.debug(f"Result: {result}")
    return result


def get_refusing_state(component_name: str, dependency_name: str) -> int:
    log.debug(f"Request: get_refusing_state({component_name}, {dependency_name})")
    endpoint_name = "get_refusing_state"
    target_host = inventory[component_name]
    url = f"http://{target_host}/{endpoint_name}/{component_name}/{dependency_name}"
    key_cache = endpoint_name + component_name + dependency_name
    result = get_results_from_request(key_cache, url, "False") == "True"
    log.debug(f"Result: {result}")
    return result


def get_data_dependency(component_name: str, dependency_name: str):
    log.debug(f"Request: get_data_dependency({component_name}, {dependency_name})")
    endpoint_name = "get_data_dependency"
    target_host = inventory[component_name]
    url = f"http://{target_host}/{endpoint_name}/{component_name}/{dependency_name}"
    key_cache = endpoint_name + component_name + dependency_name
    result = get_results_from_request(key_cache, url, "")
    log.debug(f"Result: {result}")
    return result


def is_conn_synced(syncing_component: str, component_to_sync: str,  dep_provide: str, dep_use: str, action: str):
    log.debug(f"Request: is_conn_synced({syncing_component}, {component_to_sync}, {dep_provide}, {dep_use}, {action})")
    endpoint_name = "is_conn_synced"
    target_host = inventory[component_to_sync]
    url = f"http://{target_host}/{endpoint_name}/{syncing_component}/{component_to_sync}/{dep_provide}/{dep_use}/{action}"
    key_cache = endpoint_name + syncing_component + component_to_sync + dep_provide + dep_use + action
    result = get_results_from_request(key_cache, url, "False") == "True"
    log.debug(f"Result: {result}")
    return result


def get_remote_component_state(component_name: str, id_sync: int, calling_assembly_name: str) -> [ACTIVE, INACTIVE]:
    log.debug(f"Request: get_remote_component_state({component_name}, {id_sync})")
    endpoint_name = "get_remote_component_state"
    target_host = inventory[component_name]
    url = f"http://{target_host}/{endpoint_name}/{component_name}/{id_sync}"
    key_cache = component_name + str(id_sync)
    params = {"calling_assembly_name": calling_assembly_name}
    result = get_results_from_request(key_cache, url, ACTIVE, params=params)
    log.debug(f"Result: {result}")
    return result


def check_finished_assemblies(assembly, wait_for_refusing_provide):
    wait_finished_assemblies_cond = True
    if assembly._p_id_sync == 1 and not wait_for_refusing_provide:
        log.debug(
            f"Waiting for finished reconf: {assembly._p_remote_confirmations}{len(assembly._p_remote_confirmations)} {assembly._remote_assemblies_names}{len(assembly._remote_assemblies_names)}")
        wait_finished_assemblies_cond = len(assembly._p_remote_confirmations) == len(assembly._remote_assemblies_names)
    return wait_finished_assemblies_cond
