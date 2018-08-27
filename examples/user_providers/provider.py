from mad import *
from transitions import *


class Provider(Component):

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
            'ip': (DepType.DATA_PROVIDE, ['configured']),
            'service': (DepType.PROVIDE, ['started'])
        }