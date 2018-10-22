import time

from madpp.all import *
from examples.utils import *

class Client(Component):

    def create(self):
        self.places = [
            'off',
            'waiting_server_ip',
            'configured',
            'running'
        ]

        self.transitions = {
            'configure1': ('off', 'waiting_server_ip', 'install_start', 0, self.configure1),
            'configure2': ('waiting_server_ip', 'configured', 'install_start', 0, self.configure2),
            'start': ('configured', 'running', 'install_start', 0, self.start),
            'suspend': ('running', 'configured', 'stop', 0, self.suspend)
        }

        self.dependencies = {
            'server_ip': (DepType.DATA_USE, ['configure2']),
            'service': (DepType.USE, ['start'])
        }
        
        self.initial_place = 'off'

    def __init__(self):
        self.server_ip = None
        Component.__init__(self)

    def configure1(self):
        tprint("Client: configuration (1/2)")
        time.sleep(1)
        tprint("Client: waiting for server IP")

    def configure2(self):
        self.server_ip = self.read('server_ip')
        tprint("Client: configuration (2/2) [server IP: %s]" % self.server_ip)
        time.sleep(1)
        tprint("Client: configured")

    def start(self):
        tprint("Client: starting")
        time.sleep(1)
        tprint("Client: running")

    def suspend(self):
        tprint("Client: suspending")
        time.sleep(2)
        tprint("Client: suspended")
