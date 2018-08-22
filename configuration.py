#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: configuration
   :synopsis: this file contains the Configuration class.
"""

class Configuration (object):
    """
    This class represents a configuration of the Madeus formal model.
    A configuration is a set of objects (components, transitions, docks) on
    which tokens are placed. It represents the current state of an assembly.
    A configuration is used by the engine to know the state of a deployment.
    """

    """
    BUILD CONFIGURATION
    """

    # list of Component objects currently containing a token
    # all components are always into the configuration until the end of the
    # deployment so this list is not represented.

    # list of Transition objects currently containing a token
    transitions = []
    # list of Place objects currently containing a token
    places = []
    # list of activated connections
    connections = []
    input_docks = []
    output_docks = []

    def __init__(self, trans, pla, idocks, odocks, conn):
        self.transitions = trans
        self.places = pla
        self.connections = conn
        self.input_docks = idocks
        self.output_docks = odocks

    """
    UPDATE CONFIGURATION
    """

    def update_connections(self, conn):
        """
        This method updates the connections of the configuration

        :param conn: new list of active connections
        """
        self.connections = conn

    def update_transitions(self, trans):
        """
        This method updates the transitions of the configuration

        :param trans: new list of active transitions
        """
        self.transitions = trans

    def update_places(self, pla):
        """
        This method updates the places of the configuration

        :param pla: new list of active places
        """
        self.places = pla

    def update_input_docks(self, id):
        """
        This method updates the input docks of the configuration

        :param id: new list of active input docks
        """
        self.input_docks = id

    def update_output_docks(self, od):
        """
        This method updates the output docks of the configuration

        :param id: new list of active output docks
        :return:
        """
        self.output_docks = od

    """
    GET CONFIGURATION
    """

    def get_transitions(self):
        """
        This method returns the list of active transitions of the configuration

        :return: self.transitions
        """
        return self.transitions

    def get_places(self):
        """
        This method returns the list of active places of the configuration

        :return: self.places
        """
        return self.places

    def get_connections(self):
        """
        This method returns the list of active connections of the configuration

        :return: self.connections
        """
        return self.connections

    def get_input_docks(self):
        """
        This method returns the list of active input docks of the configuration

        :return: self.input_docks
        """
        return self.input_docks

    def get_output_docks(self):
        """
        This method returns the list of active output docks of the configuration

        :return: self.output_docks
        """
        return self.output_docks
