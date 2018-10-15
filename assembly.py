#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: assembly
   :synopsis: this file contains the Assembly class.
"""

import sys
from typing import Dict, Tuple, List, Set
from threading import Thread, Lock, Event
from copy import deepcopy
from whiteboard import *
from dependency import *
from component import *
from utility import Messages, COLORS, remove_if

class Connection(object):
    """
    This class is used by the assembly to store connections between components
    """

    def __init__(self, comp1 : Component, dep1 : Dependency, comp2 : Component, dep2 : Dependency):
        self.active = False
        self.tuple = (comp1, dep1, comp2, dep2)
        self.names = (comp1.get_name(), dep1.get_name(), comp2.get_name(),
                          dep2.get_name())

    def activate(self):
        self.active = True

    def gettuple(self):
        return self.tuple

    def get_names(self):
        return self.names

    def isactive(self):
        return self.active

class Assembly (object):
    """This Assembly class is used to create a assembly.

        An assembly is a set of component instances and the connection of
        their dependencies.
    """



    """
    BUILD ASSEMBLY
    """

    def __init__(self):
        self.printed = False
        # dict of Component objects: id => object
        self.components : Dict[str, Component] = {}
        # list of connection tuples. A connection tuple is of the form (component1, dependency1,
        # component2, dependency2)
        self.connections : List[Tuple[Component,Dependency,Component,Dependency]] = []

        # list of white boards, 1 for each data provide
        self.wbs : Dict[Dependency, WhiteBoard] = {}

        # a dictionary to store at the assembly level a list of connections for
        # each place (name) of the assembly (ie provide dependencies)
        # this is used to improve performance of the semantics
        self.places_connections = {}

        # a dictionary to store at the assembly level a list of connections for
        # each component (name) of the assembly
        # this is used to improve performance of the semantics
        self.component_connections = {}
        
        # Operational semantics
        
        # thread running the semantics of the assembly in a loop
        self.semantics_thread = Thread(target=self.loop_smeantics)
        self.activate_component_lock : Lock = Lock()
        
        # dictionary active Component objects (with a behavior) -> event in case of wait
        self.act_components : Dict[str,Event] = {}
        #set of newly active Component objects (to initialize them)
        self.new_act_components : Set[str] = set()

        # a set of active places and connections within the assembly (global)
        self.act_places = []
        self.act_connections = []
        # set of active places and connections of the previous iteration
        self.old_places = []
        self.old_connections = []

    def add_component(self, name : str, comp : Component):
        """
        This method adds a component instance to the assembly

        :param comp: the component instance to add
        """
        comp.set_name(name)
        comp.set_color(COLORS[len(self.components)%len(COLORS)])
        self.component_connections[name] = []
        if name not in self.components:
            self.components[name]=comp
        else:
            print(Messages.fail() + "ERROR - Already instantiate component "+name +
                  + Messages.endc())
            sys.exit(0)

    def connect(self, comp1_name : str, dep1_name : str, comp2_name : str, dep2_name : str):
        """
        This method adds a connection between two components dependencies.

        :param comp1_name: The name of the first component to connect
        :param dep1_name:  The name of the dependency of the first component to connect
        :param comp2_name: The name of the second component to connect
        :param dep2_name:  The name of the dependency of the second component to connect
        """
        
        comp1 = self.get_component(comp1_name)
        comp2 = self.get_component(comp2_name)
        dep1 = comp1.st_dependencies[dep1_name]
        dep2 = comp2.st_dependencies[dep2_name]
        
        if DepType.valid_types(dep1.get_type(),
                              dep2.get_type()):
            # multiple connections are possible within MAD, so we do not
            # check if a dependency is already connected

            # create connection
            new_connection = Connection(comp1, dep1, comp2,
                                        dep2)
            self.connections.append(new_connection.gettuple())

            # fill component_connections
            if comp1.get_name() in self.component_connections:
                self.component_connections[comp1.get_name()].append(new_connection)
            else:
                self.component_connections[comp1.get_name()] = [new_connection]
            if comp2.get_name() in self.component_connections:
                self.component_connections[comp2.get_name()].append(new_connection)
            else:
                self.component_connections[comp2.get_name()] = [new_connection]

            # fill places_connections
            if dep1.get_type() == DepType.PROVIDE or \
               dep1.get_type() == DepType.DATA_PROVIDE:
                for binding in dep1.get_bindings():
                    if binding in self.places_connections:
                        self.places_connections[binding].append(new_connection)
                    else:
                        self.places_connections[binding] = [new_connection]
            elif dep2.get_type() == DepType.PROVIDE or \
               dep2.get_type() == DepType.DATA_PROVIDE:
                for binding in dep2.get_bindings():
                    if binding in self.places_connections:
                        self.places_connections[binding].append(new_connection)
                    else:
                        self.places_connections[binding] = [new_connection]

            # white board management
            # if we have a DATA connection, create a whiteboard and attached it
            if (dep1.get_type() == DepType.DATA_PROVIDE) \
                or (dep1.get_type() == DepType.DATA_USE):
                # get user and provider of the connection
                if dep1.get_type() == DepType.DATA_PROVIDE:
                    provider = dep1
                    user = dep2
                else:
                    provider = dep2
                    user = dep1
                self.wbs[provider] = provider.get_wb()
                user.set_wb(self.wbs[provider])
            # else we have a service connection to connect
            else:
                dep1.connect()
                dep2.connect()

        else:
            print(Messages.fail() + "ERROR - you try to connect dependencies "
                                 "with incompatible types. DepType.USE and "
                                  "DepType.DATA-USE should be respectively "
                                  "connected to DepType.PROVIDE and "
                                  "DepType.DATA-PROVIDE dependencies."
                  + Messages.endc())
            sys.exit(0)

    def disconnect(self, comp1_name : str, dep1_name : str, comp2_name : str, dep2_name : str):
        """
        This method adds a connection between two components dependencies.

        :param comp1_name: The name of the first component to connect
        :param dep1_name:  The name of the dependency of the first component to connect
        :param comp2_name: The name of the second component to connect
        :param dep2_name:  The name of the dependency of the second component to connect
        """
        
        #TODO: Check that it is not breaking any active behavior
        
        comp1 = self.get_component(comp1_name)
        comp2 = self.get_component(comp2_name)
        dep1 = comp1.st_dependencies[dep1_name]
        dep2 = comp2.st_dependencies[dep2_name]
        
        is_connection_tuple = \
            lambda e : e == (comp1, dep1, comp2, dep2)
        remove_if(self.connections, is_connection_tuple)
        
        is_connection = \
            lambda e : e.gettuple() == (comp1, dep1, comp2, dep2)
        remove_if(self.component_connections[comp1.get_name()], is_connection)
        remove_if(self.component_connections[comp2.get_name()], is_connection)

        # fill places_connections
        if dep1.get_type() == DepType.PROVIDE or \
            dep1.get_type() == DepType.DATA_PROVIDE:
            for binding in dep1.get_bindings():
                remove_if(self.places_connections[binding], is_connection)
        elif dep2.get_type() == DepType.PROVIDE or \
            dep2.get_type() == DepType.DATA_PROVIDE:
            for binding in dep2.get_bindings():
                remove_if(self.places_connections[binding], is_connection)

        dep1.disconnect()
        dep2.disconnect()
    
    def is_component_idle(self, component_name):
        if component_name in self.act_behaviors:
            if self.act_behaviors[component_name].is_alive():
                return False
            else:
                del self.act_behaviors[component_name]
        return True
            
    def change_behavior(self, component_name : str, behavior : str):
        component = self.get_component(component_name)
        self.activate_component_lock.acquire()
        try:
            if component_name in self.act_components:
                raise Exception("Error: trying to change the behavior of component %s to %s while it is still running behavior %s"%(component_name, behavior, component.get_active_behavior()))
                #TODO Maybe wait? To decide
            component.set_behavior(behavior)
            # Create a new thread for the behavior, ready to join in case of wait
            self.act_components[component_name] = Event()
            self.new_act_components.add(component_name)
        finally:
            self.activate_component_lock.release()
        if not self.semantics_thread.is_alive():
            self.semantics_thread.start()
        
    
    def wait(self, component_name):
        self.activate_component_lock.acquire()
        event = None
        try:
            if component_name not in self.act_components or self.act_components[component_name].is_set():
                return
            event = self.act_components[component_name]
        finally:
            self.activate_component_lock.release()
        event.wait()
        

    def get_component(self, name : str) -> Component:
        if name in self.components:
            return self.components[name]
        else:
            raise(Exception("ERROR - Unknown component %s"%name))

    def get_components(self):
        return self.components.values()

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
    
    def loop_smeantics(self, dryrun=False, printing=False):
        while True:
            self.semantics(dryrun, printing)

    def init_semantics(self):
        """
        This method activate the initial places of each component and builds
        the global self.act_places
        """
        for c in self.new_act_components:
            comp_places = self.components[c].init(
                self.component_connections[c])
            self.act_places.extend(comp_places)
        self.new_act_components.clear()

    def semantics(self, dryrun : bool, printing : bool):
        """
        This method runs one semantics iteration by first updating the list
        of enbled connections and then by running semantics of each component
        of the assembly.
        :param dryrun: boolean representing if the semantics is run in dryrun mode
        :param printing: boolean representing if the semantics must print output
        """
        
        active_components = []
        self.activate_component_lock.acquire()
        try:
            self.init_semantics()
            active_components = deepcopy(list(self.act_components.keys()))
        finally:
            self.activate_component_lock.release()
        
        
        # enable / disable connections
        if self.act_places != self.old_places:
            # enable/disable connections
            new_connections = self.disable_enable_connections(printing)
            # highest priority according to the model to guarantee the
            # disconnection of services when no more provided
            # before doing anything else
            self.old_connections = self.act_connections.copy()
            self.act_connections = new_connections.copy()

        # semantics for each component
        new_places = []
        for c in active_components:
            connections = []
            if c in self.component_connections:
                for conn in self.component_connections[c]:
                    if conn.isactive():
                        connections.append(conn.gettuple())

            c_places = self.components[c].semantics(connections, dryrun, printing)
            new_places = new_places + c_places

        # build the new configuration / ended
        self.old_places = self.act_places.copy()
        self.act_places = new_places.copy()
        
        idle_components = []
        for c in active_components:
            if self.components[c].is_idle():
                idle_components.append(c)
                
        self.activate_component_lock.acquire()
        try:
            for c in idle_components:
                self.act_components[c].set()
                del self.act_components[c]
                self.components[c].set_behavior(None)
        finally:
            self.activate_component_lock.release()
        
        


    def disable_enable_connections(self, printing : bool):
        """
        This method build the new list of enabled connections according to
        the current states of "activated" places (ie the ones getting a token).

        :param configuration: the current configuration of the deployment
        :return: the new list of activated connections
        """

        # create the new list of activated connections
        activated_connections = []

        for place in self.act_places:
            if place in self.places_connections:
                connections = self.places_connections[place]
                for conn in connections:
                    activated_connections.append(conn.gettuple())
                    if not conn.isactive():
                        conn.activate()
                        if printing:
                            print("[Assembly] Enable connection ("
                                  + str(conn.get_names()) + ")")

        return activated_connections

    def is_idle(self):
        """
        This method checks if the current reconfiguration is finished

        :return: True if the reconfiguration is finished, False otherwise
        """

        # the deployment cannot be finished if at least all components have
        # not reached a place
        if len(self.act_places) >= len(self.components):
            # if all places are finals (ie without output docks) the
            # deployment has finished
            all_finals = True
            for place in self.act_places:
                if len(place.get_output_docks()) > 0:
                    all_finals = False
            return all_finals
        else:
            return False

