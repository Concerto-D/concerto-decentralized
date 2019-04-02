#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: component
   :synopsis: this file contains the Component class.
"""

import sys, time
from queue import Queue
from abc import ABCMeta, abstractmethod
from typing import Dict, Tuple, List, Set, Callable

from concerto.place import Dock, Place
from concerto.dependency import DepType, Dependency
from concerto.transition import Transition
from concerto.gantt_chart import GanttChart
from concerto.utility import Messages, Printer

class Group(object):
    """
    This class is used to create a group object within a Component.
    A group is a set of places and transitions to which a service provide
    dependency is bound. This object facilitate the semantics and its
    efficiency.
    """
    
    class Operation():
        def __init__(self, delta : int):
            self.delta = delta
            
        def is_nothing(self) -> bool:
            return self.delta is 0
    
    def __init__(self, name : str):
        self.name : str = name
        self.elements : Set[str] = set()
        self.nb_tokens : int = 0
    
    def get_name(self) -> str:
        return self.name
    
    def add_places(self, places_names):
        self.elements.update(places_names)
    
    def add_transitions(self, transitions_names):
        self.elements.update(transitions_names)
    
    def add_state(self, state_name : str):
        self.elements.add(state_name)
    
    def add_transition(self, transition_name : str):
        self.elements.add(transition_name)
    
    def contains_place(self, place_name : str) -> bool:
        return place_name in self.elements
    
    def contains_transition(self, transition_name : str) -> bool:
        return transition_name in self.elements
    
    def contains_dock(self, dock : Dock) -> bool:
        return self.contains_transition(dock.get_transition().get_name())
    
    def enter_place_operation(self, input_docks : List[Dock]) -> Operation:
        delta : int = 0
        place_name : str = input_docks[0].get_place().get_name()
        if self.contains_place(place_name):
            delta += 1
        for dock in input_docks:
            if self.contains_dock(dock):
                delta -= 1
        return self.Operation(delta)
    
    def leave_place_operation(self, output_docks : List[Dock]) -> Operation:
        delta : int = 0
        place_name : str = output_docks[0].get_place().get_name()
        if self.contains_place(place_name):
            delta -= 1
        for dock in output_docks:
            if self.contains_dock(dock):
                delta += 1
        return self.Operation(delta)
    
    def is_activating(self, operation : Operation) -> bool:
        return (not self.is_active()) and (operation.delta > 0)
    
    def is_deactivating(self, operation : Operation) -> bool:
        return self.is_active() and (self.nb_tokens + operation.delta is 0)
    
    def is_active(self):
        return self.nb_tokens > 0
    
    def apply(self, operation : Operation):
        if self.nb_tokens + operation.delta < 0:
            raise Exception("Logic error: trying to remove %d tokens to group '%s' while its number of tokens is only %d."%(operation.delta,self.name,self.nb_tokens))
        self.nb_tokens += operation.delta


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


    def __init__(self):
        self.name : str = ""
        self.color : str = ''
        self._verbosity : int = 0
        self.forced_verobisty : int = None
        self.print_time : bool = False
        self.dryrun : bool = False
        self.gantt : GanttChart = None
        self.hidden_from_gantt_chart = False
        
        self.places : List[str] = []
        self.switches : List[Tuple[str,Callable[[Place,str],List[int]]]] = []
        self.transitions : Dict[str,Tuple] = {}
        self.groups : Dict[str,List[str]] = {}
        self.dependencies : Dict[str,Tuple] = {}
        self.initial_place : str = None
        
        self.st_places : Dict[str, Place] = {}
        self.st_transitions : Dict[str,Transition] = {}
        self.st_dependencies : Dict[str, Dependency] = {}
        self.st_groups : Dict[str, Group] = {}
        self.st_behaviors : Set[str] = set()
        
        self.trans_dependencies : Dict[str,List[Dependency]] = {}
        self.place_dependencies : Dict[str,List[Dependency]] = {}
        self.group_dependencies : Dict[str,List[Dependency]] = {}
        self.place_groups : Dict[str,List[Group]] = {}
        
        self.act_places : Set[Place] = set()
        self.act_transitions : Set[Transition] = set()
        self.act_odocks : Set[Dock] = set()
        self.act_idocks : Set[Dock] = set()
        self.act_behavior : str = "_init"
        self.queued_behaviors : Queue = Queue()
        self.visited_places : List[Place] = set()
        
        self.initialized : bool = False
        
        self.create()
        self.add_places(self.places)
        self.add_groups(self.groups)
        self.add_transitions(self.transitions)
        self.add_dependencies(self.dependencies)
    
    
    def set_verbosity(self, level : int):
        self._verbosity = level
        
    def set_print_time(self, value : bool):
        self.print_time = value
        
    def set_dryrun(self, value : bool):
        self.dryrun = value
        
    def set_gantt_chart(self, gc : GanttChart):
        if not self.hidden_from_gantt_chart:
            self.gantt = gc
    
    def force_hide_from_gantt_chart(self):
        self.hidden_from_gantt_chart = True
        self.gantt = None
    
    def force_vebosity(self, forced_verobisty : int):
        self.forced_verobisty = forced_verobisty
    
    def get_verbosity(self):
        if self.forced_verobisty is None:
            return self._verbosity
        else:
            return self.forced_verobisty


    def add_places(self, places : List[str], initial=None):
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

    def add_place(self, name : str, initial=False):
        """
        This method offers the possibility to add a single place to an
        already existing dictionary of places.

        :param name: the name of the place to add
        :param initial: whether the place is the initial place of the component (default: False)
        """
        if name in self.st_places:
            raise Exception("Trying to add '%s' as a place while it is already a place"%name)
        elif name in self.st_transitions:
            raise Exception("Trying to add '%s' as a place while it is already a transition"%name)
        elif name in self.st_groups:
            raise Exception("Trying to add '%s' as a place while it is already a group"%name)
        self.st_places[name] = Place(name)
        self.place_dependencies[name] = []
        self.place_groups[name] = []
        
        if initial:
            self.set_initial_place(initial)


    def add_switches(self, switches : List[Tuple[str,Callable[[Place,str],List[int]]]], initial=None):
        for key in switches:
            self.add_switch(key)
        if initial is not None:
            self.set_initial_place(initial)

    def add_switch(self, tuple : Tuple[str,Callable[[Place,str],List[int]]], initial=False):
        """
        This method offers the possibility to add a single place to an
        already existing dictionary of places.

        :param name: the name of the place to add
        :param initial: whether the place is the initial place of the component (default: False)
        """
        (name, override_f) = tuple
        if name in self.st_places:
            raise Exception("Trying to add '%s' as a place while it is already a place"%name)
        elif name in self.st_transitions:
            raise Exception("Trying to add '%s' as a place while it is already a transition"%name)
        elif name in self.st_groups:
            raise Exception("Trying to add '%s' as a place while it is already a group"%name)
        self.st_places[name] = Place(name, override_f, cp=self) # TODO: Remove cp
        self.place_dependencies[name] = []
        self.place_groups[name] = []
        
        if initial:
            self.set_initial_place(initial)
    
    
    def add_groups(self, groups : Dict[str,List[str]]):
        for name in groups:
            self.add_group(name, groups[name])
    
    def add_group(self, name : str, places : List[str]):
        if name in self.st_places:
            raise Exception("Trying to add '%s' as a group while it is already a place"%name)
        elif name in self.st_transitions:
            raise Exception("Trying to add '%s' as a group while it is already a transition"%name)
        elif name in self.st_groups:
            raise Exception("Trying to add '%s' as a group while it is already a group"%name)
        
        for place_name in places:
            if place_name not in self.st_places:
                raise Exception("Error: trying to add non-existing place '%s' to group '%s'"%(place_name, name))
            elif place_name is self.initial_place:
                raise Exception("Error: trying to add initial place '%s' to group '%s' (framework limitation: initial place cannot be in a group, for now...)"%(place_name, name))
        
        self.st_groups[name] = Group(name)
        self.group_dependencies[name] = []
        self.st_groups[name].add_places(places)
        for place_name in places:
            self.place_groups[place_name].append(self.st_groups[name])


    def add_transitions(self, transitions : Dict[str,Tuple]):
        """
        This method add all transitions declared in the user component class
        as a dictionary associating the name of a transition to a transition
        object created by the user too.
        Requires add_states and add_groups to have been executed

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
        
    def _force_add_transition(self, name : str, src_name : str, dst_name : str, bhv : str, idset : int, func, args=()):
        src = None
        if src_name is not None:
            src = self.st_places[src_name]
        self.st_transitions[name] = Transition(name, src, self.st_places[dst_name], bhv, idset, func, args)
        self.trans_dependencies[name] = []
        self.st_behaviors.add(bhv)
        for group in self.st_groups:
            if self.st_groups[group].contains_place(src_name) and self.st_groups[group].contains_place(dst_name):
                self.st_groups[group].add_transition(name)

    def add_transition(self, name : str, src_name : str, dst_name : str, bhv : str, idset : int, func, args=()):
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
        if name in self.st_places:
            raise Exception("Trying to add '%s' as a transition while it is already a place"%name)
        if name in self.st_transitions:
            raise Exception("Trying to add '%s' as a transition while it is already a transition"%name)
        if name in self.st_groups:
            raise Exception("Trying to add '%s' as a transition while it is already a group"%name)
        if name is "_init":
            raise Exception("Cannot name a transition '_init' (used internally)")
        if bhv is "_init":
            raise Exception("Cannot name a behavior '_init' (used internally)")
        if src_name not in self.st_places:
            raise Exception("Trying to add transition '%s' starting from unexisting place '%s'"%(name, src_name))
        if dst_name not in self.st_places:
            raise Exception("Trying to add transition '%s' going to unexisting place '%s'"%(name, dst_name))
        
        self._force_add_transition(name,src_name,dst_name,bhv,idset,func,args)
    

    def add_dependencies(self, dep : Dict[str,Tuple[DepType, List[str]]]):
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
                raise Exception("ERROR dependency %s - two arguments should be given for construction, "
                        "a type enum DepType and the name of the place, the transition "
                        "or the group to which the dependency is bound."%key)

    def add_dependency(self, name : str, type : DepType, bindings : List[str]):
        """
        This method offers the possibility to add a single dependency to an
        already existing dictionary of dependencies.

        :param name: the name of the dependency to add
        :param type: the type DepType of the dependency
        :param binding: the name of the binding of the dependency (place or transition)
        """
        if type == DepType.DATA_USE:
            for bind in bindings:
                if bind not in self.st_transitions:
                    raise Exception("Trying to bind dependency %s (of type %s) to something else than a transition"%(name,str(type)))
            
            self.st_dependencies[name] = Dependency(self, name, type)
            for transition_name in bindings:
                self.trans_dependencies[transition_name].append(self.st_dependencies[name])
                
                
        elif type == DepType.USE:
            places = []
            transitions = []
            groups = []
            for bind in bindings:
                if bind in self.st_transitions:
                    transitions.append(bind)
                elif bind in self.st_places:
                    places.append(bind)
                elif bind in self.st_groups:
                    groups.append(bind)
                else:
                    raise Exception("Trying to bind dependency %s (of type %s) to something else than a place, a transition or a group"%(name,str(type)))
                
            self.st_dependencies[name] = Dependency(self, name, type)
            for place_name in places:
                self.place_dependencies[place_name].append(self.st_dependencies[name])
            for transition_name in transitions:
                self.trans_dependencies[transition_name].append(self.st_dependencies[name])
            for group_name in groups:
                self.group_dependencies[group_name].append(self.st_dependencies[name])

        elif type == DepType.DATA_PROVIDE:
            for bind in bindings:
                if bind not in self.st_places:
                    raise Exception("Trying to bind dependency %s (of type %s) to something else than a place"%(name,str(type)))
            
            self.st_dependencies[name] = Dependency(self, name, type)
            for place_name in bindings:
                self.place_dependencies[place_name].append(self.st_dependencies[name])

        elif type == DepType.PROVIDE:
            places = []
            groups = []
            for bind in bindings:
                if bind in self.st_places:
                    places.append(bind)
                elif bind in self.st_groups:
                    groups.append(bind)
                else:
                    raise Exception("Trying to bind dependency %s (of type %s) to something else than a place or a group"%(name,str(type)))
                
            self.st_dependencies[name] = Dependency(self, name, type)
            for place_name in places:
                self.place_dependencies[place_name].append(self.st_dependencies[name])
            for group_name in groups:
                self.group_dependencies[group_name].append(self.st_dependencies[name])


    def set_initial_place(self, name : str):
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
        

    def get_places(self):
        """
        This method returns the dictionary of places of the component

        :return: self.st_places the dictionary of places
        """
        return self.st_places

    def get_dependency(self, name : str) -> Dependency:
        """
        This method returns the dependencies object associated to a given
        name

        :param name: the name (string) of the dependency to get
        :return: the dependency object associated to the name
        """
        return self.st_dependencies[name]
    
    def get_dependency_type(self, name : str) -> DepType:
        return self.get_dependency(name).get_type()

    def set_name(self, name : str):
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
    
    def print_color(self, string : str):
        if self.get_verbosity() < 0:
            return
        message : str = "%s[%s] %s%s"%(self.get_color(), self.get_name(), string, Messages.endc())
        if self.print_time:
            Printer.st_tprint(message)
        else:
            print(message)

    def is_connected(self, name : str):
        """
        This method is used to know if a given dependency is connected or not
        :param name: name of the dependency
        :return: True if connected, False otherwise
        """
        return not self.st_dependencies[name].is_free()

    """
    READ / WRITE DEPENDENCIES
    """

    def read(self, name : str):
        return self.st_dependencies[name].read()

    def write(self, name : str, val):
        # keep trace of the line below to check wether the calling method has
        #  the right to acess thes dependency
        # this is not portable according to Python implementations
        # moreover, the write is associated to a transition while the data
        # provide is associated to a place in the model. This has to be
        # corrected somewhere.
        # print(sys._getframe().f_back.f_code.co_name)
        self.st_dependencies[name].write(val)

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
    
    def set_behavior(self, behavior : str):
        if behavior not in self.st_behaviors and behavior is not None:
            raise Exception("Trying to set behavior %s in component %s while this behavior does not exist in this component." % (behavior, self.get_name()))
        # TODO warn if no transition with the behavior is fireable from the current state
        self.act_behavior = behavior
        if self.gantt is not None:
            self.gantt.push_b(self.get_name(), behavior, time.perf_counter())
        self.visited_places = set()
        if self.get_verbosity() >= 1:
            self.print_color("Changing behavior to '%s'"%behavior)
        
    def get_behaviors(self):
        return self.st_behaviors
        
    def get_active_behavior(self):
        return self.act_behavior
    
    def queue_behavior(self, behavior : str):
        if self.get_active_behavior() is None:
            self.set_behavior(behavior)
        else:
            if behavior not in self.st_behaviors and behavior is not None:
                raise Exception("Trying to queue behavior %s in component %s while this behavior does not exist in this component." % (behavior, self.get_name()))
            self.queued_behaviors.put(behavior)
            if self.get_verbosity() >= 1:
                self.print_color("Queing behavior '%s'"%behavior)
            
            
            

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
        return self.get_active_behavior() is None
    
    
    def init(self):
        from concerto.utility import empty_transition
        """
        This method initializes the component and returns the set of active places
        """
        if self.initialized:
            raise Exception("Trying to initialize component '%s' a second time"%self.get_name())
        
        self._force_add_transition("_init",None,self.initial_place,"_init",0,empty_transition)
        self.act_transitions.add(self.st_transitions["_init"])
        
        self.initialized = True
    
    def semantics(self) -> bool:
        """
        This method apply the operational semantics at the component level.
        Returns whether the component is IDLE.
        """
        
        if not self.initialized:
            self.init()
        
        #done = False
        
        #if self.act_places:
            #done = self._place_to_odocks()
        #if (not done) and self.act_odocks:
            #done = self._start_transition()
        #if (not done) and self.act_transitions:
            #done = self._end_transition()
        #if (not done) and self.act_idocks:
            #done = self._idocks_to_place()
        
        #TODO: Discuss if best alternative: doing the 4 if possible (starting by idocks to place so that if a provide is not stable it doesn't get activated)
        if self.act_idocks:
            self._idocks_to_place()
        if self.act_places:
            self._place_to_odocks()
        if self.act_odocks:
            self._start_transition()
        if self.act_transitions:
            self._end_transition()
        
        # Checks if the component is IDLE
        idle = not self.act_transitions and not self.act_odocks and not self.act_idocks
        if idle:
            for place in self.act_places:
                if place not in self.visited_places and len(place.get_output_docks(self.act_behavior)) > 0:
                    idle = False
                    break
        
        if idle:
            if not self.queued_behaviors.empty():
                idle = False
                self.set_behavior(self.queued_behaviors.get())
        
        if idle:
            self.set_behavior(None)
            if self.get_verbosity() >= 1:
                self.print_color("Going IDLE")
        
        return idle


    def _place_to_odocks(self) -> bool:
        """
        This method represents the one moving the token of a place to its
        output docks.
        """
        did_something = False
        places_to_remove : Set[Place] = set()

        for place in self.act_places:
            if place in self.visited_places:
                continue
            odocks = place.get_output_docks(self.act_behavior)
            if len(odocks) is 0:
                continue
            
            can_leave : bool = True
            # Checking place dependencies
            for dep in self.place_dependencies[place.get_name()]:
                if dep.get_type() is DepType.PROVIDE:
                    if dep.is_locked():
                        can_leave = False
                        break
            if not can_leave:
                continue
            
            # Checking group dependencies if in a group
            deactivating_groups_operation : Dict[Group,Group.Operation] = {}
            for group in self.place_groups[place.get_name()]:
                if not can_leave:
                    break
                group_operation = group.leave_place_operation(odocks)
                if group.is_deactivating(group_operation):
                    for dep in self.group_dependencies[group.get_name()]:
                        if (dep.get_type() is DepType.PROVIDE) and dep.is_locked():
                            can_leave = False
                            break
                    deactivating_groups_operation[group] = group_operation
            if not can_leave:
                continue
            
            did_something = True
            if self.get_verbosity() >= 1:
                self.print_color("Leaving place '%s'"%(place.get_name()))
            for dep in self.place_dependencies[place.get_name()]:
                if dep.get_type() is not DepType.DATA_PROVIDE:
                    dep.stop_using()
                    if self.get_verbosity() >= 2:
                        self.print_color("Stopping to use place dependency '%s'"%dep.get_name())
            for group in deactivating_groups_operation:
                group.apply(deactivating_groups_operation[group])
                for dep in self.group_dependencies[group.get_name()]:
                    dep.stop_using()
                    if self.get_verbosity() >= 2:
                        self.print_color("Stopping to use group dependency '%s'"%dep.get_name())
                if self.get_verbosity() >= 2:
                    self.print_color("Deactivating group '%s'"%( group.get_name()))
            self.act_odocks.update(odocks)
            places_to_remove.add(place)
            self.visited_places.add(place)
        
        self.act_places.difference_update(places_to_remove)
        
        return did_something


    def _start_transition(self) -> bool:
        """
        This method starts the transitions which are ready to run:
        """
        did_something = False
        docks_to_remove : Set[Dock] = set()

        for od in self.act_odocks:
            trans = od.get_transition()

            enabled = True
            
            for dep in self.trans_dependencies[trans.get_name()]:
                # Necessarily USE or DATA_USE
                if not dep.is_served():
                    enabled = False
                    break

            if not enabled:
                continue
            
            did_something = True
            if self.get_verbosity() >= 1:
                self.print_color("Starting transition '%s'"%(trans.get_name()))
            for dep in self.trans_dependencies[trans.get_name()]:
                dep.start_using()
                if self.get_verbosity() >= 2:
                    self.print_color("Starting to use transition dependency '%s'"%dep.get_name())
            if self.gantt is None:
                gantt_tuple = None
            else:
                gantt_tuple = (self.gantt,(self.name, self.act_behavior, trans.get_name(), time.perf_counter()))
            trans.start_thread(gantt_tuple, self.dryrun)
            self.act_transitions.add(trans)
            docks_to_remove.add(od)

        self.act_odocks.difference_update(docks_to_remove)
        return did_something


    def _end_transition(self) -> bool:
        """
        This method try to join threads from currently running transitions.
        """
        did_something = False
        transitions_to_remove : Set[Transition] = set()

        # check if some of these running transitions are finished
        for trans in self.act_transitions:
            if trans.get_name() is not "_init":
                if self.gantt is None:
                    gantt_tuple = None
                else:
                    gantt_tuple = (self.gantt,(self.name, self.act_behavior, trans.get_name(), time.perf_counter()))
                joined = trans.join_thread(gantt_tuple, self.dryrun)
                # get the new set of activated input docks
                if not joined:
                    continue
            
            for dep in self.trans_dependencies[trans.get_name()]:
                dep.stop_using()
                if self.get_verbosity() >= 2:
                    self.print_color("Stopping to use transition dependency '%s'"%dep.get_name())
            if self.get_verbosity() >= 1:
                self.print_color("Ending transition '%s'"%(trans.get_name()))
            self.act_idocks.add(trans.get_dst_dock())
            transitions_to_remove.add(trans)

        self.act_transitions.difference_update(transitions_to_remove)
        return did_something


    def _idocks_to_place(self):
        """
        Input docks to place.
        """
        did_something = False
        docks_to_remove : Set[Dock] = set()

        # if not all input docks are enabled for a place, the place will not
        # be activated.
        still_idocks = []

        for dock in self.act_idocks:
            place : Place = dock.get_place()
            if place in self.act_places:
                continue
            
            grp_inp_docks = place.get_groups_of_input_docks(self.act_behavior)
            for inp_docks in grp_inp_docks:
                if len(inp_docks) is 0:
                    continue
                
                ready = True
                for dock2 in inp_docks:
                    if dock2 not in self.act_idocks:
                        ready = False
                        break
                if not ready:
                    continue
                
                # Checking place dependencies
                for dep in self.place_dependencies[place.get_name()]:
                    if dep.get_type() is DepType.USE or dep.get_type() is DepType.DATA_USE:
                        if not dep.is_served():
                            ready = False
                            break
                if not ready:
                    continue
                
                # Checking group dependencies
                activating_groups_operation : Dict[Group,Group.Operation] = {}
                for group in self.place_groups[place.get_name()]:
                    if not ready:
                        break
                    group_operation = group.enter_place_operation(inp_docks)
                    if group.is_activating(group_operation):
                        for dep in self.group_dependencies[group.get_name()]:
                            if dep.get_type() is DepType.USE and (not dep.is_served()):
                                ready = False
                                break
                        activating_groups_operation[group] = group_operation
                if not ready:
                    continue
                
                did_something = True
                for group in activating_groups_operation:
                    if self.get_verbosity() >= 2:
                        self.print_color("Activating group '%s'"%( group.get_name()))
                    group.apply(activating_groups_operation[group])
                    for dep in self.group_dependencies[group.get_name()]:
                        dep.start_using()
                        if self.get_verbosity() >= 2:
                            self.print_color("Starting to use group dependency '%s'"%dep.get_name())
                if self.get_verbosity() >= 1:
                    self.print_color("Entering place '%s'"%( place.get_name()))
                for dep in self.place_dependencies[place.get_name()]:
                    dep.start_using()
                    if self.get_verbosity() >= 2:
                        self.print_color("Starting to use place dependency '%s'"%dep.get_name())
                self.act_places.add(place)
                docks_to_remove.update(inp_docks)
        
        self.act_idocks.difference_update(docks_to_remove)
        return did_something
    
    def get_active_places(self):
        return list([p.get_name() for p in self.act_places])
    
    def get_debug_info(self) -> str:
        debug_string = "== Component '%s' status ==\n" % self.get_name()
        # TODO: remove access to internal variable queue of queued_behaviors, not in API
        debug_string += ("  active behaviors: %s + %s\n" % (self.act_behavior, self.queued_behaviors.queue))
        debug_string += ("  active places: %s\n" % ','.join([p.get_name() for p in self.act_places]))
        debug_string += ("  active transitions: %s\n" % ','.join([t.get_name() for t in self.act_transitions]))
        debug_string += ("  active odocks (transition): %s\n" % ','.join([d.get_transition().get_name() for d in self.act_odocks]))
        debug_string += ("  active idocks (transition): %s\n" % ','.join([d.get_transition().get_name() for d in self.act_idocks]))
        return debug_string
