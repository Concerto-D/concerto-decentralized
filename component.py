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

class Group(object):
    """
    This class is used to create a group object within a Component.
    A group is a set of places and transitions to which a service provide
    dependency is bound. This object facilitate the semantics and its
    efficiency.
    """
    # TODO: VERY IMPORTANT

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
    # st_behaviors a set of behavior names (strings)

    """
    BUILD COMPONENT
    """

    def __init__(self):
        self.name = ""
        self.color = ''
        self.initial_place = None
        self.st_places = {}
        self.st_transitions = {}
        self.st_dependencies = {}
        self.st_behaviors = set()
        self.act_places = []
        self.act_transitions = []
        self.act_odocks = []
        self.act_idocks = []
        self.act_behavior = None
        self.initialized = False
        self.idle = True
        self.create()
        self.add_places(self.places)
        self.add_transitions(self.transitions)
        self.add_dependencies(self.dependencies)

    def add_places(self, places, initial=None):
        """
        This method add all places declared in the user component class as a
        dictionary associating the name of a place to its number of input and
        output docks.

        :param places: dictionary of places
        """
        for key in places:
            self.add_place(key)
        if initial is not None:
            self.set_initial_place(initial)

    def add_transitions(self, transitions):
        """
        This method add all transitions declared in the user component class
        as a dictionary associating the name of a transition to a transition
        object created by the user too.

        :param transitions: dictionary of transitions
        """
        for key in transitions:
            # add docks to places and bind docks
            if len(transitions[key])==6:
                self.add_transition(key, transitions[key][0], transitions[key][
                    1], transitions[key][2], transitions[key][3], transitions[key][4], transitions[key][5])
            else:
                self.add_transition(key, transitions[key][0], transitions[key][
                    1], transitions[key][2], transitions[key][3], transitions[key][4])

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


    def add_place(self, name, initial=False):
        """
        This method offers the possibility to add a single place to an
        already existing dictionary of places.

        :param name: the name of the place to add
        :param initial: whether the place is the initial place of the component (default: False)
        """
        self.st_places[name] = Place(name)
        if initial:
            self.set_initial_place(initial)


    def set_initial_place(self, name):
        """
        This method allows to set the (unique) initial place of the component, if not already done
        using the parameter of add_place and add_places.
        
        :param name: the name of the place to mark initial
        """
        
        if name not in self.st_places:
            raise Exception("Trying to set non-existant place %s as intial place of component %s." % (name, self.get_name()))
        if self.initial_place is not None:
            raise Exception("Trying to set place %s as intial place of component %s while %s is already the intial place." % (name, self.get_name(), self.initial_place))
        self.initial_place = name
    

    def add_transition(self, name, src, dst, bhv, idset, func, args=()):
        """
        This method offers the possibility to add a single transition to an
        already existing dictionary of transitions.

        :param name: the name of the transition to add
        :param src: the name of the source place of the transition
        :param dst: the name of the destination place of the transition
        :param bhv: the name of the behavior associated to the transition
        :param func: a functor created by the user
        :param args: optional tuple of arguments to give to the functor
        """
        self.st_transitions[name] = Transition(name, src, dst, bhv, idset, func, args,
                                              self.st_places)
        self.st_behaviors.add(bhv)

    def add_dependency(self, name : str, type : DepType, bindings):
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
                # create the dependency
                self.st_dependencies[name] = Dependency(name, type, places)
                # for each place add the provide dependency
                for p in places:
                    p.add_provide(self.st_dependencies[name])
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

    def set_name(self, name):
        """
        This method sets the name of the current component

        :param name: the name (string) of the component
        """
        self.name = name

    def get_name(self):
        """
        This method returns the name of the component

        :return: the name (string) of the component
        """
        return self.name

    def set_color(self, c):
        """
        This method set a printing color to the current component

        :param c: the color to set
        """
        self.color = c

    def get_color(self):
        """
        This method returns the color associated to the current component

        :return: the printing color of the component
        """
        return self.color

    def is_connected(self, name):
        """
        This method is used to know if a given dependency is connected or not
        :param name: name of the dependency
        :return: True if connected, False otherwise
        """
        return not self.st_dependencies[name].is_free()

    """
    READ / WRITE DEPENDENCIES
    """

    def read(self, name):
        return self.st_dependencies[name].get_wb().read()

    def write(self, name, val):
        # keep trace of the line below to check wether the calling method has
        #  the right to acess thes dependency
        # this is not portable according to Python implementations
        # moreover, the write is associated to a transition while the data
        # provide is associated to a place in the model. This has to be
        # corrected somewhere.
        # print(sys._getframe().f_back.f_code.co_name)
        self.st_dependencies[name].get_wb().write(val)

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
            if self.st_dependencies[dep].is_free():
                result = False

        return result
    
    
    """
    RECONFIGURATION
    """
    
    # reconfiguration of the component by changing its current behavior
    
    def set_behavior(self, behavior):
        if behavior not in self.st_behaviors and behavior is not None:
            raise Exception("Trying to set behavior %s in component %s while this behavior does not exist in this component." % (behavior, self.get_name()))
        # TODO warn if no transition with the behavior is fireable from the current state
        self.act_behavior = behavior
        
    def get_behaviors(self):
        return self.st_behaviors
        
    def get_active_behavior(self):
        return self.act_behavior
            
            

    """
    OPERATIONAL SEMANTICS
    """

    # these four lists represents the configuration at the component level
    # they are used within the semantics parts, ie the runtime
    # act_places the set of active places of the component
    # act_transitions the set of active transitions of the component
    # act_idocks the set of active input docks of the component
    # act_odocks the set of active output docks of the component

    # trans_connections a dictionary associating one transition to its
    # associated use connections

    # old_places the set of previous iteration active places of the component
    # old_transitions the set of previous iteration active transitions of the component
    # old_idocks the set of previous iteration active input docks of the component
    # old_odocks the set of previous iteration active output docks of the component
    # old_my_connections
    
    def is_idle(self):
        """
        This method returns a boolean stating if the component is idle.
        :return: a boolean stating if the component is idle
        """
        return self.idle
    
    def init(self, comp_connections):
        """
        This method initializes the component and returns the set of active places
        """
        places = self._init_places()
        self._init_trans_connections(comp_connections)
        self.initialized = True
        self.idle = True
        return places

    def _init_trans_connections(self, comp_connections):
        """
        This method initializes the dictionary associating one transition to
        a set of connections. This dictionary is used to start a transition.
        :param comp_connections: the list of all connections associated to
        the current component.
        """

        self.trans_connections = {}

        for t in self.st_transitions:
            # find this trans in dependencies
            deps = []
            for d in self.st_dependencies:
                bindings = self.st_dependencies[d].get_bindings()
                if self.st_transitions[t] in bindings:
                    deps.append(d)

            for d in deps:
                for conn in comp_connections:
                    c = conn.gettuple()
                    if (c[0].get_name() == self.name and c[1].get_name() == d) or \
                            (c[2].get_name() ==self.name and c[3].get_name() == d):
                        if t not in self.trans_connections:
                            self.trans_connections[t] = [conn]
                        else:
                            self.trans_connections[t].append(conn)

    def _init_places(self):
        """
        This method initializes the initial activated places of the component
        in its local configuration self.act_places
        """
        if not self.act_places:
            self.act_places.append(self.st_places[self.initial_place])

        self.old_places = []
        self.old_odocks = []
        self.old_my_connections = []

        return self.act_places

    def semantics(self, my_connections, dryrun, printing):
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
        
        #TODO: ne pas autoriser plus d'une action de sémantique à s'exécuter à la fois
        
        
        if not self.initialized:
            raise ("Error: trying to execute one step of semantics in uninitialized component %s." % self.get_name())

        self.printing = printing

        new_transitions = []
        new_places = []
        new_idocks = []
        new_odocks = []

        # ending transitions (atomic)
        (still_running, idocks) = self._end_transition(dryrun)
        new_transitions.extend(still_running)
        new_idocks.extend(idocks)

        # input docks to places (atomic)
        (places, still_idocks) = self._idocks_in_place()
        
        new_idocks.extend(still_idocks)
        new_places.extend(places)

        # place to output docks
        # only when places or connections have changed compared to the
        # previous iteration.
        # otherwise, places stay the same and no new output docks activated
        if self.old_places == self.act_places \
                and self.old_my_connections == my_connections:
            new_places.extend(self.old_places)
        else:
            (odocks, still_place) = self._place_in_odocks(my_connections)
            new_places.extend(still_place)
            new_odocks.extend(odocks)

        #start transition
        # only when output docks or connections have changed compared to the
        # previous iteration
        # otherwise no new transitions and the same output docks
        if self.old_odocks == self.act_odocks \
                and self.old_my_connections == my_connections:
            new_odocks.extend(self.old_odocks)
        else:
            (add_transitions, still_odocks) = self._start_transition(
                    my_connections, dryrun)
            # concatenate new transitions with the ones still running
            new_transitions.extend(add_transitions)
            new_odocks.extend(still_odocks)

        # keep changes traces
        self.old_places = self.act_places.copy()
        self.old_odocks = self.act_odocks.copy()
        self.old_my_connections = my_connections.copy()

        # replace the new local configuration
        self.act_places = new_places.copy()
        self.act_transitions = new_transitions.copy()
        self.act_idocks = new_idocks.copy()
        self.act_odocks = new_odocks.copy()
        
        # Checks if the component is idle
        self.idle = not self.act_transitions and not self.act_odocks and not self.act_idocks
        if self.idle:
            for place in self.act_places:
                if len(place.get_output_docks(self.act_behavior)) > 0:
                    self.idle = False
                    break

        # return the new set of active places to the global configuration
        return self.act_places


    def _end_transition(self, dryrun):
        """
        This method try to join threads from currently running transitions.
        For joined transitions, the dst_docks (ie input docks of the assembly)
        are stored for the new configuration.
        Un-joined transitions are stored for the new configuration.

        :param dryrun: to indicate if the assembly is executed in dryrun mode.
        :return: return (still_running, new_idocks)

        Elements of the returned tuple are the list of transitions still
        running and the list of new input docks resulting from finished
        transitions in a pair.
        """
        still_running = []
        new_idocks = []

        # check if some of these running transitions are finished
        for trans in self.act_transitions:
            joined = trans.join_thread(dryrun)
            # get the new set of activated input docks
            if joined:
                if self.printing:
                    print(self.color + "[" + self.name + "] End transition '" +
                          trans.get_name() + "'" + Messages.endc())
                new_idocks.append(trans.get_dst_dock())
            # keep the list of unterminated transitions
            elif not joined:
                still_running.append(trans)

        return (still_running, new_idocks)


    def _idocks_in_place(self):
        """
        This method returns the list of new places enabled. These places come
        from their set of input docks, all ready.

        :return: (new_places, still_idocks)

        Elements of the returned tuple are the new list of new enabled places,
        and the list of input docks without modification
        """
        new_places = []

        # if not all input docks are enabled for a place, the place will not
        # be activated. In this case we have to keep the list of enabled input
        # docks.
        still_idocks = []

        for id in self.act_idocks:
            # print("Considering idock %s"%str(id)) # TODO REMOVE
            place : Place = id.mother
            if place not in new_places:
                #print("Considering place '%s'"%str(place.get_name())) # TODO REMOVE
                grp_inp_docks = place.get_groups_of_input_docks(self.act_behavior)
                for inp_docks in grp_inp_docks:
                    #inp_docks = grp_inp_docks[inp_docks_id]
                    #print("Number of input docks: %d"%len(inp_docks)) # TODO REMOVE
                    if len(inp_docks) > 0:
                        ready = True
                        for id in inp_docks:
                            if id not in self.act_idocks:
                                ready = False
                                break
                        if ready:
                            if self.printing:
                                print(
                                    self.color + "[" + self.name + "] In place '" +
                                    place.get_name() + "'" + Messages.endc())
                            new_places.append(place)
                        else:
                            for id in inp_docks:
                                if id in self.act_idocks:
                                    still_idocks.append(id)

        return new_places, still_idocks


    def _place_in_odocks(self, my_connections):
        """
        This method represents the one moving the token of a place to its
        output docks.

        :param my_connections: the list of enabled connections of the current
        component.
        :return: (new_odocks, still_place)

        Elements of the returned tuple are the new list of output docks and
        the list of places that cannot move to output docks (possible because of groups and dependencies on services).
        """
        new_odocks = []
        still_place = []

        for place in self.act_places:
            odocks = place.get_output_docks(self.act_behavior)
            if len(odocks) > 0:
                # the place can be left if no provide dependencies are bound
                # to it
                #provides = place.get_provides()
                #if len(provides) == 0:
                    new_odocks += odocks
                #else:
                    # we stay forever in the place that is providing the
                    # service, we consider such dependency in final places
                    # only (limitation)
                #    service_found = False
                #    for p in provides:
                #        if p.get_type() == DepType.PROVIDE:
                #            service_found = True
                #    if service_found:
                #        still_place.append(place)
                #    else:
                #        new_odocks += odocks
            else:
                still_place.append(place)

        # TODO warning the current implementation is limited compared to the
        # model. The group notion has not been implemented properly.

        return new_odocks, still_place

    def _start_transition(self, my_connections, dryrun):
        """
        This method start the transitions ready to run:

        - source dock of the transition in the list of activated output docks

        - all dependencies required by the transition in an activated connection

        :param my_connections: list of connections associated to the current component
        :param dryrun: to indicate if the assembly is executed in dryrun mode.
        :return: (new_transitions, still_odocks)

        Elements of the returned tuple are the list of new transitions
        started by the method and the list of output docks still waiting for connections.
        """
        new_transitions = []
        still_odocks = []

        for od in self.act_odocks:
            trans = od.get_transition()

            enabled = True

            if trans.get_name() in self.trans_connections:
                for conn in self.trans_connections[trans.get_name()]:
                    found = False
                    for act_conn in my_connections:
                        if act_conn == conn.gettuple():
                            found = True
                    if not found:
                        enabled = False
                        break

            if enabled:
                if self.printing:
                    print(self.color + "[" + self.name + "] Start transition '"
                        + trans.get_name() + "' ..." + Messages.endc())
                trans.start_thread(dryrun)
                new_transitions.append(trans)
            else:
                still_odocks.append(trans.get_src_dock())

        return new_transitions, still_odocks
