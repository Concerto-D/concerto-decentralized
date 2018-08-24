from mad import *
from examples.scalability.transitions import *


class User(Component):

    places = [
        'waiting',
        'started'
    ]

    transitions = {
        'start': ('waiting', 'started', DryRun().run)
    }

    dependencies = {
        'serviceu': (DepType.USE, ['start'])
    }