from mad import *
from transitions import *


class User(Component):

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
            'ipprov': (DepType.DATA_USE, ['init']),
            'service': (DepType.USE, ['config', 'start'])
        }

    def init(self):
        time.sleep(10)

    def config(self):
        time.sleep(5)

    def start(self):
        time.sleep(5)