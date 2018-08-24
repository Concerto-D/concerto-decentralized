from mad import *
from examples.scalability.transitions import *


class Provider(Component):

    echo1 = "test1"
    echo2 = "test2"

    places = [
        'waiting',
        'started'
    ]

    transitions = {
        'start': ('waiting', 'started', DryRun().testargs, (echo1, echo2))
    }

    dependencies = {
        'service': (DepType.PROVIDE, ['started'])
    }