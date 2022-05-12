#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: assembly
   :synopsis: this file contains the Assembly class.
"""

import sys
from typing import Dict, Tuple, List, Set, Optional
from threading import Thread
from queue import Queue

from concerto import communication_handler
from concerto.communication_handler import CONN, DECONN, ACTIVE, INACTIVE
from concerto.dependency import DepType, Dependency
from concerto.component import Component
from concerto.proxy_dependency import ProxyDependency
from concerto.transition import Transition
from concerto.connection import Connection
from concerto.internal_instruction import InternalInstruction
from concerto.reconfiguration import Reconfiguration
from concerto.gantt_record import GanttRecord
from concerto.utility import Messages, COLORS, Printer


class Assembly(object):
    """This Assembly class is used to create a assembly.

        An assembly is a set of component instances and the connection of
        their dependencies.
    """

    """
    BUILD ASSEMBLY
    """

    def __init__(self):
        # dict of Component objects: id => object
        self._components: Dict[str, Component] = {}
        # list of connection tuples. A connection tuple is of the form (component1, dependency1,
        # component2, dependency2)
        # TODO [con] Uniquement pour la vérification, donc pas besoin des infos
        # d'en face.
        self._connections: Dict[Tuple[Dependency, Dependency], Connection] = {}

        self._remote_components_names: Set[str] = set()

        # a dictionary to store at the assembly level a list of connections for
        # each place (name) of the assembly (ie provide dependencies)
        # this is used to improve performance of the semantics
        # TODO [con] Pas utilisé
        self.places_connections: Dict[str, List[Connection]] = {}

        # a dictionary to store at the assembly level a list of connections for
        # each component (name) of the assembly
        # this is used to improve performance of the semantics
        # TODO [con] Uniquement pour la vérification, donc pas besoin des infos
        # d'en face.
        self.component_connections: Dict[str, Set[Connection]] = {}

        # Operational semantics

        # thread running the semantics of the assembly in a loop
        self.semantics_thread: Thread = Thread(target=self.loop_smeantics)
        self.alive: bool = True

        # queue of instructions (synchronized with semantics thread)
        self.instructions_queue = Queue()  # thread-safe
        self.current_instruction = None

        # set of active components
        self.act_components: Set[str] = set()

        self.verbosity: int = 0
        self.print_time: bool = False
        self.dryrun: bool = False
        self.gantt: Optional[GanttRecord] = None
        self.name: Optional[str] = None

        self.dump_program: bool = False
        self.program_str: str = ""

        self.error_reports: List[str] = []

    def set_verbosity(self, level: int):
        self.verbosity = level
        for c in self._components:
            self._components[c].set_verbosity(level)

    def set_print_time(self, value: bool):
        self.print_time = value
        for c in self._components:
            self._components[c].set_print_time(value)

    def set_dryrun(self, value: bool):
        self.dryrun = value
        for c in self._components:
            self._components[c].set_dryrun(value)

    def set_record_gantt(self, value: bool):
        if value:
            if self.gantt is None:
                self.gantt = GanttRecord()
                for c in self._components:
                    self._components[c].set_gantt_record(self.gantt)
        else:
            self.gantt = None
            for c in self._components:
                self._components[c].set_gantt_record(None)

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
        for component_name in self._components:
            if component_name not in self.act_components:
                debug_info += "- %s: %s\n" % (
                    component_name, ','.join(self._components[component_name].get_active_places()))
        debug_info += "Active components:\n"
        for component_name in self.act_components:
            debug_info += self._components[component_name].get_debug_info()
        return debug_info

    def terminate(self, debug=False):
        # TODO Est censé attendre également les autres assemblies ?
        if debug:
            Printer.st_err_tprint("DEBUG terminate:\n%s" % self.get_debug_info())
        for component_name in self.act_components:
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
            print(message)

    def add_instruction(self, instruction: InternalInstruction):
        if self.dump_program:
            self.program_str += (str(instruction) + "\n")

        self.instructions_queue.put(instruction)
        if not self.semantics_thread.is_alive():
            self.semantics_thread.start()

    def run_reconfiguration(self, reconfiguration: Reconfiguration):
        for instr in reconfiguration._get_instructions():
            self.add_instruction(instr)

    def add_to_active_components(self, component_name: str):
        # TODO: voir si on ajoute TOUS les components ou seulement une partie
        self.act_components.add(component_name)
        communication_handler.set_component_state(ACTIVE, component_name)

    def remove_from_active_components(self, idle_components: Set[str]):
        self.act_components.difference_update(idle_components)
        for component_name in idle_components:
            communication_handler.set_component_state(INACTIVE, component_name)

    def add_component(self, name: str, comp: Component):
        self.add_instruction(InternalInstruction.build_add(name, comp))

    def _add(self, name: str, comp: Component) -> bool:
        """
        This method adds a component instance to the assembly

        :param comp: the component instance to add
        """
        if name in self._components:
            raise Exception("Trying to add '%s' as a component while it is already a component" % name)
        comp.set_name(name)
        comp.set_color(COLORS[len(self._components) % len(COLORS)])
        comp.set_verbosity(self.verbosity)
        comp.set_print_time(self.print_time)
        comp.set_dryrun(self.dryrun)
        comp.set_gantt_record(self.gantt)
        comp.set_assembly(self)
        self._components[name] = comp
        self.component_connections[name] = set()
        self.add_to_active_components(name)  # _init
        return True

    def del_component(self, component_name: str):
        self.add_instruction(InternalInstruction.build_del(component_name))

    def _del(self, component_name: str) -> bool:
        if component_name in self.act_components:
            return False
        if len(self.component_connections[component_name]) > 0:
            return False
        del self.component_connections[component_name]
        del self._components[component_name]
        return True

    def connect(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        self.add_instruction(InternalInstruction.build_connect(comp1_name, dep1_name, comp2_name, dep2_name))

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

        comp1 = self.get_component(comp1_name)
        dep1 = comp1.get_dependency(dep1_name)

        remote_connection = comp2_name not in self._components.keys()
        if remote_connection:
            dep2_type = DepType.compute_opposite_type(dep1.get_type()) # TODO: assumption sur le fait que la dependency d'en face est forcément la stricte opposée
            dep2 = ProxyDependency(comp2_name, dep2_name, dep2_type)  # TODO [con, dcon]: la stocker pour le dcon ?
        else:
            comp2 = self.get_component(comp2_name)
            dep2 = comp2.get_dependency(dep2_name)

        if DepType.valid_types(dep1.get_type(),
                               dep2.get_type()):
            # multiple connections are possible within MAD, so we do not
            # check if a dependency is already connected

            # create connection
            new_connection = Connection(dep1, dep2)

            provide_dep = new_connection.get_provide_dep()
            use_dep = new_connection.get_use_dep()

            if (provide_dep, use_dep) in self._connections:
                raise Exception("Trying to add already existing connection from %s.%s to %s.%s" % (
                    comp1_name, dep1_name, comp2_name, dep2_name))

            self._connections[(provide_dep, use_dep)] = new_connection
            self.component_connections[comp1_name].add(new_connection)

            # self.component_connections ne sert qu'à faire une vérification au moment du del, un component remote
            # ne pourra jamais être del par l'assembly, donc ne pas l'ajouter à la liste est possible
            if not remote_connection:
                self.component_connections[comp2_name].add(new_connection)

            # [con] Ajouter la synchronization avec le composant d'en face
            # TODO: réfléchir sur le besoin de la synchronization pour le con
            if remote_connection:
                # TODO A discuter: ajouter les remotes components moins tardivement qu'au moment de la connexion
                # Et quand les enlever
                self._remote_components_names.add(comp2_name)

                # Need d'initialiser le nombre de user sur la dépendance à 0 car si on veut déconnecter tout de suite,
                # un check est fait sur le nb d'utilisateur
                # TODO [dcon] voir si c'est pas mieux de faire un check sur si le topic a une valeur nulle
                communication_handler.send_nb_dependency_users(0, comp1_name, dep1_name)
                communication_handler.send_syncing_conn(comp1_name, comp2_name, dep1_name, dep2_name, CONN)
                Printer.st_tprint(f"{self.name} : Waiting CONN message from {comp2_name}")
                communication_handler.wait_conn_to_sync(comp1_name, comp2_name, dep2_name, dep1_name, CONN)
                Printer.st_tprint(f"{self.name} : RECEIVED CONN message from {comp2_name}")

            return True

        else:
            raise Exception("Trying to connect uncompatible dependencies %s.%s and %s.%s" % (
                comp1_name, dep1_name, comp2_name, dep2_name))

    def disconnect(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str):
        self.add_instruction(InternalInstruction.build_disconnect(comp1_name, dep1_name, comp2_name, dep2_name))

    def _disconnect(self, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str) -> bool:
        """
        This method adds a connection between two components dependencies.
        Assumption: comp1_name and dep1_name are NOT remote
        :param comp1_name: The name of the first component to connect
        :param dep1_name:  The name of the dependency of the first component to connect
        :param comp2_name: The name of the second component to connect
        :param dep2_name:  The name of the dependency of the second component to connect
        """
        comp1 = self.get_component(comp1_name)
        dep1 = comp1.get_dependency(dep1_name)

        remote_disconnection = comp2_name not in self._components.keys()
        if remote_disconnection:
            dep2_type = DepType.compute_opposite_type(dep1.get_type())
            dep2 = ProxyDependency(comp2_name, dep2_name, dep2_type)
        else:
            comp2 = self.get_component(comp2_name)
            dep2 = comp2.get_dependency(dep2_name)

        dep1type = dep1.get_type()
        if dep1type == DepType.PROVIDE or dep1type == DepType.DATA_PROVIDE:
            provide_dep = dep1
            use_dep = dep2
        else:
            provide_dep = dep2
            use_dep = dep1

        if (provide_dep, use_dep) not in self._connections:
            raise Exception("Trying to remove unexisting connection from %s.%s to %s.%s" % (
                comp1_name, dep1_name, comp2_name, dep2_name))

        connection: Connection = self._connections[(provide_dep, use_dep)]
        if connection.can_remove():
            connection.disconnect()  # TODO [dcon] pertinent d'ajouter une liste de connexions au ProxyDependency ?
            self.component_connections[comp1_name].discard(connection)

            # self.component_connections ne sert qu'à faire une vérification au moment du del, un component remote
            # ne pourra jamais être del par l'assembly, donc ne pas l'ajouter à la liste est possible
            if not remote_disconnection:
                self.component_connections[comp2_name].discard(connection)
            del self._connections[(provide_dep, use_dep)]

            # [dcon] Ajouter la synchronization avec le composant d'en face
            # TODO: réfléchir sur le besoin de la synchronization pour le dcon
            if remote_disconnection:
                communication_handler.send_syncing_conn(comp1_name, comp2_name, dep1_name, dep2_name, DECONN)
                Printer.st_tprint(f"{self.name} : Waiting DECONN message from {comp2_name}")
                communication_handler.wait_conn_to_sync(comp1_name, comp2_name, dep2_name, dep1_name, DECONN)
                Printer.st_tprint(f"{self.name} : RECEIVED DECONN message from {comp2_name}")

            return True
        else:
            return False

    def push_b(self, component_name: str, behavior: str):
        self.add_instruction(InternalInstruction.build_push_b(component_name, behavior))

    def _push_b(self, component_name: str, behavior: str):
        component = self.get_component(component_name)
        component.queue_behavior(behavior)
        if component_name not in self.act_components:
            self.add_to_active_components(component_name)
        return True

    def wait(self, component_name: str):
        self.add_instruction(InternalInstruction.build_wait(component_name))

    def _wait(self, component_name: str):
        # TODO [wait] Si on doit wait un component remote:
        # - Soit on remplace la fonction par des zenoh.get successifs
        # - Soit on met en place un subscribe (à voir comment et où)
        # - Soit on change le fonctionnement de la fonction semantics()
        return self.is_component_idle(component_name)

    def wait_all(self):
        self.add_instruction(InternalInstruction.build_wait_all())

    def _wait_all(self):
        # Wait remotes
        all_remotes_are_idles = True
        for comp_name in self._remote_components_names:
            if not self.is_component_idle(comp_name):
                all_remotes_are_idles = False

        return len(self.act_components) is 0 and all_remotes_are_idles

    def synchronize(self, debug=False):
        # TODO: aims to also synchronize with other assemblies ?
        if debug:
            # TODO Remove access to internal queue of instructions_queue (not part of API)
            Printer.st_err_tprint("Synchronizing. %d unfinished tasks:\n- %s (in progress)\n%s\n" % (
                self.instructions_queue.unfinished_tasks, str(self.current_instruction),
                "\n".join(["- %s" % str(ins) for ins in self.instructions_queue.queue])))
        self.instructions_queue.join()

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
        if component_name in self._components.keys():
            return component_name not in self.act_components
        else:
            return communication_handler.get_remote_component_state(component_name)

    def get_component(self, name: str) -> Component:
        if name in self._components:
            return self._components[name]
        else:
            raise (Exception("ERROR - Unknown component %s" % name))

    def get_components(self) -> List[Component]:
        return list(self._components.values())

    def thread_safe_report_error(self, component: Component, transition: Transition, error: str):
        report = "Component: %s\nTransition: %s\nError:\n%s" % (component.name, transition.name, error)
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
            print(Messages.warning() + "WARNING - some WARNINGS have been "
                                       "detected in your components, please "
                                       "check them so as to not get unwilling "
                                       "behaviors in your deployment cordination"
                  + Messages.endc())

        if not check_dep:
            print(Messages.warning() + "WARNING - some dependencies are not "
                                       "connected within the assembly. This "
                                       "could lead to unwilling behaviors in "
                                       "your deployment coordination."
                  + Messages.endc())

        return check and check_dep

    """
    OPERATIONAL SEMANTICS
    """

    def loop_smeantics(self):
        while self.alive:
            self.semantics()

    def semantics(self):
        """
        This method runs one semantics iteration by first consuming the list
        of assembly instructions and then by running semantics of each component
        of the assembly.
        """
        # On commence par exécuter les instructions non bloquantes
        if self.current_instruction is not None:
            finished = self.current_instruction.apply_to(self)
            if finished:
                self.current_instruction = None
                self.instructions_queue.task_done()

        # Consume instructions queue
        while (not self.instructions_queue.empty()) and (self.current_instruction is None):
            instruction: InternalInstruction = self.instructions_queue.get()
            finished = instruction.apply_to(self)
            # Instruction pas finie: wait, waitall
            if finished:
                self.instructions_queue.task_done()
            else:
                self.current_instruction = instruction

        # semantics for each component
        # Dès qu'une instruction est bloquante (e.g. wait, waitall) on exécute
        # les behaviors des composants
        idle_components: Set[str] = set()

        for c in self.act_components:
            is_idle = self._components[c].semantics()
            if is_idle:
                idle_components.add(c)

        self.remove_from_active_components(idle_components)

    def is_idle(self) -> bool:
        """
        This method checks if the current reconfiguration is finished

        :return: True if the reconfiguration is finished, False otherwise
        """

        # the deployment cannot be finished if at least all components have
        # not reached a place
        return len(self.act_components) == 0
