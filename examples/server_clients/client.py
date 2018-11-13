import time

from madpp.all import *
from madpp.utility import *

class Client(Component):

    def create(self):
        self.places = [
            'off',
            'waiting_server_ip',
            'configured',
            'running',
            'paused'
        ]
        
        self.groups = {
            'using_service': ['running', 'paused']
        }

        self.transitions = {
            'configure1': ('off', 'waiting_server_ip', 'install_start', 0, self.configure1),
            'configure2': ('waiting_server_ip', 'configured', 'install_start', 0, self.configure2),
            'prepare_start': ('configured', 'paused', 'install_start', 0, self.prepare_start),
            'start': ('paused', 'running', 'install_start', 0, self.start),
            'suspend1': ('running', 'paused', 'stop', 0, self.suspend1),
            'suspend2': ('paused', 'configured', 'stop', 0, self.suspend2)
        }

        self.dependencies = {
            'server_ip': (DepType.DATA_USE, ['configure2']),
            'service': (DepType.USE, ['using_service'])
        }
        
        self.initial_place = 'off'

    def __init__(self):
        self.server_ip = None
        Component.__init__(self)

    def configure1(self):
        self.print_color("configuration (1/2)")
        time.sleep(1)
        self.print_color("waiting for server IP")

    def configure2(self):
        self.server_ip = self.read('server_ip')
        self.print_color("configuration (2/2) [server IP: %s]" % self.server_ip)
        time.sleep(1)
        self.print_color("configured")

    def prepare_start(self):
        self.print_color("waiting for server service")

    def start(self):
        self.print_color("starting")
        time.sleep(1)
        self.print_color("running")

    def suspend1(self):
        self.print_color("suspending")
        time.sleep(2)

    def suspend2(self):
        self.print_color("suspended")
