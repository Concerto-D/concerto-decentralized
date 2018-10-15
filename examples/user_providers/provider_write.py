from mad import *
import time


class ProviderWrite(Component):

    def create(self):
        self.places = [
            'waiting',
            'initiated',
            'configured',
            'started'
        ]

        self.transitions = {
            'init': ('waiting', 'initiated', 'install', self.init),
            'config': ('initiated', 'configured', 'install', self.config),
            'start': ('configured', 'started', 'install', self.start)
        }

        self.dependencies = {
            'ip': (DepType.DATA_PROVIDE, ['configured']),
            'service': (DepType.PROVIDE, ['started'])
        }
        
        self.initial_place = 'waiting'

    def init(self):
        time.sleep(10)
        self.write('ip', "192.168.0.2")

    def config(self):
        time.sleep(5)

    def start(self):
        time.sleep(5)
