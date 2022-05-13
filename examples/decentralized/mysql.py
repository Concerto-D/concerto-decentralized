from concerto.all import *


class Mysql(Component):

    def create(self):
        self.places = [
            'uninstalled',
            'installed',
            'running',
        ]

        self.transitions = {
            'install': ('uninstalled', 'installed', 'install_start', 0, self.install),
            'start': ('installed', 'running', 'install_start', 0, self.start),
            'stop': ('running', 'installed', 'uninstall', 0, self.stop),
            'uninstall': ('installed', 'uninstalled', 'uninstall', 0, self.uninstall)
        }

        self.dependencies = {
            'service': (DepType.PROVIDE, ['running'])
        }

        self.initial_place = 'uninstalled'

    def __init__(self):
        Component.__init__(self)

    def install(self):
        time.sleep(2.)
        self.print_color("installed")

    def start(self):
        time.sleep(1.)
        self.print_color("running")

    def stop(self):
        time.sleep(1.)
        self.print_color("stopped")

    def uninstall(self):
        time.sleep(1.)
        self.print_color("uninstalled")

