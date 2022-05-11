# -*- coding: utf-8 -*-

"""
.. module:: proxy_dependency
   :synopsis: this file contains the ProxyDependency class.
"""
from concerto import communication_handler
from concerto.dependency import Dependency, DepType


class ProxyDependency(Dependency):
    """
    This class represents a proxy_dependency, meaning that it serves as an intermediary between this
    assembly an the one that host the real dependency.
    """

    def __init__(self, remote_component_name: str, name: str, dep_type: DepType):
        Dependency.__init__(self, None, name, dep_type)
        self.remote_component_name = remote_component_name

    def is_in_use(self) -> bool:
        """
        On fait dans le topic plutôt qu'en local car la dépendance est remote
        """
        return communication_handler.get_nb_dependency_users(self.remote_component_name, self.name) > 0

    # TODO [con] voir si on garde ça, ou si on compare les dépendances directement par référence
    def __eq__(self, other):
        return self.name == other.name and self.remote_component_name == other.remote_component_name

    def __hash__(self):
        return hash((self.name, self.remote_component_name))