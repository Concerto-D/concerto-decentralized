from concerto.assembly import Assembly
from examples.decentralized.client import Client


class Clients(Assembly):
    def __init__(self, n):
        Assembly.__init__(self)
        self.client = Client()
        self.name = "client"+n

