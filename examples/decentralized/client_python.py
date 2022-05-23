from concerto.all import *


class ClientPython(Component):

    def create(self):
        self.places = [
            'off',
            'installed',
            'configured',
            'running',
            'paused'
        ]
        
        self.groups = {
            'using_service': ['running', 'paused'],
            'python_group': ['running', 'paused', 'configured', 'installed']
        }

        self.transitions = {
            'install1': ('off', 'installed', 'install_start', 0, self.install1),
            'install2': ('off', 'configured', 'install_start', 0, self.install2),
            'configure': ('installed', 'configured', 'install_start', 0, self.configure),
            'start': ('configured', 'running', 'install_start', 0, self.start),
            'suspend1': ('running', 'paused', 'stop', 0, self.suspend1),
            'suspend2': ('paused', 'configured', 'stop', 0, self.suspend2),
            'unconfigure': ('configured', 'installed', 'uninstall', 0, self.unconfigure),
            'uninstall': ('installed', 'off', 'uninstall', 0, self.uninstall)
        }

        self.dependencies = {
            'python': (DepType.USE, ['python_group']),
            'server_ip': (DepType.DATA_USE, ['configure']),
            'service': (DepType.USE, ['using_service'])
        }
        
        self.initial_place = 'off'

    def __init__(self):
        self.server_ip = None
        Component.__init__(self)

    def install1(self):
        self.print_color("installing (1/2)")
        time.sleep(2.)
        self.print_color("installed (1/2)")

    def install2(self):
        self.print_color("installing (2/2)")
        time.sleep(3.)
        self.print_color("installed (2/2)")

    def configure(self):
        self.server_ip = self.read('server_ip')
        self.print_color("configuring [server IP: %s]" % self.server_ip)
        time.sleep(1.)
        self.print_color("configured")

    def start(self):
        self.print_color("starting")
        time.sleep(1.)
        self.print_color("running")

    def suspend1(self):
        self.print_color("suspending")
        time.sleep(0.)

    def suspend2(self):
        time.sleep(1.)
        self.print_color("suspended")

    def unconfigure(self):
        time.sleep(1.)
        self.print_color("unconfigured")

    def uninstall(self):
        time.sleep(1.)
        self.print_color("uninstalled")

