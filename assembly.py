#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains the definition of an assembly of MAD (Madeus Application
Deployer) components.

"""

from automaton import Automaton
from utils.extra import printerr


class Assembly(object):
    """
    Define a MAD assembly.

    Args:
        components (list(list(:obj:`PetriNet`, str))): List of components to
            assemble.
        step (bool): If True, run the deployment process step by step
            (default=False).

    Examples:
        The following example shows how to instantiate an assembly of two MAD
        components named 'user' and 'provider':

        >>> # Instanciate the two components:
        >>> user = User()
        >>> provider = Provider()
        >>>
        >>> # Instanciate the assembly:
        >>> assembly = Assembly([
        ...     [user, 'user'],
        ...     [provider, 'provider']
        >>> ])

    """

    def __init__(self, components=None, step=False, dry_run=False,
                profiling=True):
        self.automaton = Automaton(components, step, dry_run, profiling)

    def add_instance(self, instance, name):
        self.automaton.add_component(instance, name)
       
    def add_instances(self, instances_with_names):
        self.automaton.add_components(instances_with_names)
       
    def connect(self, component1_name, port1_name, component2_name, port2_name):
        self.automaton.components[component1_name].net.ports[port1_name].connect(
                self.automaton.components[component2_name].net.ports[port2_name])
       
    def connect_multiple(self, array):
        for e in array:
            c1 = e[0]
            p1 = e[1]
            c2 = e[2]
            p2 = e[3]
            self.connect_multiple(c1, p1, c2, p2)
       
    def auto_connect(self, component1_name, component2_name):
        self.automaton.components[component1_name].net.auto_connect(
                self.automaton.components[component2_name])

    def run(self, component_name):
        self.automaton.run(component_name)

    def auto_run(self):
        # Make sure the components have been initialized:
        for _, comp in self.automaton.components.items():
            if not comp.net.is_initialized():
                comp.net.initialize()
        self.automaton.autorun()

    def set_dry_run(self, value):
        self.automaton.dry_run=value

    def check_dep(self, verbose=True):
        check = True
        for cname, comp in self.automaton.components.items():
            if comp.net.get_current_transitions() != [] \
                    or not comp.net.is_initialized():
                if verbose:
                    printerr("%s not in final state" % cname)
                check = False
        return check
