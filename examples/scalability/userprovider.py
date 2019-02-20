from concerto.all import *
from concerto.utility import empty_transition


class UserProvider(Component):

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]
        
        self.initial_place = 'waiting'

        self.transitions = {
            'start': ('waiting', 'started', 'start', 0, empty_transition)
        }

        self.dependencies = {
            'serviceu': (DepType.USE, ['start']),
            'servicep': (DepType.PROVIDE, ['started'])
        }
