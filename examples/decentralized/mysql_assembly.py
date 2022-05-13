from concerto.assembly import Assembly
from examples.decentralized.mysql import Mysql


class MysqlAssembly(Assembly):
    def __init__(self):
        Assembly.__init__(self)
        self.mysql = Mysql()
        self.name = "mysql_assembly"
