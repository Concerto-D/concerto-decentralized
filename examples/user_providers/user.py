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
            'init': ('waiting', 'initiated', Init().run),
            'config': ('initiated', 'configured', Config().run),
            'start': ('configured', 'started', Start().run)
        }

        self.dependencies = {
            'ipprov': (DepType.DATA_USE, ['init']),
            'service': (DepType.USE, ['config', 'start'])
        }