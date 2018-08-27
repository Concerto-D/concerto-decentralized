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
            'init': ('waiting', 'initiated', self.init),
            'config': ('initiated', 'configured', self.config),
            'start': ('configured', 'started', self.start)
        }

        self.dependencies = {
            'ip': (DepType.DATA_PROVIDE, ['configured']),
            'service': (DepType.PROVIDE, ['started'])
        }

    def init(self):
        time.sleep(10)
        self.write('ip', "192.168.0.2")

    def config(self):
        time.sleep(5)

    def start(self):
        time.sleep(5)