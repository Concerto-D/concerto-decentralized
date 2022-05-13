from concerto.assembly import Assembly
from examples.decentralized.client import Client
from examples.decentralized.server import Server
from examples.decentralized.server_mysql import ServerMysql


class ServerMysqlAssembly(Assembly):
    def __init__(self):
        Assembly.__init__(self)
        self.server = ServerMysql()
        self.client_server = Client()
        self.name = "server_mysql"
