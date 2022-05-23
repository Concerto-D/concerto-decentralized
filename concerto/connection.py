from concerto.component import *


class Connection:
    """
    This class is used by the assembly to store connections between components
    """

    def __init__(self, dep1: Dependency, dep2: Dependency):
        use_dep, provide_dep = self.compute_provide_use_deps(dep1, dep2)
        self._use_dep = use_dep
        self._provide_dep = provide_dep
        self._provide_dep.connect(self)
        self._use_dep.connect(self)

    @property
    def _p_id(self):
        return self.build_id_from_dependencies(self._use_dep, self._provide_dep)

    def can_remove(self) -> bool:
        return not self.is_locked()

    def disconnect(self):
        self._provide_dep.disconnect(self)
        self._use_dep.disconnect(self)

    # TODO: never used
    # def get_tuple(self) -> Tuple[Component, Dependency, Component, Dependency]:
    #     return self.get_provide_comp(), self.get_provide_dep(), self.get_use_comp(), self.get_use_dep()

    # def get_names(self) -> Tuple[str, str, str, str]:
    #     return (
    #         self.get_provide_comp().get_name(),
    #         self.get_provide_dep().get_name(),
    #         self.get_use_comp().get_name(),
    #         self.get_use_dep().get_name())

    # def get_provide_comp(self) -> Component:
    #     return self._provide_dep.get_component()

    # def get_use_comp(self) -> Component:
    #     return self._use_dep.get_component()

    def get_provide_dep(self) -> Dependency:
        return self._provide_dep

    def get_use_dep(self) -> Dependency:
        return self._use_dep

    def is_active(self) -> bool:
        return self._provide_dep.is_in_use()

    def is_locked(self) -> bool:
        return self._use_dep.is_in_use()

    def get_opposite_dependency(self, dep):
        return self._use_dep if dep == self._provide_dep else self._provide_dep

    @staticmethod
    def build_id_from_dependencies(dep1: Dependency, dep2: Dependency):
        use_dep, provide_dep = Connection.compute_provide_use_deps(dep1, dep2)
        return f"{use_dep._p_id}/{provide_dep._p_id}"


    @staticmethod
    def compute_provide_use_deps(dep1: Dependency, dep2: Dependency):
        if dep1.get_type() in [DepType.PROVIDE, DepType.DATA_PROVIDE]:
            provide_dep = dep1
            use_dep = dep2
        else:
            provide_dep = dep2
            use_dep = dep1

        return use_dep, provide_dep
