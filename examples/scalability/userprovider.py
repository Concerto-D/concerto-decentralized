from mad import *
from examples.scalability.transitions import *


class UserProvider(Component):

    places = [
        'waiting',
        'started'
    ]

    transitions = {
        'start': (DryRun(), 'waiting', 'started')
    }

    dependencies = {
        'serviceu': (DepType.USE, ['start']),
        'servicep': (DepType.PROVIDE, ['started'])
    }