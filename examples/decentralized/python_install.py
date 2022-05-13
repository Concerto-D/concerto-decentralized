from concerto.all import *


class PythonInstall(Component):

    def create(self):
        self.places = [
            'uninstalled',
            'installed',
        ]

        self.transitions = {
            'install': ('uninstalled', 'installed', 'install', 0, self.install),
            'uninstall': ('installed', 'uninstalled', 'uninstall', 0, self.uninstall)
        }

        self.dependencies = {
            'installation': (DepType.PROVIDE, ['installed']),
        }

        self.initial_place = 'uninstalled'

    def __init__(self):
        Component.__init__(self)

    def install(self):
        time.sleep(2.)
        self.print_color("installed")

    def uninstall(self):
        time.sleep(1.)
        self.print_color("uninstalled")

