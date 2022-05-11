from concerto.assembly import Assembly
from examples.decentralized.server import Server


class Servers(Assembly):
    def __init__(self):
        Assembly.__init__(self)
        self.server = Server()
