from concerto.assembly import Assembly
from examples.decentralized.client_python import ClientPython
from examples.decentralized.python_install import PythonInstall
from examples.decentralized.server import Server


class ClientsPython(Assembly):
    def __init__(self, n):
        Assembly.__init__(self)
        self.client = ClientPython()
        self.server = Server()
        self.python_install = PythonInstall()
        self.name = "client_assembly"+n
