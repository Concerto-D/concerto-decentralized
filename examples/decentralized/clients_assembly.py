from concerto.assembly import Assembly
from examples.decentralized.client import Client
from examples.decentralized.python_install import PythonInstall


class Clients(Assembly):
    def __init__(self, n):
        Assembly.__init__(self)
        self.client = Client()
        self.python_install = PythonInstall()
        self.name = "client"+n
