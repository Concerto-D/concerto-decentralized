from concerto.assembly import Assembly
from examples.decentralized.mysql import Mysql


class MysqlAssembly(Assembly):
    components_types = {
        "Mysql": Mysql
    }

    remote_component_names = {"server", "client_server", "client1", "python_install"}
    remote_assemblies_names = {"client_assembly1", "server_mysql_assembly"}

    def __init__(self):
        Assembly.__init__(self, "mysql_assembly", self.components_types, self.remote_component_names, self.remote_assemblies_names)
        self.mysql = Mysql()
