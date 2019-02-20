import time

from concerto.all import *
from concerto.utility import *

class Sysbench(Component):

    def create(self):
        self.places = [
            'uninstalled',
            'installed'
        ]

        self.transitions = {
            'install': ('uninstalled', 'installed', 'install', 0, self.install),
        }

        self.dependencies = {
            'sysbench_dir': (DepType.PROVIDE, ['installed'])
        }
        
        self.initial_place = 'uninstalled'
        

    def install(self):
        time.sleep(0.7)

