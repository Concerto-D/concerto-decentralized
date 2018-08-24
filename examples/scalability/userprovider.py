from mad import *
from examples.scalability.transitions import *


class UserProvider(Component):

    places = [
        'waiting',
        'started'
    ]

    transitions = {
        'start': ('waiting', 'started', DryRun().run)
    }

    dependencies = {
        'serviceu': (DepType.USE, ['start']),
        'servicep': (DepType.PROVIDE, ['started'])
    }