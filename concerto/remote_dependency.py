# -*- coding: utf-8 -*-

"""
.. module:: remote_dependency
   :synopsis: this file contains the RemoteDependency class.
"""
from concerto import communication_handler
from concerto.dependency import Dependency, DepType


class RemoteDependency(Dependency):
    """
    This class represents a remote_dependency, it serves as an intermediary between this
    assembly an the one that host the real dependency.
    """

    def __init__(self, remote_component_name: str, name: str, dep_type: DepType):
        Dependency.__init__(self, None, name, dep_type)
        self.remote_component_name = remote_component_name

    def is_in_use(self) -> bool:
        """
        On fait dans le topic plutôt qu'en local car la dépendance est remote
        """
        return communication_handler.get_nb_dependency_users(self.remote_component_name, self._p_name) > 0

    @property
    def _p_id(self):
        return f"{self.remote_component_name}_{self._p_name}"

    def get_component_name(self):
        return self.remote_component_name

    # TODO [con] voir si on garde ça, ou si on compare les dépendances directement par référence
    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self._p_name == other._p_name and self.remote_component_name == other.remote_component_name

    def __hash__(self):
        return hash((self._p_name, self.remote_component_name))