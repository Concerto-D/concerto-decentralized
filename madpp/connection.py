from madpp.dependency import DepType, Dependency
from madpp.component import *

class Connection(object):
    """
    This class is used by the assembly to store connections between components
    """

    def __init__(self, dep1 : Dependency, dep2 : Dependency):
        dep1type = dep1.get_type()
        if dep1type == DepType.PROVIDE or dep1type == DepType.DATA_PROVIDE:
            self.provide_dep = dep1
            self.use_dep = dep2
        else:
            self.provide_dep = dep2
            self.use_dep = dep1
        self.provide_dep.connect(self)
        self.use_dep.connect(self)
    
    def can_remove(self) -> bool:
        return not self.is_locked()
    
    def disconnect(self):
        self.provide_dep.disconnect(self)
        self.use_dep.disconnect(self)

    def get_tuple(self) -> Tuple[Component,Dependency,Component,Dependency]:
        return (self.provide_comp, self.provide_dep, self.use_comp, self.use_dep)

    def get_names(self) -> Tuple[str,str,str,str]:
        return (self.provide_comp.get_name(), self.provide_dep.get_name(), self.use_comp.get_name(), self.use_dep.get_name())
    
    def get_provide_comp(self) -> Component:
        return self.provide_dep.get_component()
    
    def get_provide_dep(self) -> Dependency:
        return self.provide_dep
    
    def get_use_comp(self) -> Component:
        return self.use_dep.get_component()
    
    def get_use_dep(self) -> Dependency:
        return self.use_dep

    def is_active(self) -> bool:
        return self.provide_dep.is_in_use()

    def is_locked(self) -> bool:
        return self.use_dep.is_in_use()
