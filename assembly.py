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

    def dump_dot_component(self, out, cname, comp):
        out.write("   subgraph cluster_"+cname+" {\n")
        out.write("      style=filled;\n")
        out.write("      color=lightgrey;\n")
        out.write("      label="+cname+";\n")
        out.write("      subgraph cluster_internal_"+cname+" {\n")
        out.write("         color=\"#707070\";\n")
        out.write("         label=\"\";\n")
        # PLACES
        out.write("         node [shape=box; style=filled; color=red];\n")
        for pl in comp.net.places:
            out.write("         "+cname+"_"+pl+";\n")
        # TRANSITIONS
        out.write("         node [shape=diamond; style=filled; color=lightblue];\n")
        for t in comp.net.transitions:
            out.write("         "+cname+"_"+t+";\n")
        for t in comp.net.transitions.values():
            out.write("         "+cname+"_"+t.src+" -> "+cname+"_"+t.name+";\n")
            out.write("         "+cname+"_"+t.name+" -> "+cname+"_"+t.dst+";\n")
        out.write("       }\n")
        # PORTS
        out.write("      node [shape=ellipse; style=filled; color=white];\n")
        for pt in comp.net.ports.values():
            out.write("        "+cname+"_"+pt.name+";\n") # PORT
            if pt.type == "provide":
                out.write("        "+cname+"_"+pt.inside_link+" -> "+ cname+"_"+pt.name+";\n")
            else:
                out.write("        "+cname+"_"+pt.name+" -> "+ cname+"_"+pt.inside_link+";\n")
        out.write("   }\n")

    def dump_dot_connection(self, out, cname, comp):
        for pt in comp.net.ports.values():
            if pt.type == "use":
                for cnx in pt.outside_links:
                    out.write("   "+cnx.net.name+"_"+cnx.name+" -> "+cname+"_"+pt.name+";\n")

    def dump_dot(self, filename):
        with open(filename, "w") as out:
            out.write("digraph MAD\n")
            out.write("{\n")
            for cname, comp in self.automaton.components.items():
                self.dump_dot_component(out, cname, comp)
            for cname, comp in self.automaton.components.items():
                self.dump_dot_connection(out, cname, comp)
            out.write("}\n")
