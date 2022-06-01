from concerto.assembly import Assembly
from evaluation.assemblies.dep import Dep
from evaluation.config import COMPONENTS_PARAMETERS


class DepAssembly(Assembly):
    components_types = {
        "Dep": Dep
    }

    remote_component_names = {"server"}
    remote_assemblies_names = {"server_assembly"}

    def __init__(self, p, nb_dep_tot, is_asynchrone=True):
        Assembly.__init__(self, f"dep_assembly_{p}", self.components_types, self.remote_component_names,
                          self.remote_assemblies_names, is_asynchrone)
        dep_params = COMPONENTS_PARAMETERS[f"dep{p}"]
        self.dep = Dep(*dep_params)

        # Adding remote components and assemblies
        for i in range(nb_dep_tot):
            if i != p:  # Not adding self
                self.remote_component_names.add(f"dep{i}")
                self.remote_assemblies_names.add(f"dep_assembly_{i}")
