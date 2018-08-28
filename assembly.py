#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: assembly
   :synopsis: this file contains the Assembly class.
"""

import sys
from dependency import *
from utility import Messages, COLORS


class WhiteBoard (object):
    """ This class is used to implement data dependencies of the Madeus model.
    Each connection between two components is associated to a white board
    able to contain one value of any type. The provider component will write
    data inside its transitions while the user components will read data.
    """

    def __init__(self):
        pass

    def write(self, data):
        self.data = data

    def read(self):
        return self.data


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
            self.connections.append((comp1, comp1.st_dependencies[name1], comp2,
                                     comp2.st_dependencies[name2]))

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

    def disable_enable_connections(self, configuration, printing):
        """
        This method build the new list of enabled connections according to
        the current states of "activated" places (ie the ones getting a token).

        :param configuration: the current configuration of the deployment
        :return: the new list of activated connections
        """
        places = configuration.get_places()
        conf_conn = configuration.get_connections()

        # create the new list of activated connections
        activated_connections = []

        # for all connections of the assembly
        for conn in self.connections:
            if conn[1].gettype() == DepType.PROVIDE or conn[1].gettype() == \
                    DepType.DATA_PROVIDE:
                # foreach place bound to this connection and present in
                # enabled places (ie get a token), add the connection to the
                # list of enabled connections.
                for place in places:
                    if place in conn[1].getbindings(): # if the place is in
                        # the group of places bound to the service
                        activated_connections.append(conn)
                        if conn not in conf_conn:
                            if printing:
                                print("[Assembly] Enable connection (" + conn[
                                    0].getname() + ", "
                                      + conn[1].getname() + ", "
                                      + conn[2].getname() + ", "
                                      + conn[3].getname() + ")")

            elif conn[3].gettype() == DepType.PROVIDE or conn[3].gettype() ==\
                    DepType.DATA_PROVIDE:
                for place in places:
                    if place in conn[3].getbindings(): # if the place is in
                        # the group of places bound to the service
                        activated_connections.append(conn)
                        if conn not in conf_conn:
                            if printing:
                                print("[Assembly] Enable connection (" + conn[
                                    0].getname() + ", "
                                      + conn[1].getname() + ", "
                                      + conn[2].getname() + ", "
                                      + conn[3].getname() + ")")

        # data connections are always kept once activated
        for conn in conf_conn:
            if conn not in activated_connections:
                if conn[1].gettype() == DepType.DATA_PROVIDE \
                        or conn[1].gettype() == DepType.DATA_USE \
                        or conn[3].gettype() ==  DepType.DATA_USE\
                        or conn[3].gettype() ==  DepType.DATA_PROVIDE:
                    activated_connections.append(conn)

        return activated_connections

    def is_finish(self, configuration):
        """
        This method checks if the deployment is finished

        :param configuration: the current configuration of the deployment
        :return: True if the deployment is finished, False otherwise
        """

        places = configuration.get_places()
        # the deployment cannot be finished if at least all components have
        # not reached a place
        if len(places) >= len(self.components):
            # if all places are finals (ie without output docks) the
            # deployment has finished
            all_finals = True
            for place in places:
                if len(place.get_outputdocks()) > 0:
                    all_finals = False
            return all_finals
        else:
            return False

