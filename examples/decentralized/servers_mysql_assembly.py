from concerto.assembly import Assembly
from examples.decentralized.client import Client
from examples.decentralized.server_mysql import ServerMysql


class ServerMysqlAssembly(Assembly):
    components_types = {
        "ServerMysql": ServerMysql,
        "Client": Client
    }

    remote_component_names = {"client1", "python_install", "mysql"}
    remote_assemblies_names = {"client_assembly1", "mysql_assembly"}

    def __init__(self, is_asynchrone=True):
        Assembly.__init__(self, "server_mysql_assembly", self.components_types, self.remote_component_names,
                          self.remote_assemblies_names, is_asynchrone)
        self.server = ServerMysql()
        self.client_server = Client()
