import time

from madpp.all import *
from examples.utils import *

class Server(Component):

    def create(self):
        self.places = [
            'undeployed',
            'allocated',
            'running',
            'maintenance'
        ]

        self.transitions = {
            'allocate': ('undeployed', 'allocated', 'deploy', 0, self.allocate),
            'run': ('allocated', 'running', 'deploy', 0, self.run),
            'suspend': ('running', 'maintenance', 'stop', 0, self.suspend),
            'restart': ('maintenance', 'allocated', 'deploy', 1, self.restart)
        }

        self.dependencies = {
            'ip': (DepType.DATA_PROVIDE, ['allocated']),
            'service': (DepType.PROVIDE, ['running'])
        }
        
        self.initial_place = 'undeployed'

    def __init__(self):
        self.my_ip = None
        Component.__init__(self)

    def allocate(self):
        tprint("Server: allocating resources")
        time.sleep(4)
        self.my_ip = "123.124.1.2"
        tprint("Server: got IP %s" % self.my_ip)
        self.write('ip', self.my_ip)
        tprint("Server: finished allocation")

    def run(self):
        tprint("Server: preparing to run")
        time.sleep(4)
        tprint("Server: running")

    def suspend(self):
        tprint("Server: suspending")
        time.sleep(1)
        tprint("Server: suspended")

    def restart(self):
        tprint("Server: restarting")
        time.sleep(0.5) 
