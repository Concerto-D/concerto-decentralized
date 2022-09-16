# -*- coding: utf-8 -*-

"""
.. module:: dependency
   :synopsis: this file contains the Dependency class.
"""

from enum import Enum
from typing import Set

from concerto import communication_handler


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

    @staticmethod
    def compute_opposite_type(type):
        if type == DepType.USE:
            return DepType.PROVIDE
        if type == DepType.DATA_USE:
            return DepType.DATA_PROVIDE
        if type == DepType.PROVIDE:
            return DepType.USE
        if type == DepType.DATA_PROVIDE:
            return DepType.DATA_USE


class Dependency(object):
    """
    This class represents a dependency.
    """

    def __init__(self, component, name: str, dep_type: DepType):
        self._component = component
        self._p_name = name
        self._p_type = dep_type
        self._p_connections: Set = set()
        self._p_is_refusing: bool = False
        self._p_nb_users = 0
        self._p_data = None

    @property
    def _p_id(self):
        return f"{self._component.name}-{self._p_name}"

    def get_component_name(self):
        """
        This method returns the component of the dependency

        :return: component
        """
        return self._component.name

    def get_name(self) -> str:
        """
        This method returns the name of the dependency

        :return: name
        """
        return self._p_name

    def get_type(self) -> DepType:
        """
        This method returns the type of the dependency DepType

        :return: type
        """
        return self._p_type

    def check_get_data_is_provide(self):
        if self.get_type() is not DepType.DATA_PROVIDE and self.get_type() is not DepType.PROVIDE:
            raise Exception(
                "Trying to get data from dependency '%s' which is not of type provide or data provide" % self.get_name())

    def check_write_data_is_provide(self):
        if self.get_type() is not DepType.DATA_PROVIDE and self.get_type() is not DepType.PROVIDE:
            raise Exception("Trying to write to dependency '%s' which is not of type provide or data provide" % self.get_name())

    def get_data(self):
        self.check_get_data_is_provide()
        return self._p_data

    def read(self):
        if self.get_type() is not DepType.DATA_USE and self.get_type() is not DepType.USE:
            raise Exception("Trying to read from dependency '%s' which is not of type use or data use" % self.get_name())
        for c in self._p_connections:
            if c.is_active():
                return c.get_provide_dep().get_data()
        raise Exception("Trying to read from dependency '%s' which is not served" % self.get_name())

    def write(self, data):
        self.check_write_data_is_provide()
        self._p_data = data

    def connect(self, c):
        """
        This method set self.free to False to indicate that the dependency
        has been connected in the assembly. Note that a dependency can be
        connected more than once, however this method is used to throw a
        warning when dependencies are not connected.

        :return: self.free
        """
        self._p_connections.add(c)

    def disconnect(self, c):
        self._p_connections.remove(c)

    def is_in_use(self) -> bool:
        return self._p_nb_users > 0

    def start_using(self):
        self._p_nb_users += 1

        # S'il y a au moins une dépendance remote, il faut la prévenir de la mise à jour du nb_users
        for conn in self._p_connections:
            if type(conn.get_opposite_dependency(self)).__name__ == 'RemoteDependency':
                communication_handler.send_nb_dependency_users(self._p_nb_users, self.get_component_name(), self._p_name)

    def stop_using(self):
        self._p_nb_users -= 1

        # S'il y a au moins une dépendance remote, il faut la prévenir de la mise à jour du nb_users
        for conn in self._p_connections:
            if type(conn.get_opposite_dependency(self)).__name__ == 'RemoteDependency':
                communication_handler.send_nb_dependency_users(self._p_nb_users, self.get_component_name(), self._p_name)

    def is_refusing(self):
        return self._p_is_refusing

    def is_allowed(self):
        if self._p_type != DepType.DATA_USE and self._p_type != DepType.USE:
            raise Exception("Trying to check if a provide port is allowed")
        for c in self._p_connections:
            if c.get_provide_dep().is_refusing():
                return False
        return True

    def set_refusing_state(self, value: bool):
        self._p_is_refusing = value

        # S'il y a au moins une dépendance remote, il faut la prévenir du fait que le provide n'accepte
        # plus d'utilisation
        if any(type(conn.get_opposite_dependency(self)).__name__ == 'RemoteDependency' for conn in self._p_connections):
            communication_handler.send_refusing_state(value, self.get_component_name(), self._p_name)

    def is_served(self):
        """
        Est ce que le use port est provisionné ?
        """
        if self._p_type != DepType.DATA_USE and self._p_type != DepType.USE:
            raise Exception("Trying to check if a (data) provide port is served")
        for c in self._p_connections:
            if c.is_active():
                return True
        return False

    def is_locked(self):
        """
        Est que le provide port est utilisé par au moins un use port ?
        """
        if self._p_type != DepType.DATA_PROVIDE and self._p_type != DepType.PROVIDE:
            raise Exception("Trying to check if a (data) use port is active")
        for c in self._p_connections:
            if c.is_locked():
                return True
        return False

    def __str__(self):
        return self._p_name

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self._p_name == other._p_name and self._component == other._component

    def __hash__(self):
        return hash((self._p_name, self._component))
