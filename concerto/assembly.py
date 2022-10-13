#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: assembly
   :synopsis: this file contains the Assembly class.
"""
import time
from os.path import exists
from pathlib import Path
from typing import Dict, List, Set, Optional

from concerto import communication_handler, assembly_config, time_logger, global_variables, rest_communication, exposed_api
from concerto.communication_handler import CONN, DECONN, INACTIVE
from concerto.dependency import DepType
from concerto.component import Component
from concerto.debug_logger import log, log_once
from concerto.global_variables import CONCERTO_D_SYNCHRONOUS
from concerto.remote_dependency import RemoteDependency
from concerto.time_logger import TimestampType, create_timestamp_metric
from concerto.transition import Transition
from concerto.connection import Connection
from concerto.gantt_record import GanttRecord
from concerto.utility import COLORS, TimeManager

# In synchronous execution, how much interval (in seconds) to poll results
FREQUENCE_POLLING = 0.1


def track_instruction_number(func):
    """
    Keep track of the number of instruction executed, and ignore the instructions that have been
    already executed
    self is passed as argument since we decorate methods of the class
    """
    def _track_instruction_number(self, *args, **kwargs):
        if global_variables.current_nb_instructions_done >= self.global_nb_instructions_done[global_variables.reconfiguration_name]:
            result = func(self, *args, **kwargs)
        else:
            result = None
        global_variables.current_nb_instructions_done += 1
        return result

    return _track_instruction_number


class Assembly(object):
    """This Assembly class is used to create a assembly.

        An assembly is a set of component instances and the connection of
        their dependencies.
    """

    """
    BUILD ASSEMBLY
    """

    def __init__(
            self,
            name,
            components_types,
            remote_assemblies,
            transitions_times,
            waiting_rate,
            concerto_d_version,
            nb_concerto_nodes,
            reconfiguration_name
    ):
        self.time_manager = TimeManager(waiting_rate)
        self.components_types = components_types
        # dict of Component objects: id => object
        self.components: Dict[str, Component] = {}  # PERSIST
        # list of connection tuples. A connection tuple is of the form (component1, dependency1,
        # component2, dependency2)
        self.connections: Dict[str, Connection] = {}
        self.transitions_times = transitions_times

        self._remote_assemblies: List[str] = remote_assemblies
        self.nb_concerto_nodes = nb_concerto_nodes
        self.wait_for_refusing_provide = False

        # a dictionary to store at the assembly level a list of connections for
        # each component (name) of the assembly
        # this is used to improve performance of the semantics
        self.component_connections: Dict[str, Set[Connection]] = {}

        # set of active components
        self.act_components: Set[str] = set()

        # Nombre permettant de savoir à partir de quelle instruction reprendre le programme
        self.global_nb_instructions_done: Dict[str, int] = {reconfiguration_name: 0}

        self.waiting_rate = waiting_rate

        self.verbosity: int = 2
        self.print_time: bool = False
        self.dryrun: bool = False
        self.gantt: Optional[GanttRecord] = None
        self.name: str = name

        self.dump_program: bool = False
        self.program_str: str = ""

        self.error_reports: List[str] = []

        self.components_states = {}
        self.remote_confirmations: Set[str] = set()

        global_variables.concerto_d_version = concerto_d_version
        global_variables.reconfiguration_name = reconfiguration_name
        global_variables.current_nb_instructions_done = 0

        self._reprise_previous_config()

        if concerto_d_version == CONCERTO_D_SYNCHRONOUS:
            rest_communication.parse_inventory_file()
            rest_communication.load_communication_cache(self.get_name())
            exposed_api.run_api_in_thread(self)

    @property
    def obj_id(self):
        return self.name

    def to_json(self):
        return {
            "components": self.components,
            "connections": self.connections,
            "component_connections": self.component_connections,
            "act_components": self.act_components,
            "global_nb_instructions_done": self.global_nb_instructions_done,
            "waiting_rate": self.waiting_rate,
            "components_states": self.components_states,
            "remote_confirmations": self.remote_confirmations,
        }

    @create_timestamp_metric(TimestampType.TimestampEvent.LOADING_STATE)
    def _reprise_previous_config(self):
        """
        Check if the previous programm went to sleep (i.e. if a saved config file exists)
        and restore the previous config if so
        """
        # TODO: si on ne reprend pas le state on le log quand même ? Ca peut donner une idée du temps que ça prend sans devoir le récupérer
        if exists(assembly_config.build_saved_config_file_path(self.name)):
            log.debug(f"\33[33m --- conf found at {assembly_config.build_saved_config_file_path(self.name)} ----\033[0m")
            previous_config = assembly_config.load_previous_config(self)
            assembly_config.restore_previous_config(self, previous_config)
        else:
            log.debug("'\33[33m'----- Previous config doesn't NOT exists, starting from zero ----'\033[0m'")
            log.debug(f"'\33[33m'----- Searched in {assembly_config.build_saved_config_file_path(self.name)} -----'\033[0m'")

    def set_verbosity(self, level: int):
        self.verbosity = level
        for c in self.components:
            self.components[c].set_verbosity(level)

    def set_print_time(self, value: bool):
        self.print_time = value
        for c in self.components:
            self.components[c].set_print_time(value)

    def set_dryrun(self, value: bool):
        self.dryrun = value
        for c in self.components:
            self.components[c].set_dryrun(value)

    def set_record_gantt(self, value: bool):
        if value:
            if self.gantt is None:
                self.gantt = GanttRecord()
                for c in self.components:
                    self.components[c].set_gantt_record(self.gantt)
        else:
            self.gantt = None
            for c in self.components:
                self.components[c].set_gantt_record(None)

    def get_gantt_record(self) -> GanttRecord:
        return self.gantt

    def set_dump_program(self, value: bool):
        self.dump_program = value

    def get_program_dump(self):
        return self.program_str

    def clear_program_dump(self):
        self.program_str = ""

    def set_name(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name

    def get_debug_info(self) -> str:
        debug_info = "Inactive components:\n"
        for component_name in self.components:
            if component_name not in self.act_components:
                debug_info += "- %s: %s\n" % (
                    component_name, ','.join(self.components[component_name].get_active_places()))
        debug_info += "Active components:\n"
        for component_name in self.act_components:
            debug_info += self.components[component_name].get_debug_info()
        return debug_info

    def add_to_active_components(self, component_name: str):
        self.act_components.add(component_name)

    def remove_from_active_components(self, idle_components: Set[str]):
        self.act_components.difference_update(idle_components)

    def instanciate_component(self, name, comp_type: str):
        if name == "server":
            comp = self.components_types[comp_type](**self.transitions_times[name], nb_deps_tot=self.nb_concerto_nodes)
        else:
            comp = self.components_types[comp_type](**self.transitions_times[name])
        comp.set_name(name)
        comp.set_color(COLORS[len(self.components) % len(COLORS)])
        comp.set_verbosity(self.verbosity)
        comp.set_print_time(self.print_time)
        comp.set_dryrun(self.dryrun)
        comp.set_gantt_record(self.gantt)
        comp.set_assembly(self)

        return comp

    @track_instruction_number
    @create_timestamp_metric(TimestampType.TimestampInstruction.ADD, is_instruction_method=True)
    def add_component(self, name: str, comp_type: str):
        if name in self.components:
            raise Exception("Trying to add '%s' as a component while it is already a component" % name)
        comp = self.instanciate_component(name, comp_type)
        self.components[name] = comp
        self.component_connections[name] = set()
        self.add_to_active_components(name)  # _init

    @track_instruction_number
    @create_timestamp_metric(TimestampType.TimestampInstruction.DEL, is_instruction_method=True)
    def del_component(self, component_name: str):
        finished = False
        while not finished:
            finished = True
            if component_name in self.act_components:
                finished = False
            if len(self.component_connections[component_name]) > 0:
                finished = False  # TODO: should never go here
            del self.component_connections[component_name]
            del self.components[component_name]

            if not finished:
                self.run_semantics_iteration()

    @track_instruction_number
    @create_timestamp_metric(TimestampType.TimestampInstruction.CONN, is_instruction_method=True)
    def connect(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        """
        This method adds a connection between two components dependencies.
        Assumption: comp1_name and dep1_name are NOT remote
        :param comp1_name: The name of the first component to connect
        :param dep1_name:  The name of the dependency of the first component to connect
        :param comp2_name: The name of the second component to connect
        :param dep2_name:  The name of the dependency of the second component to connect
        """
        # [con] On n'aura pas accès à comp2 à moins de faire un échange de messages en plus:
        # - Remove la vérification
        # - Faire une vérification à partir du type de composant (si on part du principe
        # que les assemblies connaissent tous les types de composants possibles)
        # - Ajouter un échange de message avec les informations du composant d'en face
        finished = False
        log.debug(f"Creating connection: {comp1_name} {dep1_name} {comp2_name} {dep2_name}")
        while not finished:
            dep1, dep2 = self._compute_dependencies_from_names(comp1_name, dep1_name, comp2_name, dep2_name)
            connection_id = Connection.build_id_from_dependencies(dep1, dep2)
            if connection_id in self.connections:
                # log.debug(f"Connection already done: Waiting connection from {comp2_name}")
                finished = communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, CONN)
            else:
                finished = self._create_conn(comp1_name, dep1_name, comp2_name, dep2_name)

            if not finished:
                self.run_semantics_iteration()

    def _create_conn(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        dep1, dep2 = self._compute_dependencies_from_names(comp1_name, dep1_name, comp2_name, dep2_name)
        if DepType.valid_types(dep1.get_type(),
                               dep2.get_type()):
            # multiple connections are possible within MAD, so we do not
            # check if a dependency is already connected

            # create connection
            new_connection = Connection(dep1, dep2)

            if new_connection.obj_id in self.connections.keys():
                raise Exception("Trying to add already existing connection from %s.%s to %s.%s" % (
                    comp1_name, dep1_name, comp2_name, dep2_name))

            self.connections[new_connection.obj_id] = new_connection
            self.component_connections[comp1_name].add(new_connection)

            # self.component_connections ne sert qu'à faire une vérification au moment du del, un component remote
            # ne pourra jamais être del par l'assembly, donc ne pas l'ajouter à la liste est possible
            remote_connection = comp2_name not in self.components.keys()
            if not remote_connection:
                self.component_connections[comp2_name].add(new_connection)

            # [con] Ajouter la synchronization avec le composant d'en face
            # TODO: réfléchir sur le besoin de la synchronization pour le con: pourquoi attendre que la connection d'en face
            # soit faite, on peut juste lancer les bhvs et s'il n'y a pas de remote dependencies on considère la dépendance
            # non served
            if remote_connection:
                # Need d'initialiser le nombre de user sur la dépendance à 0 car si on veut déconnecter tout de suite,
                # un check est fait sur le nb d'utilisateur
                communication_handler.send_syncing_conn(comp1_name, comp2_name, dep1_name, dep2_name, CONN)
                is_conn_synced = communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, CONN)
                log.debug("Connection done locally, waiting for the connection message from:"
                                  f"{comp1_name} {comp2_name} {dep2_name} {dep1_name}")
                # log.debug(f"Is conn synced between {comp1_name} and {comp2_name} ? (for {dep1_name} and {dep2_name}): {is_conn_synced}")
                return is_conn_synced
            return True

        else:
            raise Exception("Trying to connect uncompatible dependencies %s.%s and %s.%s" % (
                comp1_name, dep1_name, comp2_name, dep2_name))

    def _compute_dependencies_from_names(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        is_comp1_remote = comp1_name not in self.components.keys()
        is_comp2_remote = comp2_name not in self.components.keys()
        if is_comp1_remote:
            dep2 = self.get_component(comp2_name).get_dependency(dep2_name)
            dep1 = RemoteDependency(
                comp1_name,
                dep1_name,
                DepType.compute_opposite_type(dep2.get_type())
            )
        elif is_comp2_remote:
            dep1 = self.get_component(comp1_name).get_dependency(dep1_name)
            dep2 = RemoteDependency(
                comp2_name,
                dep2_name,
                DepType.compute_opposite_type(dep1.get_type())
            )
        else:
            dep1 = self.get_component(comp1_name).get_dependency(dep1_name)
            dep2 = self.get_component(comp2_name).get_dependency(dep2_name)

        return dep1, dep2

    @track_instruction_number
    @create_timestamp_metric(TimestampType.TimestampInstruction.DCONN, is_instruction_method=True)
    def disconnect(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        """
        This method adds a connection between two components dependencies.
        Assumption: comp1_name and dep1_name are NOT remote
        :param comp1_name: The name of the first component to connect
        :param dep1_name:  The name of the dependency of the first component to connect
        :param comp2_name: The name of the second component to connect
        :param dep2_name:  The name of the dependency of the second component to connect
        """
        finished = False
        log.debug(f"Creating disconnection: {comp1_name} {dep1_name} {comp2_name} {dep2_name}")
        while not finished:
            dep1, dep2 = self._compute_dependencies_from_names(comp1_name, dep1_name, comp2_name, dep2_name)
            connection_id = Connection.build_id_from_dependencies(dep1, dep2)
            if connection_id not in self.connections:
                finished = communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, DECONN)
            else:
                finished = self._remove_conn(comp1_name, dep1_name, comp2_name, dep2_name)

            if not finished:
                self.run_semantics_iteration()

    def _remove_conn(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        dep1, dep2 = self._compute_dependencies_from_names(comp1_name, dep1_name, comp2_name, dep2_name)
        id_connection_to_remove = Connection.build_id_from_dependencies(dep1, dep2)

        if id_connection_to_remove not in self.connections.keys():
            raise Exception("Trying to remove unexisting connection from %s.%s to %s.%s" % (
                comp1_name, dep1_name, comp2_name, dep2_name))

        connection: Connection = self.connections[id_connection_to_remove]
        if connection.can_remove():
            connection.disconnect()
            self.component_connections[comp1_name].discard(connection)

            # self.component_connections ne sert qu'à faire une vérification au moment du del, un component remote
            # ne pourra jamais être del par l'assembly, donc ne pas l'ajouter à la liste est possible
            is_remote_disconnection = comp2_name not in self.components.keys()
            if not is_remote_disconnection:
                self.component_connections[comp2_name].discard(connection)
            del self.connections[id_connection_to_remove]

            # [dcon] Ajouter la synchronization avec le composant d'en face
            # TODO: réfléchir sur le besoin de la synchronization pour le dcon, parce qu'une fois que moi je me suis déco,
            # je n'ai pas besoin de savoir si les autres se sont déco (si on suppose un programme valide)
            if is_remote_disconnection:
                communication_handler.send_syncing_conn(comp1_name, comp2_name, dep1_name, dep2_name, DECONN)
                log.debug("Disconnection done locally, waiting for the disconnection message from:"
                                  f"{comp1_name} {comp2_name} {dep2_name} {dep1_name}")
                return communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, DECONN)

            return True
        else:
            return False

    @track_instruction_number
    @create_timestamp_metric(TimestampType.TimestampInstruction.PUSH_B, is_instruction_method=True)
    def push_b(self, component_name: str, behavior: str):
        component = self.get_component(component_name)
        component.queue_behavior(behavior)
        if component_name not in self.act_components:
            self.add_to_active_components(component_name)

    @track_instruction_number
    @create_timestamp_metric(TimestampType.TimestampInstruction.WAIT, is_instruction_method=True)
    def wait(self, component_name: str, wait_for_refusing_provide: bool = False):
        finished = False
        self.wait_for_refusing_provide = wait_for_refusing_provide
        while not finished:
            log_once.debug(f"Waiting for component {component_name} to finish its behaviors execution")
            if component_name in self.components.keys():  # Local component
                is_component_idle = component_name not in self.act_components
            else:                                         # Remote component
                is_component_idle = communication_handler.get_remote_component_state(component_name, self.name) == INACTIVE

            finished = is_component_idle

            if not finished:
                self.run_semantics_iteration()

        self.wait_for_refusing_provide = False

    @track_instruction_number
    @create_timestamp_metric(TimestampType.TimestampInstruction.WAITALL, is_instruction_method=True)
    def wait_all(self, wait_for_refusing_provide: bool = False):
        """
        Global synchronization
        :params wait_for_refusing_provide: Used to specify that the assembly need to wait for the provides
        ports connected to it that they finish their reconfiguration. Else the use port might reconfigure itself
        before receiving order to wait for the provide port to reconfigure itself.
        """
        finished = False
        self.wait_for_refusing_provide = wait_for_refusing_provide
        while not finished:
            finished = True
            if not len(self.act_components) == 0:
                log_once.debug(f"WAIT ALL {wait_for_refusing_provide} --- Local component not finished, actives components: {len(self.act_components)}")
                finished = False
            else:
                ass_to_wait = set()
                for ass_name in self._remote_assemblies:
                    assembly_idle = communication_handler.get_remote_component_state(ass_name, self.name) == INACTIVE
                    if not assembly_idle:
                        ass_to_wait.add(ass_name)
                        finished = False
                if ass_to_wait:
                    log_once.debug(f"WAIT ALL {wait_for_refusing_provide} --- Remote assembly {ass_to_wait} not finished, waiting for it")

                if None in self.remote_confirmations: self.remote_confirmations.remove(None)  # TODO fix bug

                if not wait_for_refusing_provide and finished and len(self._remote_assemblies) != len(self.remote_confirmations):
                    remotes_to_wait = [remote for remote in self._remote_assemblies if remote not in self.remote_confirmations]

                    log_once.debug(f"WAIT ALL {wait_for_refusing_provide} --- All remote finished, but waiting for their confirmations (remote asses to confirm: {len(self._remote_assemblies)}, actual remotes confirmations: {len(self.remote_confirmations)}). Remote that I don't have confirmation: {remotes_to_wait}")
                    finished = False

            if not finished:
                self.run_semantics_iteration()

        # End of global synchronization, reset all fields used for it
        if not wait_for_refusing_provide:
            self.remote_confirmations.clear()
            communication_handler.clear_global_synchronization_cache()

        self.wait_for_refusing_provide = False

    def is_component_idle(self, component_name: str) -> bool:
        if self.wait_for_refusing_provide:
            return False
        if component_name == self.get_name():
            res = self.is_idle()
            # log_once.debug(f"Is {component_name} idle: {res}")
            return res
        elif component_name in self.components.keys():
            res = component_name not in self.act_components
            # log_once.debug(f"Is {component_name} (comp) idle: {res}")
            return res
        else:
            raise Exception(f"Tried to call is_component_idle on a non-local component {component_name}")

    def is_idle(self):
        return len(self.act_components) == 0

    def get_component(self, name: str) -> Component:
        if name in self.components:
            return self.components[name]
        else:
            raise (Exception("ERROR - Unknown component %s" % name))

    def get_components(self) -> List[Component]:
        return list(self.components.values())

    def thread_safe_report_error(self, component: Component, transition: Transition, error: str):
        report = "Component: %s\nTransition: %s\nError:\n%s" % (component.name, transition.transition_name, error)
        self.error_reports.append(report)

    def get_error_reports(self) -> List[str]:
        return self.error_reports

    def finish_reconfiguration(self):
        log.debug("---------------------- END OF RECONFIGURATION GG -----------------------")
        Path(f"{global_variables.execution_expe_dir}/finished_reconfigurations/{self.obj_id}").touch()  # Create a file that serves as a flag
        self.go_to_sleep(50)

    def run_semantics_iteration(self):
        # Execute semantic iterator
        idle_components: Set[str] = set()
        are_active_transitions = False
        all_tokens_blocked = True
        for c in self.act_components:
            is_idle, did_something, are_active_transitions = self.components[c].semantics()
            if is_idle:
                idle_components.add(c)
            all_tokens_blocked = all_tokens_blocked and (not did_something)

        self.remove_from_active_components(idle_components)

        if self.is_idle():
            communication_handler.set_component_state(INACTIVE, self.name)

        # Check for sleeping conditions
        if self.time_manager.is_waiting_rate_time_up() and all_tokens_blocked:
            log.debug("Everyone blocked")
            log.debug("Going sleeping bye")
            self.go_to_sleep(0)
        elif self.time_manager.is_initial_time_up() and not are_active_transitions:
            log.debug("Time's up")
            log.debug("Go sleep")
            self.go_to_sleep(0)
        else:
            time.sleep(FREQUENCE_POLLING)

    def go_to_sleep(self, exit_code):
        assembly_config.save_config(self)
        if global_variables.concerto_d_version == CONCERTO_D_SYNCHRONOUS:
            rest_communication.save_communication_cache(self.get_name())
        time_logger.register_end_all_time_values()
        time_logger.register_timestamps_in_file()
        log.debug("")  # To separate differents sleeping rounds
        exit(exit_code)


