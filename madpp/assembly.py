#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: assembly
   :synopsis: this file contains the Assembly class.
"""

import sys
from typing import Dict, Tuple, List, Set
from threading import Thread, Lock, Event
from queue import Queue
from madpp.dependency import DepType, Dependency
from madpp.component import Component
from madpp.connection import Connection
from madpp.internal_instruction import InternalInstruction
from madpp.gantt_chart import GanttChart
from madpp.utility import Messages, COLORS, Printer


class Assembly (object):
    """This Assembly class is used to create a assembly.

        An assembly is a set of component instances and the connection of
        their dependencies.
    """



    """
    BUILD ASSEMBLY
    """

    def __init__(self):
        # dict of Component objects: id => object
        self.components : Dict[str, Component] = {}
        # list of connection tuples. A connection tuple is of the form (component1, dependency1,
        # component2, dependency2)
        self.connections : Dict[Tuple[Dependency,Dependency],Connection] = {}

        # a dictionary to store at the assembly level a list of connections for
        # each place (name) of the assembly (ie provide dependencies)
        # this is used to improve performance of the semantics
        self.places_connections : Dict[str,List[Connection]] = {}

        # a dictionary to store at the assembly level a list of connections for
        # each component (name) of the assembly
        # this is used to improve performance of the semantics
        self.component_connections : Dict[str,Set[Connection]] = {}
        
        # Operational semantics
        
        # thread running the semantics of the assembly in a loop
        self.semantics_thread : Thread = Thread(target=self.loop_smeantics)
        self.alive : bool = True
        
        # queue of instructions (synchronized with semantics thread)
        self.instructions_queue = Queue() # thread-safe
        self.current_instruction = None
        
        # set of active components
        self.act_components : Set[str] = set()
        
        self.verbosity : int = 0
        self.print_time : bool = False
        self.dryrun : bool = False
        self.gantt : GanttChart = None
        self.name : str = None
    
    
    def set_verbosity(self, level : int):
        self.verbosity = level
        for c in self.components:
            self.components[c].set_verbosity(level)
        
    def set_print_time(self, value : bool):
        self.print_time = value
        for c in self.components:
            self.components[c].set_print_time(value)
    
    def set_dryrun(self, value : int):
        self.dryrun = value
        for c in self.components:
            self.components[c].set_dryrun(value)
            
    def set_use_gantt_chart(self, value : bool):
        if value:
            if self.gantt is None:
                self.gantt = GanttChart()
                for c in self.components:
                    self.components[c].set_gantt_chart(self.gantt)
        else:
            self.gantt = None
            for c in self.components:
                self.components[c].set_gantt_chart(None)
        
    def get_gantt_chart(self):
        return self.gantt
            
    def set_name(self, name : str):
        self.name = name
    
    def get_name(self) -> str:
        return self.name
    
    def get_debug_info(self) -> str:
        debug_info = "Inactive components:\n"
        for component_name in self.components:
            if component_name not in self.act_components:
                debug_info += "- %s: %s\n"%(component_name, ','.join(self.components[component_name].get_active_places()))
        debug_info += "Active components:\n"
        for component_name in self.act_components:
            debug_info += self.components[component_name].get_debug_info()
        return debug_info
    
    def terminate(self, debug=False):
        if debug:
            Printer.st_err_tprint("DEBUG terminate:\n%s"%self.get_debug_info())
        for component_name in self.act_components:
            self.wait(component_name)
            if debug:
                Printer.st_err_tprint("DEBUG terminate: waiting component '%s'"%component_name)
        self.synchronize()
        self.alive = False
        self.semantics_thread.join()
    
    def force_terminate(self):
        self.synchronize()
        self.alive = False
        self.semantics_thread.join()
    
    def print(self, string : str):
        if self.verbosity < 0:
            return
        if self.name is None:
            name = "Assembly"
        else:
            name = self.name
        message : str = "[%s] %s"%(name, string)
        if self.print_time:
            Printer.st_tprint(message)
        else:
            print(message)
    
    
    def add_instruction(self, instruction : InternalInstruction):
        self.instructions_queue.put(instruction)
        if not self.semantics_thread.is_alive():
            self.semantics_thread.start()


    def add_component(self, name : str, comp : Component):
        self.add_instruction(InternalInstruction.build_add(name,comp))

    def _add(self, name : str, comp : Component) -> bool:
        """
        This method adds a component instance to the assembly

        :param comp: the component instance to add
        """
        if name in self.components:
            raise Exception("Trying to add '%s' as a component while it is already a component"%name)
        comp.set_name(name)
        comp.set_color(COLORS[len(self.components)%len(COLORS)])
        comp.set_verbosity(self.verbosity)
        comp.set_print_time(self.print_time)
        comp.set_dryrun(self.dryrun)
        comp.set_gantt_chart(self.gantt)
        self.components[name]=comp
        self.component_connections[name] = set()
        self.act_components.add(name) # _init
        return True
        
    
    def del_component(self, component_name : str):
        self.add_instruction(InternalInstruction.build_del(component_name))
    
    def _del(self, component_name : str) -> bool:
        if component_name in self.act_components:
            return False
        if len(self.component_connections[component_name]) > 0:
            return False
        del self.component_connections[component_name]
        del self.components[component_name]
        return True


    def connect(self, comp1_name : str, dep1_name : str, comp2_name : str, dep2_name : str):
        self.add_instruction(InternalInstruction.build_connect(comp1_name,dep1_name,comp2_name,dep2_name))

    def _connect(self, comp1_name : str, dep1_name : str, comp2_name : str, dep2_name : str) -> bool:
        """
        This method adds a connection between two components dependencies.

        :param comp1_name: The name of the first component to connect
        :param dep1_name:  The name of the dependency of the first component to connect
        :param comp2_name: The name of the second component to connect
        :param dep2_name:  The name of the dependency of the second component to connect
        """
        
        comp1 = self.get_component(comp1_name)
        comp2 = self.get_component(comp2_name)
        
        dep1 = comp1.get_dependency(dep1_name)
        dep2 = comp2.get_dependency(dep2_name)
        
        if DepType.valid_types(dep1.get_type(),
                              dep2.get_type()):
            # multiple connections are possible within MAD, so we do not
            # check if a dependency is already connected

            # create connection
            new_connection = Connection(dep1, dep2)
            
            provide_dep = new_connection.get_provide_dep()
            use_dep = new_connection.get_use_dep()
            
            if (provide_dep, use_dep) in self.connections:
                raise Exception("Trying to add already existing connection from %s.%s to %s.%s"%(comp1_name, dep1_name, comp2_name, dep2_name))
            
            self.connections[(provide_dep, use_dep)] = new_connection
            self.component_connections[comp1_name].add(new_connection)
            self.component_connections[comp2_name].add(new_connection)

            return True

        else:
            raise Exception("Trying to connect uncompatible dependencies %s.%s and %s.%s"%(comp1_name, dep1_name, comp2_name, dep2_name))


    def disconnect(self, comp1_name : str, dep1_name : str, comp2_name : str, dep2_name : str):
        self.add_instruction(InternalInstruction.build_disconnect(comp1_name,dep1_name,comp2_name,dep2_name))

    def _disconnect(self, comp1_name : str, dep1_name : str, comp2_name : str, dep2_name : str) -> bool:
        """
        This method adds a connection between two components dependencies.

        :param comp1_name: The name of the first component to connect
        :param dep1_name:  The name of the dependency of the first component to connect
        :param comp2_name: The name of the second component to connect
        :param dep2_name:  The name of the dependency of the second component to connect
        """
        
        comp1 = self.get_component(comp1_name)
        comp2 = self.get_component(comp2_name)
        
        dep1 = comp1.get_dependency(dep1_name)
        dep2 = comp2.get_dependency(dep2_name)
        
        dep1type = dep1.get_type()
        if dep1type == DepType.PROVIDE or dep1type == DepType.DATA_PROVIDE:
            provide_dep = dep1
            use_dep = dep2
        else:
            provide_dep = dep2
            use_dep = dep1
            
        if (provide_dep, use_dep) not in self.connections:
            raise Exception("Trying to remove unexisting connection from %s.%s to %s.%s"%(comp1_name, dep1_name, comp2_name, dep2_name))
        
        connection : Connection = self.connections[(provide_dep, use_dep)]
        if connection.can_remove():
            connection.disconnect()
            self.component_connections[comp1_name].discard(connection)
            self.component_connections[comp2_name].discard(connection)
            del self.connections[(provide_dep, use_dep)]
            return True
        else:
            return False
        
    
    def change_behavior(self, component_name : str, behavior : str):
        self.add_instruction(InternalInstruction.build_change_behavior(component_name, behavior))
            
    def _change_behavior(self, component_name : str, behavior : str):
        component = self.get_component(component_name)
        component.queue_behavior(behavior)
        if component_name not in self.act_components:
            self.act_components.add(component_name)
        return True
        
    
    def wait(self, component_name : str):
        self.add_instruction(InternalInstruction.build_wait(component_name))
    
    def _wait(self, component_name : str):
        return self.is_component_idle(component_name)
        
    
    def wait_all(self):
        self.add_instruction(InternalInstruction.build_wait_all())
    
    def _wait_all(self):
        return len(self.act_components) is 0


    def synchronize(self):
        self.instructions_queue.join()
    
    
    def is_component_idle(self, component_name : str) -> bool:
        return (not component_name in self.act_components)
        

    def get_component(self, name : str) -> Component:
        if name in self.components:
            return self.components[name]
        else:
            raise(Exception("ERROR - Unknown component %s"%name))


    def get_components(self) -> List[Component]:
        return list(self.components.values())

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
        
        if self.current_instruction is not None:
            finished = self.current_instruction.apply_to(self)
            if finished:
                self.current_instruction = None
                self.instructions_queue.task_done()
            
        # Consume instructions queue
        while (not self.instructions_queue.empty()) and (self.current_instruction is None):
            instruction : InternalInstruction = self.instructions_queue.get()
            finished = instruction.apply_to(self)
            if finished:
                self.instructions_queue.task_done()
            else:
                self.current_instruction = instruction
        

        # semantics for each component
        idle_components : Set[str] = set()
        
        for c in self.act_components:
            is_idle = self.components[c].semantics()
            if is_idle:
                idle_components.add(c)
        
        self.act_components.difference_update(idle_components)
        

    def is_idle(self) -> bool:
        """
        This method checks if the current reconfiguration is finished

        :return: True if the reconfiguration is finished, False otherwise
        """

        # the deployment cannot be finished if at least all components have
        # not reached a place
        return len(self.act_components) == 0

