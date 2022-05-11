from concerto.assembly import Assembly
from examples.decentralized.client import Client


class Clients(Assembly):
    def __init__(self):
        Assembly.__init__(self)
        self.client = Client()
        self.client.set_color('\33[34m')
