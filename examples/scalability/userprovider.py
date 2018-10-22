from mad import *
from examples.scalability.transitions import *


class UserProvider(Component):

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]
        
        self.initial_place = 'waiting'

        self.transitions = {
            'start': ('waiting', 'started', 'start', 0, DryRun().run)
        }

        self.dependencies = {
            'serviceu': (DepType.USE, ['start']),
            'servicep': (DepType.PROVIDE, ['started'])
        }
