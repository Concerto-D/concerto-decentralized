#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains the core parts of MAD (Madeus Application Deployer).

MAD is a Python implementation of the Madeus model that aims to efficiently and
safely deploy distributed software from a fine-grained description of their
deployment process and their dependencies. More precisely, MAD allows to:

    1. Describe the deployment steps and the dependencies of distributed
    software components in accordance with the Madeus model;
    2. Describe an assembly of components, resulting in a functional
    distributed software;
    3. Automatically deploy the component assembly of distributed software
    following the operational semantics of Madeus.

This module is in charge of describing the elements required for the first
points. Basically, each software component deployment process can be described
through Petri-nets. In such Petri-nets, places are in charge of defining the
state of the deployment, while the transitions between those places are used to
trigger actions. Furthermore, our Petri-net based components are equipped with
ports to define dependencies between the different components of a distributed
software. While some ports are meant to ``provide`` something (e.g. data,
synchronization information), others are meant to ``use`` or consume those
things. Thus, a ``provide`` port from Component_A can be connected to a ``use``
port from Component_B.

While this module is in charge of defining those elements related to the first
point of the list, elements related to the assembly of components can be found
in ~assembly.py~ and elements related to the automatic deployment of such
assembly are defined in ~automaton.py~.

"""

from six import string_types
from functools import partial
from utils.extra import listify
from collections import Callable
from utils.exceptions import NetError, NetConditionError, NetCallbackError


class Place(object):
    """
    Define a place element in a Madeus PetriNet.

    Places are used to describe the state of a component.

    Args:
        name (str): Name of the place.

    Attributes:
        name (str): Name of the place.
        state (bool): True if the state is activated.
        incoming (int): Count the number of incoming transitions.
        outgoing (int): Count the number of outgoing transitions.
    """

    def __init__(self, name):
        self.name = name
        self.state = False
        self.incoming = 0
        self.outgoing = 0

    def toggle_state(self, state=None):
        """
        Used to toggle the state of the place.

        Args:
            state (bool): Describe the state of the place.
        """
        self.state = not self.state if state is None else state


class Transition(object):
    """
    Define a transition in a Madeus PetriNet.

    A transition connects two places by applying a set of actions through
    callbacks, and might be constrained by conditions.

    Args:
        name (str): Name of the transition.
        net (:obj:`PetriNet`): A reference to the PetriNet.
        src (str): Name of the source place.
        dst (str): Name of the destination place.
        conditions (:obj:`list` of :obj:`callable`, optional): List of
                functions that must return a boolean to determine if the
                transition can be fired or not.

    Attributes:
        name (str): Name of the transition.
        state (bool): True if the transition has not been triggered.
        net (:obj:`PetriNet`): A reference to the PetriNet.
        src (str): Name of the source place.
        dst (str): Name of the destination place.
        callback (:obj:`list` of :obj:`callable`): List of functions to call
                when the transition if fired.
        conditions (:obj:`list` of :obj:`callable`): List of functions that
                must return a boolean to determine if the transition can be
                fired or not (default=None).
        inUse (int): Since callbacks take some time to run and mad manages
                parallelism, this attribute is used to know if a transition is
                currently handled or not.
    """

    def __init__(self, name, net, src, dst, conditions=None):

        self.name = name
        self.state = True
        self.net = net
        self.src = src
        self.dst = dst
        self.callbacks = []
        self.conditions = [] if conditions is None else listify(conditions)
        self.inUse = 0

        # Increment incoming and outgoing counters for dst and src places:
        self.net.get_place(self.dst).incoming += 1
        self.net.get_place(self.src).outgoing += 1

    def fire(self, dry_run=False):
        """
        If the conditions are valid, this function triggers the callbacks
        attached to the transition.

        Args:
            dry_run (bool, optional): If True, no callback is triggered when
                transitions are fired (default=False).
        """
        # Check if the transition is available regarding the current state:
        if self.src not in self.net.model.current_places:
            raise Exception(
                    'Transaction "%s" can\'t be fired because "%s" is not in '
                    'the current set of places "%s".'
                    % (self.name, self.src, self.net.current_places))

        # Check if the transition has already been triggered:
        if not self.state:
            raise Exception(
                    'Transaction "%s" can\'t be fired because it is not '
                    'activated.'
                    % (self.name))

        # Check if the transition is valid in the current deployment state:
        if self.name not in self.net.get_current_transitions():
            raise Exception(
                    'Transaction "%s" can\'t be fired because it is not in '
                    'the current set of transitions "%s".'
                    % (self.name, self.net.get_current_transitions()))

        # Check that every user's conditions return `True`:
        for condition in self.conditions:
            func = getattr(self.net.model, condition, lambda: None)
            if func and func():
                pass
            else:
                raise NetConditionError('Condition "%s" from the "%s" '
                        'transition is not valid' % (condition, self.name))
                return 1

        # Start the transition actions by calling user's callbacks:
        for callback in self.callbacks:
            if not dry_run:
                # shall we check the return status of such callable?
                # if callback fails: exit before updating the net
                result = callback()
                if result:
                    raise NetCallbackError('Callback "%s" from the "%s" '
                            'transition is not valid'
                            % (callback.__name__, self.name))
                    return 1

        # Update the PetriNet:
        self.net.update_net(self.src, self.dst)

        # Transition has been successfully done! We toggle the state:
        self.state = False

        return 0


    def add_callback(self, func):
        """
        Add a callback to trigger during the transition.

        Args:
            func (str): Name of the callback function to call.
        """
        self.callbacks.append(func)

    def add_condition(self, func):
        """
        Add a condition to check before firing the transition.

        Args:
            func (str): Name of a function which must return True or False
        """
        self.conditions.append(func)


class Port(object):
    """
    Describe a port used to connect multiple PetriNet elements.

    Args:
        name (str): Name of the port.
        net (:obj:`PetriNet`): A reference to the PetriNet that holds the port.
        inside_link (str): The name of the internal PetriNet element the port
                is connected to:
                - if it is a place: the port is a `provide port`;
                - if it is a transition: the port is a `use port`.
        method (str): Name of a PetriNet method called by a `provide port`.

    Attributes:
        name (str): Name of the port.
        net (:obj:`PetriNet`): A reference to the PetriNet that holds the port.
        type (str): Type of the port (either `provide` or `use`).
        state (bool): True if the port is active.
        inside_link (str): The name of the internal PetriNet element the port
                is connected to:
                - if it is a place: the port is a `provide port`;
                - if it is a transition: the port is a `use port`.
        method (str, optional): Name of a PetriNet method called by a `provide
                port`.
        outside_link (:obj:`list of :obj:`Port`): A list of references to the
                remote ports this port is connected to.
    """

    def __init__(self, name, net, inside_link, method=None):
        self.name = name
        self.net = net
        self.type = None
        self.state = False
        self.inside_link = inside_link
        self.method = method or name
        self.outside_links = []

        # TODO: add an error when user has not specified a method for the
        # provide port

        # If provide port:
        #   Create a method in the port pointing to the user-defined method
        #   based on the same name, or provided as an argument.
        if inside_link in net.places:
            self.type = "provide"
            setattr(self, name, getattr(net.model, self.method))
        # If use port:
        #   1. Create an attribute in the port currently set to None, which
        #       will point to the method of a remote port thank to the
        #       `connect` method;
        #   2. Add a condition in the transition to call that method.
        elif inside_link in net.transitions:
            self.type = "use"
            setattr(self, self.name, None)
            # the line below is useless as it points to None just above :)
            # need to update that at connection time
            setattr(self.net.model, self.name, getattr(self, self.name))
            self.net.transitions[self.inside_link].add_condition(self.name)
        else:
            raise Exception(
                'Trying to map port "%s" to non-existing element "%s"'
                % (name, inside_link))

    def toggle_state(self, state=None):
        """Used to toggle the state of the port."""
        self.state = not self.state if state is None else state
        # When a provide port is activated, a notification is sent to the
        # automaton to trigger the remote use port:
        self.notify()

    def connect(self, outside_link):
        """
        This method connects two ports by calling the `link_to` method from
        both sides.

        Args:
            outside_link (:obj:`Port`): A reference to the remote port.
        """
        self.link_to(outside_link)
        outside_link.link_to(self)
        # Once created at both side, notifications are sent to the automaton if
        # the component is initialized:
        if self.net.get_place(self.net.initial).state:
            self.notify()
        if outside_link.net.get_place(outside_link.net.initial).state:
            outside_link.notify()

    def link_to(self, outside_link):
        """
        This method links a local port to a remote port, and create the related
        attributes.

        Args:
            outside_link (:obj:`Port`): A reference to the remote port.
        """
        if outside_link not in self.outside_links:
            self.outside_links.append(outside_link)
            # If the local port is a "use": connect local port to remote port
            if self.inside_link in self.net.transitions:
                # Make the local port method to point to the remote port method:
                setattr(self, self.name, getattr(outside_link,
                    outside_link.name))
                # Override the default value (i.e. None) of the PetriNet method
                # related to this port, set at its creation, to point to the
                # port method set just above:
                setattr(self.net.model, self.name, getattr(self, self.name))

    def notify(self):
        """Send a notification to the automaton if it is set."""
        # Must fill a queue which will be processed by threads
        if self.type == "provide" and self.net.automaton:
            self.net.automaton.notify(self)


class PetriNet(object):
    """
    Describes a PetriNet modelling a software component's deployment process.

    Args:
        model (:obj:`PetriNet`, optional): A reference to an instance of the
            PetriNet.
        places (dict(str: :obj:`Place`), optional): Dictionary of places.
        transitions (dict(str: :obj:`Transition`), optional): Dictionary of
            transitions.
        ports (dict(str: :obj:`Port`), optional): Dictionary of ports.
        initial (str, optional): Name of the initial place.

    Attributes:
        model (:obj:`PetriNet`): A reference to an instance of the PetriNet.
        places (dict(str: :obj:`Place`)): Dictionary of places.
        transitions (dict(str: :obj:`Transition`)): Dictionary of transitions.
        ports (dict(str: :obj:`Port`)): Dictionary of ports.
        current_places (dict(str: :obj:`Place`)): Dictionary containing the
            current active places in the PetriNet.
        model.current_places (list(str)): List containing the current active
            places' names in the model.
        initial (str): Name of the initial place.
        automaton (:obj:`Automaton`): A reference to an automaton.
    """

    def __init__(self, model=None, places=None, transitions=None, ports=None,
            initial=None):
        
        self.model = self if model is None else model 
        self.places = {}
        self.transitions = {}
        self.ports = {}
        self.current_places = {}
        self.model.current_places = set()
        self.initial = None
        self.automaton = None
        self.name = None
        
        # Add places to the PetriNet's:
        if places is not None:
            places = listify(places)
            for place in places:
                # Places can be set as objects or strings:
                if isinstance(place, string_types):
                    place = Place(place)
                self.places[place.name] = place
                setattr(self.model, 'is_%s' % place.name,
                        partial(self.is_place, place.name))

        # Add transitions to the PetriNet's:
        if transitions is not None:
            transitions = listify(transitions)
            for transition in transitions:
                self.add_transition(**transition)

        # Add ports to the PetriNet's:
        if ports is not None:
            ports = listify(ports)
            for port in ports:
                self.add_port(**port)

        # Set the initial place:
        if initial is not None:
            if initial not in self.places:
                raise ValueError(
                        'Initial place "%s" is not in the list of valid '
                        'places.' % initial)
            self.initial = initial

    def is_place(self, place_name):
        """Returns True if a place is active, given its name."""
        return place in self.current_places

    def get_place(self, place):
        """Returns a place if it exists in the PetriNet, given its name."""
        if place not in self.places:
            raise Exception('The place "%s" does not exist.' % place)
            return None
        else:
            return self.places[place]

    def is_initialized(self):
        """Return `True` if the PetriNet has been initialized"""
        if not self.initial:
            raise Exception('The component has no initial state.')
            return 1
        return self.get_place(self.initial).state

    def update_net(self, src, dest):
        """
        Update the state of a PetriNet given two places.

        This method moves a token from a source place to a destination place,
        and activates the potential related local and remote ports.

        Args:
            src (str): Name of the source place.
            dest (str): Name of the destination place.
        """

        # Moving the token from the source place means here to decrement its
        # outgoing transition counter, and deactivate the place if there is no
        # more outgoing transitions.
        # Note: it does not make sense for the initial state. In such case,
        # ``src=None`` so the value of ``src`` is checked first:
        if src:
            src_place = self.get_place(src)
            src_place.outgoing -= 1
            if src_place.outgoing == 0:
                del self.current_places[src]
                self.model.current_places.discard(src)

        dest_place = self.get_place(dest)
        self.current_places[dest] = dest_place
        self.model.current_places.add(dest)
        # Update the number of incoming transitions for the destination place
        # if necessary:
        if dest_place.incoming < 2:
            # Activate the place:
            dest_place.toggle_state()
            # Activate the ports related to the state
            # TODO: find a more efficient/stylish way here:
            for port in self.ports.values():
                if port.inside_link == dest:
                    port.toggle_state(True)
        else:
            dest_place.incoming -= 1

    def add_transition(self, name, source, dest, callbacks=[],
            conditions=None):
        """
        Add a transition between two places given their names.

        Args:
            name (str): Name of the transition.
            source (str): Name of the source place.
            dest (str): Name of the destination place.
            callbacks (list(str), optional): List of names referring to
                user-defined methods.
            conditions (list(str), optional): List of names referring to
                user-defined methods which must return a boolean.
        """
        if source not in self.places:
            raise Exception(
                    'The source "%s" of the transition "%s" is not a place of '
                    'the PetriNet.' % (source, name))
        if dest not in self.places:
            raise Exception(
                    'The destination "%s" of the transition "%s" is not a '
                    ' place of the PetriNet.' % (dest, name))

        # Create the transition and the related method in the model:
        if name not in self.transitions:
            self.transitions[name] = Transition(name, self, source, dest,
                    conditions or [])
            setattr(self.model, name, self.transitions[name].fire)

        # Set a set of callbacks for the transition (can be a list of methods
        # or a string):
        func = getattr(self.model, 'func_' + name, None)
        if func is not None:
            self.transitions[name].add_callback(func)

        for callback in callbacks:
            if isinstance(callback, string_types):
                func = getattr(self.model, callback, None)
                if func is None:
                    raise Exception(
                            'The method "%s" is not defined.' % callback)
            elif isinstance(callback, Callable):
                func = callback
            self.transitions[name].add_callback(func)

    def get_transitions(self, place):
        """Returns the outgoing transitions given a place name."""
        return {name: transition for name,transition in self.transitions.items()
                    if transition.src == place.name}

    def get_current_transitions(self):
        """Returns the available transitions regarding the current state."""
        return [name for name,transition in self.transitions.items()
                if transition.state
                and self.get_place(transition.src).state
                and transition.src in self.current_places]

    def add_port(self, name, inside_link, method=None):
        """
        Add a port to the PetriNet and map it to a place or a transition.

        Args:
            name (str): Name of the port.
            inside_link (str): Name of the internal element linked to the port.
            method (str): Name of a PetriNet method called by a `provide port`.
        """
        self.ports[name] = Port(name, self, inside_link, method)

    def auto_connect(self, remote_component):
        """
        Automatically connect local ports to remote ports given a PetriNet
        based on their names.

        Args:
            remote_component (:obj:`PetriNet`): A reference to another
                PetriNet model.
        """
        remote_component = remote_component.net
        for name, port in self.ports.items():
            # If same name is found on remote component, let's connect them:
            if name in remote_component.ports:
                remote_port = remote_component.ports[name]
                port.connect(remote_port)

    def connect(self, port_name, remote_component, remote_port_name):
        """
        Connect a named local port to a named remote port.
        """
        # Let's do some sanity checks
        if port_name in self.ports and remote_port_name in remote_component.ports:
            port = self.ports[port_name]
            remote_port = remote_component.ports[remote_port_name]
            port.connect(remote_port)        

    def initialize(self):
        """Initialize the PetriNet by setting a token in the initial place."""
        self.update_net(None, self.initial)

