from mad import *
from transitions import *


class UserGroups(Component):

    def create(self):

        self.places = [
            'waiting',
            'initiated',
            'configured',
            'started'
        ]

        self.transitions = {
            'uinit': ('waiting', 'initiated', InitShort().run),
            'uconfig': ('initiated', 'configured', ConfigLong().run),
            'ustart': ('configured', 'started', Start().run)
        }

        self.dependencies = {
            'service': (DepType.USE, ['uconfig', 'ustart'])
        }