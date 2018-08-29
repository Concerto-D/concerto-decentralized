#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: assembly
   :synopsis: this file contains the Assembly class.
"""

import sys
from whiteboard import *
from dependency import *
from utility import Messages, COLORS

class Connection(object):
    """
    This class is used by the assembly to store connections between components
    """

    def __init__(self, comp1, dep1, comp2, dep2):
        self.active = False
        self.tuple = (comp1, dep1, comp2, dep2)
        self.names = (comp1.getname(), dep1.getname(), comp2.getname(),
                          dep2.getname())

    def activate(self):
        self.active = True

    def gettuple(self):
        return self.tuple

    def getnames(self):
        return self.names

    def isactive(self):
        return self.active

class Assembly (object):
    """This Assembly class is used to create a assembly.

        An assembly is a set of component instances and the connection of
        their dependencies.
    """

    # dict of Component objects: id => object
    components = {}

    # list of connections. A connection is a tuple (component1, dependency1,
    # component2, dependency2)
    connections = []

    # list of white boards, 1 for each data provide
    wbs = {}

    # a dictionary to store at the assembly level a list of connections for
    # each place (name) of the assembly (ie provide dependencies)
    # this is used to improve performance of the semantics
    places_connections = {}

    # a dictionary to store at the assembly level a list of connections for
    # each component (name) of the assembly
    # this is used to improve performance of the semantics
    component_connections = {}

    """
    BUILD ASSEMBLY
    """

    def __init__(self):
        self.printed = False

    def addComponent(self, name, comp):
        """
        This method adds a component instance to the assembly

        :param comp: the component instance to add
        """
        comp.setname(name)
        comp.setcolor(COLORS[len(self.components)%len(COLORS)])
        if name not in self.components:
            self.components[name]=comp
        else:
            print(Messages.fail() + "ERROR - Already instantiate component "+name +
                  + Messages.endc())
            sys.exit(0)

    def addConnection(self, comp1, name1, comp2, name2):
        """
        This method adds a connection between two components dependencies.

        :param comp1: The first component to connect
        :param name1: The dependency name of the first component to connect
        :param comp2: The second component to connect
        :param name2: The dependency name of the second component to connect
        """
        if DepType.validtypes(comp1.st_dependencies[name1].gettype(),
                              comp2.st_dependencies[name2].gettype()):
            # multiple connections are possible within MAD, so we do not
            # check if a dependency is already connected

            # create connection
            new_connection = Connection(comp1, comp1.st_dependencies[name1], comp2,
                                        comp2.st_dependencies[name2])
            self.connections.append(new_connection.gettuple())

            # fill component_connections
            if comp1.getname() in self.component_connections:
                self.component_connections[comp1.getname()].append(new_connection)
            else:
                self.component_connections[comp1.getname()] = [new_connection]
            if comp2.getname() in self.component_connections:
                self.component_connections[comp2.getname()].append(new_connection)
            else:
                self.component_connections[comp2.getname()] = [new_connection]

            # fill places_connections
            if comp1.st_dependencies[name1].gettype() == DepType.PROVIDE or \
               comp1.st_dependencies[name1].gettype() == DepType.DATA_PROVIDE:
                for binding in comp1.st_dependencies[name1].getbindings():
                    if binding.getname() in self.places_connections:
                        self.places_connections[binding.getname()].append(new_connection)
                    else:
                        self.places_connections[binding.getname()] = [new_connection]
            elif comp2.st_dependencies[name2].gettype() == DepType.PROVIDE or \
               comp2.st_dependencies[name2].gettype() == DepType.DATA_PROVIDE:
                for binding in comp2.st_dependencies[name2].getbindings():
                    if binding.getname() in self.places_connections:
                        self.places_connections[binding.getname()].append(new_connection)
                    else:
                        self.places_connections[binding.getname()] = [new_connection]

            # white board management
            # if we have a DATA connection, create a whiteboard and attached it
            if (comp1.st_dependencies[name1].gettype() == DepType.DATA_PROVIDE) \
                or (comp1.st_dependencies[name1].gettype() == DepType.DATA_USE):
                white_board = WhiteBoard()
                # get user and provider of the connection
                if comp1.st_dependencies[name1].gettype() == DepType.DATA_PROVIDE:
                    provider = comp1.st_dependencies[name1]
                    user = comp2.st_dependencies[name2]
                else:
                    provider = comp2.st_dependencies[name2]
                    user = comp1.st_dependencies[name1]
                if provider not in self.wbs:
                    self.wbs[provider] = white_board
                    provider.connectwb(self.wbs[provider])
                user.connectwb(self.wbs[provider])
            # else we have a service connection to connect
            else:
                comp1.st_dependencies[name1].connect()
                comp2.st_dependencies[name2].connect()

        else:
            print(Messages.fail() + "ERROR - you try to connect dependencies "
                                 "with incompatible types. DepType.USE and "
                                  "DepType.DATA-USE should be respectively "
                                  "connected to DepType.PROVIDE and "
                                  "DepType.DATA-PROVIDE dependencies."
                  + Messages.endc())
            sys.exit(0)

    def get_component(self, name):
        if name in self.components:
            return self.components[name]
        else:
            print(Messages.fail() + "ERROR - Unknown component "+name +
                  + Messages.endc())
            sys.exit(0)

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

    # a set of active places and connections within the assembly (global)
    act_places = []
    act_connections = []
    # set of active places and connections of the previous iteration
    old_places = []
    old_connections = []

    def init_semantics(self):
        """
        This method activate the initial places of each component and builds
        the global self.act_places
        """
        for c in self.components:
            comp_places = self.components[c].init_places()
            self.act_places.extend(comp_places)

    def semantics(self, dryrun, printing):
        """
        This method runs one semantics iteration by first updating the list
        of enbled connections and then by running semantics of each component
        of the assembly.
        :param dryrun: boolean representing if the semantics is run in dryrun mode
        :param printing: boolean representing if the semantics must print output
        """

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
        for c in self.components:
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


    def disable_enable_connections(self, printing):
        """
        This method build the new list of enabled connections according to
        the current states of "activated" places (ie the ones getting a token).

        :param configuration: the current configuration of the deployment
        :return: the new list of activated connections
        """

        # create the new list of activated connections
        activated_connections = []

        for place in self.act_places:
            if place.getname() in self.places_connections:
                connections = self.places_connections[place.getname()]
                for conn in connections:
                    activated_connections.append(conn.gettuple())
                    if not conn.isactive():
                        conn.activate()
                        if printing:
                            print("[Assembly] Enable connection ("
                                  + str(conn.getnames()) + ")")

        return activated_connections

    def is_finish(self):
        """
        This method checks if the deployment is finished

        :param configuration: the current configuration of the deployment
        :return: True if the deployment is finished, False otherwise
        """

        # the deployment cannot be finished if at least all components have
        # not reached a place
        if len(self.act_places) >= len(self.components):
            # if all places are finals (ie without output docks) the
            # deployment has finished
            all_finals = True
            for place in self.act_places:
                if len(place.get_outputdocks()) > 0:
                    all_finals = False
            return all_finals
        else:
            return False

