from concerto.assembly import Assembly
from examples.decentralized.client_python import ClientPython
from examples.decentralized.python_install import PythonInstall


class ClientsPython(Assembly):
    def __init__(self, n):
        Assembly.__init__(self)
        self.client = ClientPython()
        self.python_install = PythonInstall()
        self.name = "client"+n
