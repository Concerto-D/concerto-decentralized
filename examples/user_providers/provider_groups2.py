from mad import *
from transitions import *


class ProviderGroups2(Component):

    def create(self):
        self.places = [
            'waiting',
            'initiated',
            'configured',
            'started'
        ]

        self.transitions = {
            'pinit': ('waiting', 'initiated', Init().run),
            'pconfig': ('initiated', 'configured', Config().run),
            'pstart': ('configured', 'started', Start().run)
        }

        self.dependencies = {
            'service': (DepType.PROVIDE, ['started', 'configured'])
        }