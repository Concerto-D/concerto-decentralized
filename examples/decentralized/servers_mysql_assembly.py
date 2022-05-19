from concerto.assembly import Assembly
from examples.decentralized.client import Client
from examples.decentralized.server_mysql import ServerMysql


class ServerMysqlAssembly(Assembly):
    components_types = {
        "ServerMysql": ServerMysql,
        "Client": Client
    }

    remote_component_names = {"client1", "python_install", "mysql"}

    def __init__(self):
        Assembly.__init__(self, "server_mysql_assembly", self.components_types, self.remote_component_names)
        self.server = ServerMysql()
        self.client_server = Client()
