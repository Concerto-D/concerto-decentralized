import json
import queue
import shutil
import os
from typing import Dict
from pathlib import Path

import concerto
from concerto import time_logger
from concerto.component import Component, Group
from concerto.connection import Connection
from concerto.dependency import DepType, Dependency
from concerto.internal_instruction import InternalInstruction
from concerto.debug_logger import log
from concerto.place import Dock, Place
from concerto.time_logger import TimeToSave
from concerto.transition import Transition
from concerto.utility import Printer

SAVED_CONFIG_DIRECTORY = "."
ARCHIVE_DIR_NAME = "archives_reprises"
REPRISE_DIR_NAME = "reprise_configs"


class FixedEncoder(json.JSONEncoder):
    def default(self, obj):
        if any(isinstance(obj, k) for k in [concerto.assembly.Assembly, Component, Dependency, Dock, Connection, Place, Transition, InternalInstruction, Group]):
            d = obj.__dict__
            output = {}
            for k, v in d.items():
                if k.startswith("_p_"):
                    output[k] = v
            if any(isinstance(obj, k) for k in [Component, Connection, Dock]):
                output["_p_id"] = obj._p_id
            return output
        elif isinstance(obj, DepType) or isinstance(obj, InternalInstruction.Type):
            return obj.name
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, queue.Queue):
            return list(obj.queue)
        else:
            return obj


def build_saved_config_file_path(assembly_name: str, is_archive: bool = False) -> str:
    if is_archive:
        relative_path = f"{SAVED_CONFIG_DIRECTORY}/{ARCHIVE_DIR_NAME}/saved_config_{assembly_name}.json"
    else:
        relative_path = f"{SAVED_CONFIG_DIRECTORY}/{REPRISE_DIR_NAME}/saved_config_{assembly_name}.json"
    abs_path = str(Path(relative_path).resolve())
    return abs_path


def save_config(assembly):
    Printer.st_tprint("Saving current conf ...")
    time_logger.log_time_value(TimeToSave.START_SAVING_STATE)
    with open(build_saved_config_file_path(assembly.name), "w") as outfile:
        json.dump(assembly, outfile, cls=FixedEncoder, indent=4)
    time_logger.log_time_value(TimeToSave.END_SAVING_STATE)


def load_previous_config(assembly):
    Printer.st_tprint("Retrieving previous conf ...")
    file_path = build_saved_config_file_path(assembly.name)
    with open(file_path, "r") as infile:
        result = json.load(infile)
        Printer.st_tprint("done")

    Printer.st_tprint(f"Archiving file in {build_saved_config_file_path(assembly.name, is_archive=True)}")
    shutil.copyfile(
        file_path,
        build_saved_config_file_path(assembly.name, is_archive=True)
    )
    Printer.st_tprint(f"Removing previous conf ...")
    os.remove(file_path)
    Printer.st_tprint("done")
    return result


def restore_previous_config(assembly, previous_config, reconf_configuration: Dict):
    # Restore components
    components_dicts = previous_config['_p_components']
    components_names = components_dicts.keys()
    components = _instanciate_components(assembly, previous_config, reconf_configuration)
    for comp_values in components_dicts.values():
        component = _restore_component(assembly, comp_values, components_names, components)
        assembly._p_components[component._p_id] = component

    assembly._p_connections = {}
    # Restore connections
    for conn_data in previous_config['_p_connections'].keys():
        dep1_id, dep2_id = conn_data.split("/")
        comp1_name, dep1_name = dep1_id.split("-")
        comp2_name, dep2_name = dep2_id.split("-")

        dep1, dep2 = assembly._compute_dependencies_from_names(comp1_name, dep1_name, comp2_name, dep2_name)
        conn = Connection(dep1, dep2)
        if comp1_name in assembly._p_components.keys():
            assembly._p_component_connections[comp1_name].add(conn)
        if comp2_name in assembly._p_components.keys():
            assembly._p_component_connections[comp2_name].add(conn)
        assembly._p_connections[conn._p_id] = conn

    assembly._p_act_components = set(previous_config['_p_act_components'])
    assembly._p_id_sync = previous_config['_p_id_sync']
    assembly._p_nb_instructions_done = previous_config['_p_nb_instructions_done']
    assembly._p_sleep_when_blocked = previous_config['_p_sleep_when_blocked']


def _instanciate_components(assembly, previous_config, reconf_configuration: Dict):
    components_dicts = previous_config['_p_components']
    components = {}
    for comp_values in components_dicts.values():
        comp_id = comp_values['_p_id']
        comp_type = comp_values['_p_component_type']
        component_params = reconf_configuration['transitions_time'][comp_id]
        # TODO: à refacto
        if "server" in comp_id:
            component = assembly.components_types[comp_type](nb_deps=reconf_configuration['nb_deps_tot'], **component_params)
        else:
            component = assembly.components_types[comp_type](**component_params)
        component.set_name(comp_id)
        component.set_assembly(assembly)
        components[comp_id] = component

    return components


def _restore_component(assembly, comp_values, components_names, components):
    comp_id = comp_values['_p_id']
    component = components[comp_id]
    assembly._p_component_connections[comp_id] = set()
    component._p_initialized = comp_values['_p_initialized']

    # Restore dependencies
    for dep_values in comp_values['_p_st_dependencies'].values():
        dep_comp = component._p_st_dependencies[dep_values['_p_name']]
        dep_comp._p_is_refusing = dep_values['_p_is_refusing']
        dep_comp._p_nb_users = dep_values['_p_nb_users']
        dep_comp._p_data = dep_values['_p_data']

    # Restore groups
    for group_name in comp_values['_p_st_groups'].keys():
        group_comp = component._p_st_groups[group_name]
        group_vals = comp_values['_p_st_groups'][group_name]
        group_comp._p_nb_tokens = group_vals['_p_nb_tokens']

    # Restore active places
    for place_dict in comp_values['_p_act_places']:
        place_comp = component._p_st_places[place_dict['_p_name']]
        component._p_act_places.add(place_comp)

    # Restore active transitions
    for transitions_dict in comp_values['_p_act_transitions']:
        transitions_comp = component._p_st_transitions[transitions_dict['_p_name']]
        component._p_act_transitions.add(transitions_comp)

    # Restore active odocks
    for odock in comp_values['_p_act_odocks']:

        # Finding corresponding odock
        for transition in component._p_st_transitions.values():
            if transition.src_dock._p_id == odock['_p_id']:
                component._p_act_odocks.add(transition.src_dock)

    # Restore active idocks
    for idock in comp_values['_p_act_idocks']:

        # Finding corresponding idock
        for transition in component._p_st_transitions.values():
            if transition.dst_dock._p_id == idock['_p_id']:
                component._p_act_idocks.add(transition.dst_dock)


    # Restore active behavior
    component._p_act_behavior = comp_values['_p_act_behavior']

    # Restore queued behaviors
    for bhv in comp_values['_p_queued_behaviors']:
        component.queue_behavior(bhv)

    # Restore visited places
    for place_dict in comp_values['_p_visited_places']:
        place_comp = component._p_st_places[place_dict['_p_name']]
        component._p_visited_places.add(place_comp)

    return component
