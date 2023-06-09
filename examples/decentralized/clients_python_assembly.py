from concerto.assembly import Assembly
from examples.decentralized.client_python import ClientPython
from examples.decentralized.python_install import PythonInstall
from examples.decentralized.server import Server


class ClientsPython(Assembly):
    components_types = {
        "ClientPython": ClientPython,
        "Server": Server,
        "PythonInstall": PythonInstall
    }

    remote_component_names = {"server", "client_server", "mysql"}
    remote_assemblies_names = {"mysql_assembly", "server_mysql_assembly"}

    def __init__(self, n, sleep_when_blocked=True):
        Assembly.__init__(self, "client_assembly" + n, self.components_types, self.remote_component_names,
                          self.remote_assemblies_names, sleep_when_blocked)
        self.client = ClientPython()
        self.server = Server()
        self.python_install = PythonInstall()
