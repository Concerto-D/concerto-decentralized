from madpp.all import *
from examples.scalability.transitions import *


class User(Component):

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
            'serviceu': (DepType.USE, ['start'])
        }
        
