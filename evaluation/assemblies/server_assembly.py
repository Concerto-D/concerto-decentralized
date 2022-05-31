from concerto.assembly import Assembly
from evaluation.assemblies.server import Server


class ServerAssembly(Assembly):
    components_types = {
        "Server": Server
    }

    remote_component_names = {"dep0", "dep1"}
    remote_assemblies_names = {"dep_assembly_0", "dep_assembly_1"}

    def __init__(self, is_asynchrone=True):
        Assembly.__init__(self, "server_assembly", self.components_types, self.remote_component_names,
                          self.remote_assemblies_names, is_asynchrone)
        self.server = Server(1, [2, 3], 4, [5, 6], [7, 8])
