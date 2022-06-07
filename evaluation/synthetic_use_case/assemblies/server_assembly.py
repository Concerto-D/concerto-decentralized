from concerto.assembly import Assembly
from evaluation.synthetic_use_case.assemblies.server import Server


class ServerAssembly(Assembly):
    components_types = {
        "Server": Server
    }

    remote_component_names = set()   # Filled on __init__
    remote_assemblies_names = set()  # Filled on __init__

    def __init__(self, config_dict, is_asynchrone=True):
        Assembly.__init__(self, "server_assembly", self.components_types, self.remote_component_names,
                          self.remote_assemblies_names, is_asynchrone)
        server_params = config_dict['transitions_time']['server']
        self.server = Server(**server_params)

        # Adding remote components and assemblies
        for i in range(config_dict['nb_deps_tot']):
            self.remote_component_names.add(f"dep{i}")
            self.remote_assemblies_names.add(f"dep_assembly_{i}")