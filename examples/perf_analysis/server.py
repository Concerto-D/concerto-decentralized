import time

from concerto.all import *
from examples.utils import *

class Server(Component):

    def create(self):
        self.places = [
            'undeployed',
            'allocated',
            'running'
        ]

        self.transitions = {
            'allocate': ('undeployed', 'allocated', 'deploy', 0, self.allocate),
            'run': ('allocated', 'running', 'deploy', 0, self.run),
            'update': ('running', 'allocated', 'stop', 0, self.update),
            'cleanup': ('running', 'allocated', 'stop', 0, self.cleanup)
        }

        self.dependencies = {
            'ip': (DepType.DATA_PROVIDE, ['allocated']),
            'service': (DepType.PROVIDE, ['running'])
        }
        
        self.initial_place = 'undeployed'

    def __init__(self, t_sa=4., t_sr=4., t_su=1., t_sc=0.5):
        self.my_ip = None
        self.t_sa = t_sa
        self.t_sr = t_sr
        self.t_su = t_su
        self.t_sc = t_sc
        Component.__init__(self)

    def allocate(self):
        self.print_color("allocating resources")
        time.sleep(self.t_sa)
        self.my_ip = "123.124.1.2"
        self.write('ip', self.my_ip)
        self.print_color("finished allocation (IP: %s)" % self.my_ip)

    def run(self):
        self.print_color("preparing to run")
        time.sleep(self.t_sr)
        self.print_color("running")

    def update(self):
        self.print_color("updating")
        time.sleep(self.t_su)
        self.print_color("updated")

    def cleanup(self):
        self.print_color("cleaning up")
        time.sleep(self.t_sc) 
        self.print_color("cleaned up")
