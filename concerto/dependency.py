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
        self._p_nb_users = 0
        self._p_data = None

    @property
    def _p_id(self):
        return f"{self._component.name}_{self._p_name}"

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

    def get_data(self):
        if self.get_type() is not DepType.DATA_PROVIDE and self.get_type() is not DepType.PROVIDE:
            raise Exception(
                "Trying to get data from dependency '%s' which is not of type provide or data provide" % self.get_name())
        return self._p_data

    def read(self):
        # TODO: à comprendre, pk on récupère les data de seulement la première connection active ?
        # Pk on fait un get_provide_dep alors qu'on fait déjà la vérification dans le premier if ?
        if self.get_type() is not DepType.DATA_USE and self.get_type() is not DepType.USE:
            raise Exception("Trying to read from dependency '%s' which is not of type use or data use" % self.get_name())
        for c in self._p_connections:
            if c.is_active():
                return c.get_provide_dep().get_data()
        raise Exception("Trying to read from dependency '%s' which is not served" % self.get_name())

    def write(self, data):
        if self.get_type() is not DepType.DATA_PROVIDE and self.get_type() is not DepType.PROVIDE:
            raise Exception("Trying to write to dependency '%s' which is not of type provide or data provide" % self.get_name())
        self._p_data = data

    def is_connected(self) -> bool:
        """
        This method indicates if the dependency is connected or not, ie if it is
        already connected to another dependency within the assembly

        :return: True if connected, False otherwise
        """
        return len(self._p_connections) > 0

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

        # Si la dépendance d'en face associée à la même connection est remote,
        # alors il faut la prévenir de la mise à jour du nb_users
        for conn in self._p_connections:
            if type(conn.get_opposite_dependency(self)).__name__ == 'RemoteDependency':
                communication_handler.send_nb_dependency_users(self._p_nb_users, self.get_component_name(), self._p_name)

    def stop_using(self):
        self._p_nb_users -= 1

        # Si la dépendance d'en face associée à la même connection est remote,
        # alors il faut la prévenir de la mise à jour du nb_users
        for conn in self._p_connections:
            if type(conn.get_opposite_dependency(self)).__name__ == 'RemoteDependency':
                communication_handler.send_nb_dependency_users(self._p_nb_users, self.get_component_name(), self._p_name)

    def is_served(self):
        """
        Est ce que le use port est provisionné ?
        TODO à comprendre: pk un use port aurait plusieurs connections ? **Pour être générique**
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

    # TODO [con] voir si on garde ça, ou si on compare les dépendances directement par référence
    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self._p_name == other._p_name and self._component == other._component

    def __hash__(self):
        return hash((self._p_name, self._component))
