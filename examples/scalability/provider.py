from mad import *
from examples.scalability.transitions import *


class Provider(Component):

    places = [
        'waiting',
        'started'
    ]

    transitions = {
        'start': (DryRun(), 'waiting', 'started')
    }

    dependencies = {
        'service': (DepType.PROVIDE, ['started'])
    }