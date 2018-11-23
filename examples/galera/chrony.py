import time

from madpp.all import *
from madpp.utility import *

class Chrony(Component):

    def create(self):
        self.places = [
            'uninstalled',
            'installed'
        ]

        self.transitions = {
            'install': ('uninstalled', 'installed', 'install', 0, self.install),
            'change_config': ('installed', 'installed', 'change_config', 0, self.change_config)
        }

        self.dependencies = {
            'chrony': (DepType.PROVIDE, ['installed']),
            'config': (DepType.DATA_USE, ['change_config'])
        }
        
        self.initial_place = 'uninstalled'
        

    def install(self):
        time.sleep(4.5)

    def change_config(self):
        self.print_color("Changing config to:\n%s"%self.read('config'))
        time.sleep(2)

