#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: place
   :synopsis: this file contains the Place and Dock classes.
"""

class Dock(object):
    """This Dock class is used to create a dock.

        A dock is an input or an output of a place.
    """

    DOCK_TYPE = 0

    def __init__(self, place, type, transition):
        self.mother = place
        self.DOCK_TYPE = type
        self.transition = transition

    def get_place(self):
        """
        This method returns the Place object associated to the dock

        :return: a Place object
        """
        return self.mother

    def get_type(self):
        """
        This method returns the type of dock

        :return: self.DOCK_TYPE
        """
        return self.DOCK_TYPE

    def get_transition(self):
        return self.transition
    
    def get_behavior(self):
        return self.get_transition().get_behavior()


class Place (object):
    """This Place class is used to create a place of a component.

        A place represents an evolution state in the deployment of a component.
    """

    def __init__(self,name):
        self.name = name
        self.input_docks = {}  # dictionary behavior -> docks[]
        self.output_docks = {} # dictionary behavior -> docks[]
        self.provides = []

    def create_input_dock(self, transition):
        """
        This method creates an additional input dock to the current place.
        This method is called by Transition. An input dock of a place
        corresponds to a destination dock of a transition.

        :param transition: the transition to which the dock will be associated
        :return: the new input dock
        """
        new_dock = Dock(self, 0, transition)
        behavior = transition.get_behavior()
        if behavior not in self.input_docks:
            self.input_docks[behavior] = []
        self.input_docks[behavior].append(new_dock)
        return new_dock

    def create_output_dock(self, transition):
        """
        This method creates an additional output dock to the current place.
        This method is called by Transition. An output dock of a place
        corresponds to a source dock of a transition.

        :param transition: the transition to which the dock will be associated
        :return: the new output dock
        """
        new_dock = Dock(self, 1, transition)
        behavior = transition.get_behavior()
        if behavior not in self.output_docks:
            self.output_docks[behavior] = []
        self.output_docks[behavior].append(new_dock)
        return new_dock

    def get_name(self):
        """
        This method returns the name of the place

        :return: name
        """
        return self.name

    def get_input_docks(self, behavior):
        """
        This method returns the list of input docks of the place

        :return: self.input_docks[behavior] if not empty, [] otherwise
        """
        if behavior not in self.input_docks:
            return []
        else:
            return self.input_docks[behavior]

    def get_output_docks(self, behavior):
        """
        This method returns the list of output docks of the place

        :return: self.output_docks[behavior] if not empty, [] otherwise
        """
        if behavior not in self.output_docks:
            return []
        else:
            return self.output_docks[behavior]

    def add_provide(self, dep):
        """
        This method is used to add a provide dependency bound to the current
        place

        :param dep: the provide dependency to add
        """
        self.provides.append(dep)

    def get_provides(self):
        """
        This method returns the list of provide dependencies bound to the
        current place

        :return: self.provides
        """
        return self.provides
