#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: dependency
   :synopsis: this file contains the Dependency class.
"""

from enum import Enum

class DepType(Enum):
    """
    This class is not instanciated. It handles the types of dependencies.
    """

    USE = 0
    DATA_USE = 1
    PROVIDE = 2
    DATA_PROVIDE = 3

    @staticmethod
    def validtypes(type1, type2):
        """
        This method checks if the two input types are compatible:
        - DepType.USE is compatible with DepType.PROVIDE
        - DepType.DATA_USE is compatible with DepType.DATA_PROVIDE

        :param type1: the first type DepType
        :param type2: the second type DepType
        :return True if the two types are compatible, False otherwise
        """
        validity = True
        if type1 == DepType.USE and type2 != DepType.PROVIDE:
            validity = False
        if type1 == DepType.DATA_USE and type2 != DepType.DATA_PROVIDE:
            validity = False
        if type1 == DepType.PROVIDE and type2 != DepType.USE:
            validity = False
        if type1 == DepType.DATA_PROVIDE and type2 != DepType.DATA_USE:
            validity = False
        return validity


class Dependency (object):
    """
    This class represents a dependency.
    """
    free = True

    def __init__(self, name, type, bindings):
        self.name = name
        self.type = type
        self.bindings = bindings # list of transitions or places

    def getname(self):
        """
        This method returns the name of the dependency

        :return: name
        """
        return self.name

    def gettype(self):
        """
        This method returns the type of the dependency DepType

        :return: type
        """
        return self.type

    def getbindings(self):
        """
        This method returns the place or the transition to which the
        dependency is bound. If the dependency is of type DepType.USE or
        DepType.DATA_USE it is bound to a transition, otherwise it is bound
        to a place.

        :return: the transition or the place self.binding
        """
        return self.bindings

    def isfree(self):
        """
        This method indicates if the dependency is free or not, ie if it is
        already connected to another dependency within the assembly

        :return: True if not connected, False if free
        """
        return self.free

    def connect(self):
        """
        This method set self.free to False to indicate that the dependency
        has been connected in the assembly. Note that a dependency can be
        connected more than once, however this method is used to throw a
        warning when dependencies are not connected.

        :return: self.free
        """
        self.free = False