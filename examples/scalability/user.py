from mad import *
from examples.scalability.transitions import *


class User(Component):

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]

        self.transitions = {
            'start': ('waiting', 'started', DryRun().run)
        }

        self.dependencies = {
            'serviceu': (DepType.USE, ['start'])
        }