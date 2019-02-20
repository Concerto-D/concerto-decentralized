import time

from concerto.all import *
from concerto.utility import *

class Client(Component):

    def create(self):
        self.places = [
            'off',
            'installed',
            'configured',
            'running',
            'paused'
        ]
        
        self.groups = {
            'using_service': ['running', 'paused']
        }

        self.transitions = {
            'install1': ('off', 'installed', 'install_start', 0, self.install1),
            'install2': ('off', 'configured', 'install_start', 0, self.install2),
            'configure': ('installed', 'configured', 'install_start', 0, self.configure),
            'start': ('configured', 'running', 'install_start', 0, self.start),
            'suspend1': ('running', 'paused', 'stop', 0, self.suspend1),
            'suspend2': ('paused', 'configured', 'stop', 0, self.suspend2)
        }

        self.dependencies = {
            'server_ip': (DepType.DATA_USE, ['configure']),
            'service': (DepType.USE, ['using_service'])
        }
        
        self.initial_place = 'off'

    def __init__(self, t_ci1=1., t_ci2=1., t_cc=1., t_cr=1., t_cs1=2., t_cs2=0.):
        self.server_ip = None
        self.t_ci1 = t_ci1
        self.t_ci2 = t_ci2
        self.t_cc = t_cc
        self.t_cr = t_cr
        self.t_cs1 = t_cs1
        self.t_cs2 = t_cs2
        Component.__init__(self)

    def install1(self):
        self.print_color("installing (1/2)")
        time.sleep(self.t_ci1)
        self.print_color("installed (1/2)")

    def install2(self):
        self.print_color("installing (2/2)")
        time.sleep(self.t_ci2)
        self.print_color("installed (2/2)")

    def configure(self):
        self.server_ip = self.read('server_ip')
        self.print_color("configuring [server IP: %s]" % self.server_ip)
        time.sleep(self.t_cc)
        self.print_color("configured")

    def start(self):
        self.print_color("starting")
        time.sleep(self.t_cr)
        self.print_color("running")

    def suspend1(self):
        self.print_color("suspending")
        time.sleep(self.t_cs1)

    def suspend2(self):
        self.print_color("suspended")
        time.sleep(self.t_cs2)
