# -*- coding: utf-8 -*-

"""
.. module:: dependency
   :synopsis: this file contains the Dependency class.
"""

from enum import Enum
from typing import Dict, Tuple, List, Set

class DepMandatory(Enum):
    """
    This class is not instanciated and is an Enumeration. It is used to know
    if a dependency is mandatory or optional.
    """

    MANDATORY = 0
    OPTIONAL = 1

class DepType(Enum):
    """
    This class is not instanciated. It handles the types of dependencies.
    """

    USE = 0
    DATA_USE = 1
    PROVIDE = 2
    DATA_PROVIDE = 3

    @staticmethod
    def valid_types(type1, type2):
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

    def __init__(self, component, name : str, type : DepType):
        self.component = component
        self.name = name
        self.type = type
        self.connections : Set = set()
        self.nb_users = 0
        self.data = None
    
    def get_component(self):
        """
        This method returns the component of the dependency

        :return: component
        """
        return self.component

    def get_name(self) -> str:
        """
        This method returns the name of the dependency

        :return: name
        """
        return self.name

    def get_type(self) -> DepType:
        """
        This method returns the type of the dependency DepType

        :return: type
        """
        return self.type
    
    def get_data(self):
        if self.get_type() is not DepType.DATA_PROVIDE:
            raise Exception("Trying to get data from dependency '%s' which is not of type data provide"%self.get_name())
        return self.data
    
    def read(self):
        if self.get_type() is not DepType.DATA_USE:
            raise Exception("Trying to read from dependency '%s' which is not of type data use"%self.get_name())
        for c in self.connections:
            if c.is_active():
                return c.get_provide_dep().get_data()
        raise Exception("Trying to read from dependency '%s' which is not served"%self.get_name())
    
    def write(self, data):
        if self.get_type() is not DepType.DATA_PROVIDE:
            raise Exception("Trying to write to dependency '%s' which is not of type data provide"%self.get_name())
        self.data = data

    def is_connected(self) -> bool:
        """
        This method indicates if the dependency is connected or not, ie if it is
        already connected to another dependency within the assembly

        :return: True if connected, False otherwise
        """
        return len(self.connections) > 0

    def connect(self, c):
        """
        This method set self.free to False to indicate that the dependency
        has been connected in the assembly. Note that a dependency can be
        connected more than once, however this method is used to throw a
        warning when dependencies are not connected.

        :return: self.free
        """
        self.connections.add(c)
    
    def disconnect(self, c):
        self.connections.remove(c)
    
    def is_in_use(self) -> bool:
        return self.nb_users > 0
    
    def start_using(self):
        self.nb_users += 1
    
    def stop_using(self):
        self.nb_users -= 1
        
    def is_served(self):
        if self.type != DepType.DATA_USE and self.type != DepType.USE:
            raise Exception("Trying to check if a (data) provide port is served")
        for c in self.connections:
            if c.is_active():
                return True
        return False
    
    def is_locked(self):
        if self.type != DepType.DATA_PROVIDE and self.type != DepType.PROVIDE:
            raise Exception("Trying to check if a (data) use port is active")
        for c in self.connections:
            if c.is_locked():
                return True
        return False
