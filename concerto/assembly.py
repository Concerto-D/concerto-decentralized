#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: assembly
   :synopsis: this file contains the Assembly class.
"""
import sys
import time
import traceback
from os.path import exists
from pathlib import Path
from typing import Dict, List, Set, Optional
from threading import Thread
from queue import Queue

from concerto import communication_handler, assembly_config, time_logger
from concerto.communication_handler import CONN, DECONN, INACTIVE
from concerto.dependency import DepType
from concerto.component import Component
from concerto.debug_logger import log
from concerto.remote_dependency import RemoteDependency
from concerto.time_logger import TimeToSave
from concerto.transition import Transition
from concerto.connection import Connection
from concerto.internal_instruction import InternalInstruction, InternalInstructionNumAttribution
from concerto.reconfiguration import Reconfiguration
from concerto.gantt_record import GanttRecord
from concerto.utility import Messages, COLORS, Printer, TimeManager

# In synchronous execution, how much interval (in seconds) to poll results
FREQUENCE_POLLING = 1


class Assembly(object):
    """This Assembly class is used to create a assembly.

        An assembly is a set of component instances and the connection of
        their dependencies.
    """

    """
    BUILD ASSEMBLY
    """

    def __init__(self, name, components_types, remote_component_names, remote_assemblies_names, reconf_config_dict, sleep_when_blocked=True):
        self.time_manager = TimeManager()
        self.components_types = components_types
        # dict of Component objects: id => object
        self._p_components: Dict[str, Component] = {}  # PERSIST
        # list of connection tuples. A connection tuple is of the form (component1, dependency1,
        # component2, dependency2)
        self._p_connections: Dict[str, Connection] = {}

        self._remote_components_names: Set[str] = remote_component_names
        self._remote_assemblies_names: Set[str] = remote_assemblies_names

        # a dictionary to store at the assembly level a list of connections for
        # each component (name) of the assembly
        # this is used to improve performance of the semantics
        self._p_component_connections: Dict[str, Set[Connection]] = {}

        # Operational semantics

        # thread running the semantics of the assembly in a loop
        # TODO: checker pk le debug crash au bout d'un temps sur WSL (timeout ?)
        self.semantics_thread: Thread = Thread(name="semantic_thread", target=self.loop_smeantics)
        self.alive: bool = True

        # queue of instructions (synchronized with semantics thread)
        self._p_instructions_queue = Queue()  # thread-safe  # PERSIST
        self._p_current_instruction = None  # PERSIST
        self.instruction_num_attribution = InternalInstructionNumAttribution()

        # set of active components
        self._p_act_components: Set[str] = set()  # PERSIST

        # Identifiant permettant de synchronizer les wait et waitall
        self._p_id_sync = 0  #PERSIST

        # Nombre permettant de savoir à partir de quelle instruction reprendre le programme
        self._p_nb_instructions_done = 0

        self._p_sleep_when_blocked = sleep_when_blocked

        self.verbosity: int = 0
        self.print_time: bool = False
        self.dryrun: bool = False
        self.gantt: Optional[GanttRecord] = None
        self.name: str = name

        self.dump_program: bool = False
        self.program_str: str = ""

        self.error_reports: List[str] = []
        self._reprise_previous_config(reconf_config_dict)

    @property
    def _p_id(self):
        return self.name

    def _reprise_previous_config(self, reconf_config_dict: Dict):
        """
        Check if the previous programm went to sleep (i.e. if a saved config file exists)
        and restore the previous config if so
        """
        # TODO: si on ne reprend pas le state on le log quand même ? Ca peut donner une idée du temps que ça prend sans devoir le récupérer
        time_logger.log_time_value(TimeToSave.START_LOADING_STATE)
        if exists(assembly_config.build_saved_config_file_path(self.name)):
            log.debug(f"\33[33m --- conf found at {assembly_config.build_saved_config_file_path(self.name)} ----\033[0m")
            previous_config = assembly_config.load_previous_config(self)
            assembly_config.restore_previous_config(self, previous_config, reconf_config_dict)
        else:
            log.debug("'\33[33m'----- Previous config doesn't NOT exists, starting from zero ----'\033[0m'")
            log.debug(f"'\33[33m'----- Searched in {assembly_config.build_saved_config_file_path(self.name)} -----'\033[0m'")
        time_logger.log_time_value(TimeToSave.END_LOADING_STATE)

    def set_verbosity(self, level: int):
        self.verbosity = level
        for c in self._p_components:
            self._p_components[c].set_verbosity(level)

    def set_print_time(self, value: bool):
        self.print_time = value
        for c in self._p_components:
            self._p_components[c].set_print_time(value)

    def set_dryrun(self, value: bool):
        self.dryrun = value
        for c in self._p_components:
            self._p_components[c].set_dryrun(value)

    def set_record_gantt(self, value: bool):
        if value:
            if self.gantt is None:
                self.gantt = GanttRecord()
                for c in self._p_components:
                    self._p_components[c].set_gantt_record(self.gantt)
        else:
            self.gantt = None
            for c in self._p_components:
                self._p_components[c].set_gantt_record(None)

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
        for component_name in self._p_components:
            if component_name not in self._p_act_components:
                debug_info += "- %s: %s\n" % (
                    component_name, ','.join(self._p_components[component_name].get_active_places()))
        debug_info += "Active components:\n"
        for component_name in self._p_act_components:
            debug_info += self._p_components[component_name].get_debug_info()
        return debug_info

    def terminate(self, debug=False):
        if debug:
            Printer.st_err_tprint("DEBUG terminate:\n%s" % self.get_debug_info())
        for component_name in self._p_act_components:
            self.wait(component_name)
            if debug:
                Printer.st_err_tprint("DEBUG terminate: waiting component '%s'" % component_name)
        self.synchronize()
        self.alive = False
        self.semantics_thread.join()

    def force_terminate(self):
        self.synchronize()
        self.alive = False
        self.semantics_thread.join()

    def kill(self):
        """Warning: use only as last resort, anything run by the assembly will be killed, not exiting properly code
        run by the transitions """
        self.alive = False
        self.semantics_thread.join()

    def print(self, string: str):
        if self.verbosity < 0:
            return
        if self.name is None:
            name = "Assembly"
        else:
            name = self.name
        message: str = "[%s] %s" % (name, string)
        if self.print_time:
            Printer.st_tprint(message)
        else:
            Printer.print(message)

    def add_instruction(self, instruction: InternalInstruction):
        # Check if instruction has been done already
        # Do not add it to the queue if its the case
        if instruction.num < self._p_nb_instructions_done:
            return

        if self.dump_program:
            self.program_str += (str(instruction) + "\n")

        self._p_instructions_queue.put(instruction)

    def execute_reconfiguration_program(self, duration: float):
        self.time_manager.start(duration)
        self.start_reconf_timer()
        if not self.semantics_thread.is_alive():
            self.semantics_thread.start()

        self.semantics_thread.join()

    def start_reconf_timer(self):
        """
        TODO: very ad-hoc solution, to refacto
        """
        if self._p_id_sync == 0:
            time_logger.start_deploy()
        if self._p_id_sync == 1:
            time_logger.start_update()

    def end_reconf_timer(self):
        """
        TODO: very ad-hoc solution, to refacto
        """
        if self._p_id_sync == 0:
            time_logger.end_deploy()
        if self._p_id_sync == 1:
            time_logger.end_update()

    def run_reconfiguration(self, reconfiguration: Reconfiguration):
        for instr in reconfiguration._get_instructions():
            self.add_instruction(instr)

    def add_to_active_components(self, component_name: str):
        self._p_act_components.add(component_name)

    def remove_from_active_components(self, idle_components: Set[str]):
        self._p_act_components.difference_update(idle_components)

    def add_component(self, name: str, comp: Component):
        instruction = InternalInstruction.build_add(name, comp)
        self.instruction_num_attribution.attribute_num(instruction)
        self.add_instruction(instruction)

    def _add(self, name: str, comp: Component) -> bool:
        """
        This method adds a component instance to the assembly

        :param comp: the component instance to add
        """
        if name in self._p_components:
            raise Exception("Trying to add '%s' as a component while it is already a component" % name)
        comp.set_name(name)
        comp.set_color(COLORS[len(self._p_components) % len(COLORS)])
        comp.set_verbosity(self.verbosity)
        comp.set_print_time(self.print_time)
        comp.set_dryrun(self.dryrun)
        comp.set_gantt_record(self.gantt)
        comp.set_assembly(self)
        self._p_components[name] = comp
        self._p_component_connections[name] = set()
        self.add_to_active_components(name)  # _init
        return True

    def del_component(self, component_name: str):
        instruction = InternalInstruction.build_del(component_name)
        self.instruction_num_attribution.attribute_num(instruction)
        self.add_instruction(instruction)

    def _del(self, component_name: str) -> bool:
        if component_name in self._p_act_components:
            return False
        if len(self._p_component_connections[component_name]) > 0:
            return False
        del self._p_component_connections[component_name]
        del self._p_components[component_name]
        return True

    def connect(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        instruction = InternalInstruction.build_connect(comp1_name, dep1_name, comp2_name, dep2_name)
        self.instruction_num_attribution.attribute_num(instruction)
        self.add_instruction(instruction)

    def _connect(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str) -> bool:
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
        dep1, dep2 = self._compute_dependencies_from_names(comp1_name, dep1_name, comp2_name, dep2_name)
        connection_id = Connection.build_id_from_dependencies(dep1, dep2)
        if connection_id in self._p_connections:
            Printer.st_tprint(f"Connection already done: Waiting connection from {comp2_name}")
            result = communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, CONN)
        else:
            result = self._create_conn(comp1_name, dep1_name, comp2_name, dep2_name)

        return result

    def _create_conn(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        dep1, dep2 = self._compute_dependencies_from_names(comp1_name, dep1_name, comp2_name, dep2_name)
        if DepType.valid_types(dep1.get_type(),
                               dep2.get_type()):
            # multiple connections are possible within MAD, so we do not
            # check if a dependency is already connected

            # create connection
            new_connection = Connection(dep1, dep2)

            if new_connection._p_id in self._p_connections.keys():
                raise Exception("Trying to add already existing connection from %s.%s to %s.%s" % (
                    comp1_name, dep1_name, comp2_name, dep2_name))

            self._p_connections[new_connection._p_id] = new_connection
            self._p_component_connections[comp1_name].add(new_connection)

            # self._p_component_connections ne sert qu'à faire une vérification au moment du del, un component remote
            # ne pourra jamais être del par l'assembly, donc ne pas l'ajouter à la liste est possible
            remote_connection = comp2_name not in self._p_components.keys()
            if not remote_connection:
                self._p_component_connections[comp2_name].add(new_connection)

            # [con] Ajouter la synchronization avec le composant d'en face
            # TODO: réfléchir sur le besoin de la synchronization pour le con: pourquoi attendre que la connection d'en face
            # soit faite, on peut juste lancer les bhvs et s'il n'y a pas de remote dependencies on considère la dépendance
            # non served
            if remote_connection:
                # Need d'initialiser le nombre de user sur la dépendance à 0 car si on veut déconnecter tout de suite,
                # un check est fait sur le nb d'utilisateur
                communication_handler.send_syncing_conn(comp1_name, comp2_name, dep1_name, dep2_name, CONN)
                is_conn_synced = communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, CONN)
                Printer.st_tprint(f"Is conn synced between {comp1_name} and {comp2_name} ? (for {dep1_name} and {dep2_name}): {is_conn_synced}")
                return is_conn_synced
            return True

        else:
            raise Exception("Trying to connect uncompatible dependencies %s.%s and %s.%s" % (
                comp1_name, dep1_name, comp2_name, dep2_name))

    def _compute_dependencies_from_names(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        is_comp1_remote = comp1_name not in self._p_components.keys()
        is_comp2_remote = comp2_name not in self._p_components.keys()
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

    def disconnect(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        instruction = InternalInstruction.build_disconnect(comp1_name, dep1_name, comp2_name, dep2_name)
        self.instruction_num_attribution.attribute_num(instruction)
        self.add_instruction(instruction)

    def _disconnect(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str) -> bool:
        """
        This method adds a connection between two components dependencies.
        Assumption: comp1_name and dep1_name are NOT remote
        :param comp1_name: The name of the first component to connect
        :param dep1_name:  The name of the dependency of the first component to connect
        :param comp2_name: The name of the second component to connect
        :param dep2_name:  The name of the dependency of the second component to connect
        """
        dep1, dep2 = self._compute_dependencies_from_names(comp1_name, dep1_name, comp2_name, dep2_name)
        connection_id = Connection.build_id_from_dependencies(dep1, dep2)
        if connection_id not in self._p_connections:
            result = communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, DECONN)
        else:
            result = self._remove_conn(comp1_name, dep1_name, comp2_name, dep2_name)

        return result

    def _remove_conn(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        dep1, dep2 = self._compute_dependencies_from_names(comp1_name, dep1_name, comp2_name, dep2_name)
        id_connection_to_remove = Connection.build_id_from_dependencies(dep1, dep2)

        if id_connection_to_remove not in self._p_connections.keys():
            raise Exception("Trying to remove unexisting connection from %s.%s to %s.%s" % (
                comp1_name, dep1_name, comp2_name, dep2_name))

        connection: Connection = self._p_connections[id_connection_to_remove]
        if connection.can_remove():
            connection.disconnect()
            self._p_component_connections[comp1_name].discard(connection)

            # self._p_component_connections ne sert qu'à faire une vérification au moment du del, un component remote
            # ne pourra jamais être del par l'assembly, donc ne pas l'ajouter à la liste est possible
            is_remote_disconnection = comp2_name not in self._p_components.keys()
            if not is_remote_disconnection:
                self._p_component_connections[comp2_name].discard(connection)
            del self._p_connections[id_connection_to_remove]

            # [dcon] Ajouter la synchronization avec le composant d'en face
            # TODO: réfléchir sur le besoin de la synchronization pour le dcon, parce qu'une fois que moi je me suis déco,
            # je n'ai pas besoin de savoir si les autres se sont déco (si on suppose un programme valide)
            if is_remote_disconnection:
                communication_handler.send_syncing_conn(comp1_name, comp2_name, dep1_name, dep2_name, DECONN)
                return communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, DECONN)

            return True
        else:
            return False

    def push_b(self, component_name: str, behavior: str):
        instruction = InternalInstruction.build_push_b(component_name, behavior)
        self.instruction_num_attribution.attribute_num(instruction)
        self.add_instruction(instruction)

    def _push_b(self, component_name: str, behavior: str):
        component = self.get_component(component_name)
        component.queue_behavior(behavior)
        if component_name not in self._p_act_components:
            self.add_to_active_components(component_name)
        return True

    def wait(self, component_name: str, wait_for_refusing_provide: bool = False):
        instruction = InternalInstruction.build_wait(component_name, wait_for_refusing_provide)
        self.instruction_num_attribution.attribute_num(instruction)
        self.add_instruction(instruction)

    def _wait(self, component_name: str):
        is_local_component = component_name in self._p_components.keys()
        if is_local_component:
            is_component_idle = component_name not in self._p_act_components

            # Si le component a terminé, on prévient les autres assemblies
            if is_component_idle:
                communication_handler.set_component_state(INACTIVE, component_name, self._p_id_sync)
        else:
            is_component_idle = communication_handler.get_remote_component_state(component_name, self._p_id_sync) == INACTIVE

        return is_component_idle

    def wait_all(self, wait_for_refusing_provide: bool = False):
        instruction = InternalInstruction.build_wait_all(wait_for_refusing_provide)
        self.instruction_num_attribution.attribute_num(instruction)
        self.add_instruction(instruction)

    def _wait_all(self, wait_for_refusing_provide=False):
        all_local_idle = len(self._p_act_components) is 0
        if all_local_idle:
            # TODO: ne pas renvoyer un message quand on se réveille si on l'a déjà fait
            if not wait_for_refusing_provide:
                communication_handler.set_component_state(INACTIVE, self.name, self._p_id_sync)
            all_remote_idle = all(
                communication_handler.get_remote_component_state(assembly_name, self._p_id_sync) == INACTIVE
                for assembly_name in self._remote_assemblies_names
            )
        else:
            all_remote_idle = False

        return all_local_idle and all_remote_idle

    def synchronize(self, debug=False):
        if debug:
            # TODO Remove access to internal queue of instructions_queue (not part of API)
            Printer.st_err_tprint("Synchronizing. %d unfinished tasks:\n- %s (in progress)\n%s\n" % (
                self._p_instructions_queue.unfinished_tasks, str(self._p_current_instruction),
                "\n".join(["- %s" % str(ins) for ins in self._p_instructions_queue.queue])))
        self._p_instructions_queue.join()

    def synchronize_timeout(self, time: int):
        from concerto.utility import timeout
        finished = False
        with timeout(time):
            self.synchronize()
            finished = True

        if finished:
            return True, None
        else:
            return False, self.get_debug_info()

    def is_component_idle(self, component_name: str) -> bool:
        if component_name in self._p_components.keys():
            return component_name not in self._p_act_components
        else:
            return communication_handler.get_remote_component_state(component_name, self._p_id_sync) == INACTIVE

    def get_component(self, name: str) -> Component:
        if name in self._p_components:
            return self._p_components[name]
        else:
            raise (Exception("ERROR - Unknown component %s" % name))

    def get_components(self) -> List[Component]:
        return list(self._p_components.values())

    def thread_safe_report_error(self, component: Component, transition: Transition, error: str):
        report = "Component: %s\nTransition: %s\nError:\n%s" % (component.name, transition._p_name, error)
        self.error_reports.append(report)

    def get_error_reports(self) -> List[str]:
        return self.error_reports

    """
    CHECK ASSEMBLY
    """

    def check_warnings(self):
        """
        This method check WARNINGS in the structure of an assembly.

        :return: false if some WARNINGS have been detected, true otherwise
        """
        check = True
        check_dep = True

        # Check warnings
        for comp in self.get_components():
            check = comp.check_warnings()
            check_dep = comp.check_connections()

        if not check:
            Printer.print(Messages.warning() + "WARNING - some WARNINGS have been "
                                       "detected in your components, please "
                                       "check them so as to not get unwilling "
                                       "behaviors in your deployment cordination"
                  + Messages.endc())

        if not check_dep:
            Printer.print(Messages.warning() + "WARNING - some dependencies are not "
                                       "connected within the assembly. This "
                                       "could lead to unwilling behaviors in "
                                       "your deployment coordination."
                  + Messages.endc())

        return check and check_dep

    """
    OPERATIONAL SEMANTICS
    """

    def is_reconfiguration_finished(self):
        return self._p_instructions_queue.empty() and self._p_current_instruction is None

    def finish_reconfiguration(self):
        Printer.print("---------------------- END OF RECONFIGURATION GG -----------------------")
        Path(f"concerto/finished_reconfigurations/{self._p_id}").touch()  # Create a file that serves as a flag
        exit()

    def loop_smeantics(self):
        while self.alive:
            try:
                if self.is_reconfiguration_finished():
                    self.finish_reconfiguration()
                self.semantics()
            except Exception:
                log.error(traceback.format_exc())

    def semantics(self):
        """
        This method runs one semantics iteration by first consuming the list
        of assembly instructions and then by running semantics of each component
        of the assembly.
        """
        # On commence par exécuter les instructions non bloquantes
        if self._p_current_instruction is not None:
            finished = self._p_current_instruction.apply_to(self)
            if finished:
                if (self._p_current_instruction.type in [InternalInstruction.Type.WAIT, InternalInstruction.Type.WAIT_ALL]
                        and not self._p_current_instruction.args['wait_for_refusing_provide']):
                    # TODO: very ad-hoc solution, to refacto
                    # Consider that it goes from one reconf (deploy) to another (update)
                    self.end_reconf_timer()
                    self._p_id_sync += 1
                    self.start_reconf_timer()
                self._p_current_instruction = None
                self._p_instructions_queue.task_done()
                self._p_nb_instructions_done += 1

        # Consume instructions queue
        while (not self._p_instructions_queue.empty()) and (self._p_current_instruction is None):
            instruction: InternalInstruction = self._p_instructions_queue.get()
            Printer.st_tprint(f"Current instruction: {instruction.type}_{instruction.num}")
            finished = instruction.apply_to(self)
            # Instruction pas finie: wait, waitall
            if finished:
                if instruction.type in [InternalInstruction.Type.WAIT, InternalInstruction.Type.WAIT_ALL] and not instruction.args['wait_for_refusing_provide']:
                    self._p_id_sync += 1
                self._p_instructions_queue.task_done()
                self._p_nb_instructions_done += 1
            else:
                self._p_current_instruction = instruction

        # semantics for each component
        # Dès qu'une instruction est bloquante (e.g. wait, waitall) on exécute
        # les behaviors des composants
        idle_components: Set[str] = set()

        are_active_transitions = False
        all_tokens_blocked = True
        for c in self._p_act_components:
            is_idle, did_something, are_active_transitions = self._p_components[c].semantics()
            if is_idle:
                idle_components.add(c)
            all_tokens_blocked = all_tokens_blocked and (not did_something)

        self.remove_from_active_components(idle_components)

        # Synchrone or asynchrone wait
        # TODO: refacto moment où on log l'endormissement et le end_reconf
        # TODO: voir pour le bug: le end of reconfiguration s'affiche alors que l'assembly est encore en train de tourner (le wait/1/server_assembly est à inactive)
        if self.is_reconfiguration_finished():
            self.end_reconf_timer()
            self.finish_reconfiguration()
        elif self._p_sleep_when_blocked and all_tokens_blocked:
            self.end_reconf_timer()
            assembly_config.save_config(self)
            Printer.st_tprint("Everyone blocked")
            Printer.st_tprint("Going sleeping bye")
            exit()
        elif self.time_manager.is_time_up() and not are_active_transitions:
            self.end_reconf_timer()
            assembly_config.save_config(self)
            Printer.st_tprint("Time's up")
            Printer.st_tprint("Go sleep")
            exit()
        else:
            time.sleep(FREQUENCE_POLLING)

    def is_idle(self) -> bool:
        """
        This method checks if the current reconfiguration is finished

        :return: True if the reconfiguration is finished, False otherwise
        """

        # the deployment cannot be finished if at least all components have
        # not reached a place
        return len(self._p_act_components) == 0
