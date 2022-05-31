from concerto.assembly import Assembly
from evaluation.assemblies.dep import Dep


class DepAssembly(Assembly):
    components_types = {
        "Dep": Dep
    }

    remote_component_names = {"server"}
    remote_assemblies_names = {"server_assembly"}

    def __init__(self, n, is_asynchrone=True):
        Assembly.__init__(self, f"dep_assembly_{n}", self.components_types, self.remote_component_names,
                          self.remote_assemblies_names, is_asynchrone)
        self.dep = Dep(id=n)
