from concerto.all import *
from concerto.utility import empty_transition


class User(Component):

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
            'serviceu': (DepType.USE, ['start'])
        }
        
