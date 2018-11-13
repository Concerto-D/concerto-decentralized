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
        self.print_color("allocating resources")
        time.sleep(4)
        self.my_ip = "123.124.1.2"
        self.print_color("got IP %s" % self.my_ip)
        self.write('ip', self.my_ip)
        self.print_color("finished allocation")

    def run(self):
        self.print_color("preparing to run")
        time.sleep(4)
        self.print_color("running")

    def suspend(self):
        self.print_color("suspending")
        time.sleep(1)
        self.print_color("suspended")

    def restart(self):
        self.print_color("restarting")
        time.sleep(0.5) 
