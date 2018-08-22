from mad import *
from examples.scalability.transitions import *


class User(Component):

    places = [
        'waiting',
        'started'
    ]

    transitions = {
        'start': (DryRun(), 'waiting', 'started')
    }

    dependencies = {
        'serviceu': (DepType.USE, ['start'])
    }