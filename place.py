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

    def getplace(self):
        """
        This method returns the Place object associated to the dock

        :return: a Place object
        """
        return self.mother

    def gettype(self):
        """
        This method returns the type of dock

        :return: self.DOCK_TYPE
        """
        return self.DOCK_TYPE

    def get_transition(self):
        return self.transition


class Place (object):
    """This Place class is used to create a place of a component.

        A place represents an evolution state in the deployment of a component.
    """

    def __init__(self,name):
        self.name = name
        self.input_docks = []
        self.output_docks = []
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
        self.input_docks.append(new_dock)
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
        self.output_docks.append(new_dock)
        return new_dock

    def getname(self):
        """
        This method returns the name of the place

        :return: name
        """
        return self.name

    def get_inputdocks(self):
        """
        This method returns the list of input docks of the place

        :return: self.input_docks
        """
        return self.input_docks

    def get_outputdocks(self):
        """
        This method returns the list of output docks of the place

        :return: self.output_docks
        """
        return self.output_docks

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
