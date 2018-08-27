#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: component
   :synopsis: this file contains the Component class.
"""

import sys
from abc import ABCMeta, abstractmethod
from place import *
from dependency import *
from transition import Transition
from utility import Messages

class Component (object, metaclass=ABCMeta):
    """This Component class is used to create a component.

        A component is a software module to deploy. It is composed of places,
        transitions between places, dependencies and bindings between
        dependencies and Places/transitions.

        This is an abstract class that need to be override.
    """

    @abstractmethod
    def create(self):
        pass

    # st_places a dictionary of Place objects
    # st_transitions a dictionary of Transition objects
    # st_dependencies a dictionary of Dependency objects

    """
    BUILD COMPONENT
    """

    def __init__(self):
        self.name = ""
        self.color = ''
        self.st_places = {}
        self.st_transitions = {}
        self.st_dependencies = {}
        self.create()
        self.add_places(self.places)
        self.add_transitions(self.transitions)
        self.add_dependencies(self.dependencies)

    def add_places(self, places):
        """
        This method add all places declared in the user component class as a
        dictionary associating the name of a place to its number of input and
        output docks.

        :param places: dictionary of places
        """
        for key in places:
            self.add_place(key)

    def add_transitions(self, transitions):
        """
        This method add all transitions declared in the user component class
        as a dictionary associating the name of a transition to a transition
        object created by the user too.

        :param transitions: dictionary of transitions
        """
        for key in transitions:
            # add docks to places and bind docks
            if len(transitions[key])==4:
                self.add_transition(key, transitions[key][0], transitions[key][
                    1], transitions[key][2], transitions[key][3])
            else:
                self.add_transition(key, transitions[key][0], transitions[key][
                    1], transitions[key][2])

    def add_dependencies(self, dep):
        """
        This method add all dependencies declared in the user component class
        as a dictionary associating the name of a dependency to both a type
        and the name of the transition or the place to which it is bound.

        - a 'use' or 'data-use' dependency can be bound to a transition

        - a 'provide' or 'data-provide' dependency can be bound to a place

        :param dep: dictionary of dependencies

        """
        for key in dep:
            if len(dep[key])==2:
                type = dep[key][0]
                bname = dep[key][1] # list of places or transitions bounded to
                self.add_dependency(key, type, bname)

            else:
                print(Messages.fail() + "ERROR dependency "
                      + key
                      + " - two arguments should be given for construction, "
                        "a type enum DepType and the name of the transition "
                        "or the place to which the dependency is bound."
                      + Messages.endc())
                sys.exit(0)


    def add_place(self, name):
        """
        This method offers the possibility to add a single place to an
        already existing dictionary of places.

        :param name: the name of the place to add
        """
        self.st_places[name] = Place(name)

    def add_transition(self, name, src, dst, func, args=()):
        """
        This method offers the possibility to add a single transition to an
        already existing dictionary of transitions.

        :param name: the name of the transition to add
        :param src: the name of the source place of the transition
        :param dst: the name of the destination place of the transition
        :param func: a functor created by the user
        :param args: optional tuple of arguments to give to the functor
        """
        self.st_transitions[name] = Transition(name, src, dst, func, args,
                                              self.st_places)

    def add_dependency(self, name, type, bindings):
        """
        This method offers the possibility to add a single dependency to an
        already existing dictionary of dependencies.

        :param name: the name of the dependency to add
        :param type: the type DepType of the dependency
        :param binding: the name of the binding of the dependency (place or transition)
        """
        if type == DepType.DATA_USE or type == DepType.USE:
            btrans = True
            trans = []
            for bind in bindings:
                if bind not in self.st_transitions:
                    btrans = False
                    break
                else:
                    trans.append(self.st_transitions[bind])
            if btrans:
                self.st_dependencies[name] = Dependency(name, type, trans)
            else:
                print(
                    Messages.fail() + "ERROR - according to the type of dependency "
                    + name + " : " + str(type) + ", it should be "
                                                "bound to a "
                                                "transition"
                    + Messages.endc())
                sys.exit(0)

        elif type == DepType.DATA_PROVIDE or type == DepType.PROVIDE:
            btrans = True
            places = []
            for bind in bindings:
                if bind not in self.st_places:
                    btrans = False
                    break
                else:
                    places.append(self.st_places[bind])
            if btrans:
                terminal = False
                for p in places:
                    ods = p.get_outputdocks()
                    if len(ods) == 0:
                        terminal = True
                        break
                if terminal or type == DepType.DATA_PROVIDE:
                    # create the dependency
                    self.st_dependencies[name] = Dependency(name, type, places)
                    # for each place add the provide dependency
                    for p in places:
                        p.add_provide(self.st_dependencies[name])
                else:
                    print(Messages.fail() + "ERROR - at least one "
                                            "place bound to a provide "
                                            "dependency must be a terminal "
                                            "place without output "
                                            "docks."
                          + Messages.endc())
                    sys.exit(0)
            else:
                print(
                    Messages.fail() + "ERROR - according to the type of dependency "
                    + name + " : " + str(type) + ", its should be "
                                                "bound to a place"
                    + Messages.endc())
                sys.exit(0)

    def get_places(self):
        """
        This method returns the dictionary of places of the component

        :return: self.st_places the dictionary of places
        """
        return self.st_places

    def get_dependency(self, name):
        """
        This method returns the dependencies object associated to a given
        name

        :param name: the name (string) of the dependency to get
        :return: the dependency object associated to the name
        """
        return self.st_dependencies[name]

    def setname(self, name):
        """
        This method sets the name of the current component

        :param name: the name (string) of the component
        """
        self.name = name

    def getname(self):
        """
        This method returns the name of the component

        :return: the name (string) of the component
        """
        return self.name

    def setcolor(self, c):
        """
        This method set a printing color to the current component

        :param c: the color to set
        """
        self.color = c

    def getcolor(self):
        """
        This method returns the color associated to the current component

        :return: the printing color of the component
        """
        return self.color

    """
    READ / WRITE DEPENDENCIES
    """

    def read(self, name):
        return self.st_dependencies[name].getwb().read()

    def write(self, name, val):
        # keep trace of the line below to check wether the calling method has
        #  the right to acess thes dependency
        # this is not portable according to Python implementations
        # moreover, the write is associated to a transition while the data
        # provide is associated to a place in the model. This has to be
        # corrected somewhere.
        # print(sys._getframe().f_back.f_code.co_name)
        self.st_dependencies[name].getwb().write(val)

    """
    CHECK COMPONENT
    """

    def check_warnings(self):
        """
        This method check WARNINGS in the structure of the component.

        :return: False if some WARNINGS have been detected, True otherwise.
        """
        check = True

        return check

    def check_connections(self):
        """
        This method check connections once the component has been
        instanciated and connected in an assembly. This method is called by
        the engine -> assembly

        :return: True if all dependencies of a component are connected, False otherwise
        """

        result = True

        for dep in self.st_dependencies:
            if self.st_dependencies[dep].isfree():
                result = False

        return result

    """
    OPERATIONAL SEMANTICS
    """

    def semantics(self, configuration, dryrun):
        """
        This method apply the operational semantics at the component level.
        It takes as input the current configuration of the deployment which
        represents runtime information.

        :param configuration: The current configuration of the deployment
        :return: a tuple (new_transitions, new_places, new_idocks, new_odocks)

        Elements of the returned tuple are respectively the list of
        components, transitions, places, input docks and output docks in the
        new configuration of the current component.
        """

        transitions = configuration.get_transitions()
        places = configuration.get_places()
        idocks = configuration.get_input_docks()
        odocks = configuration.get_output_docks()
        connections = configuration.get_connections()

        # current running transitions
        my_transitions = []
        for t in self.st_transitions:
            if self.st_transitions[t] in transitions:
                my_transitions.append(self.st_transitions[t])
        # check if some of these running transitions are finished
        # get the new set of activated input docks
        # keep the list of unterminated transitions
        (still_running, new_idocks) = self.end_transition(my_transitions,
                                                          dryrun)
        new_transitions = still_running

        # the activated output docks of the current component
        my_idocks = []
        for d in idocks:
            for p in self.st_places:
                ids = self.st_places[p].get_inputdocks()
                if d in ids:
                    my_idocks.append(d)
        # new list of places
        (new_places, still_idocks) = self.idocks_in_place(my_idocks)

        new_idocks += still_idocks

        # enabled places of the current component
        my_places = []
        for p in self.st_places:
            if self.st_places[p] in places:
                my_places.append(self.st_places[p])
        (new_odocks, still_place) = self.place_in_odocks(my_places,
                                                         transitions,
                                                         connections)

        new_places += still_place

        my_connections = []
        for conn in connections:
            if conn[0] == self or conn[2] == self:
                my_connections.append(conn)
        # the activated output docks of the current component
        my_odocks = []
        for d in odocks:
            for p in self.st_places:
                ods = self.st_places[p].get_outputdocks()
                if d in ods:
                    my_odocks.append(d)
        # start transitions from output docks if all dependencies are solved
        # (enabled connections)
        (add_transitions, still_odocks) = self.start_transition(my_connections,
        my_odocks, dryrun)

        # concatenate new transitions with the ones still running
        new_transitions += add_transitions
        new_odocks += still_odocks

        return (new_transitions, new_places, new_idocks, new_odocks)


    def end_transition(self, my_transitions,dryrun):
        """
        This method try to join threads from currently running transitions.
        For joined transitions, the dst_docks (ie input docks of the assembly)
        are stored for the new configuration.
        Un-joined transitions are stored for the new configuration.

        :param my_transitions: list of currently running transitions.
        :return: return (still_running, new_idocks)

        Elements of the returned tuple are the list of transitions still
        running and the list of new input docks resulting from finished
        transitions in a pair.
        """
        still_running = []
        new_idocks = []

        # check if some of these running transitions are finished
        for trans in my_transitions:
            joined = trans.join_thread(dryrun)
            # get the new set of activated input docks
            if joined:
                print(self.color + "[" + self.name + "] End transition '" +
                      trans.getname() + "'" + Messages.endc())
                new_idocks.append(trans.get_dst_dock())
            # keep the list of unterminated transitions
            elif not joined:
                still_running.append(trans)

        return (still_running, new_idocks)


    def idocks_in_place(self, my_idocks):
        """
        This method returns the list of new places enabled. These places come
        from their set of input docks, all ready.

        :param my_idocks: list of enabled input docks of the assembly
        :return: (new_place, still_idocks)

        Elements of the returned tuple are the new list of new enabled places,
        and the list of input docks without modification
        """
        new_places = []

        # if not all input docks are enabled for a place, the place will not
        # be activated. In this case we have to keep the list of enabled input
        # docks.
        still_idocks = []

        if len(my_idocks) > 0:
            for place in self.st_places:
                inp_docks = self.st_places[place].get_inputdocks()
                if len(inp_docks) > 0:
                    ready = True
                    for id in inp_docks:
                        if id not in my_idocks:
                            ready = False
                            break
                    if ready:
                        print(self.color + "[" + self.name + "] In place '" +
                              self.st_places[place].getname() + "'"
                              + Messages.endc())
                        new_places.append(self.st_places[place])
                    else:
                        for id in inp_docks:
                            if id in my_idocks:
                                still_idocks.append(id)

        return new_places, still_idocks


    def place_in_odocks(self, my_places, transitions, connections):
        """
        This method represents the one moving the token of a place to its
        output docks.

        :param my_places: the list of enabled places of the current component.
        :return: (new_odocks, still_place)

        Elements of the returned tuple are the new list of output docks and
        the list of places that cannot move to output docks (possible because of groups and dependencies on services).
        """
        new_odocks = []
        still_place = []

        for place in my_places:
            odocks = place.get_outputdocks()
            if len(odocks) > 0:
                # the place can be left if no provide dependencies are bound
                # to it, or if no using transition is active
                provides = place.get_provides()
                if len(provides) == 0:
                    new_odocks += odocks
                else:
                    # is there a provide used by a transition somewhere
                    used = False
                    # foreach provide bound to the place, check if it is in use
                    for prov in provides:
                        for conn in connections:
                            if conn[0] == self:
                                conn_trans = conn[3].getbindings() #list of
                                # transitions connected to the place
                            elif conn[2] ==self:
                                conn_trans = conn[1].getbindings()  # list of
                                # transitions connected to the place
                            lused = False
                            for t in conn_trans:
                                if t in transitions:
                                    lused = True
                                    break
                            if lused:
                                used = True
                                break

                    if not used:
                        new_odocks += odocks
                    else:
                        still_place.append(place)
            else:
                still_place.append(place)

        return new_odocks, still_place

    def start_transition(self, my_connections, my_odocks, dryrun):
        """
        This method start the transitions ready to run:

        - source dock of the transition in the list of activated output docks

        - all dependencies required by the transition in an activated connection

        :param my_connections: list of connections associated to the current component
        :param odocks: list of activated output docks of the assembly
        :return: (new_transitions, still_odocks)

        Elements of the returned tuple are the list of new transitions
        started by the method and the list of output docks still waiting for connections.
        """
        new_transitions = []
        still_odocks = []

        if len(my_odocks) > 0:
            # start transitions from output docks
            for trans in self.st_transitions:
                # if the source dock of the transition (output dock of a place) is
                # ready (ie get a token)
                if self.st_transitions[trans].get_src_dock() in my_odocks:
                    # check that connections bound to this transition are enabled
                    enabled = True

                    # find trans in dependencies
                    for d in self.st_dependencies:
                        bindings = self.st_dependencies[d].getbindings()
                        if self.st_transitions[trans] in bindings:
                            # find the dependency d in the list of my enabled
                            # connections
                            dep_found = False
                            for conn in my_connections:
                                if conn[1] == self.st_dependencies[d] \
                                        or conn[3] == self.st_dependencies[d]:
                                    dep_found = True
                                    break
                            if dep_found == False:
                                enabled = False
                                break

                    # start the thread and the transition
                    if enabled:
                        print(self.color + "[" + self.name + "] Start transition '" +
                              self.st_transitions[trans].getname() + "' ..."
                              + Messages.endc())
                        self.st_transitions[trans].start_thread(dryrun)
                        new_transitions.append(self.st_transitions[trans])
                    else:
                        still_odocks.append(self.st_transitions[trans].get_src_dock())

        return new_transitions, still_odocks
