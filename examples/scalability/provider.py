from mad import *
from examples.scalability.transitions import *


class Provider(Component):

    echo1 = "test1"
    echo2 = "test2"

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]

        self.transitions = {
            'start': ('waiting', 'started', DryRun().testargs, (self.echo1,
                                                                self.echo2))
        }

        self.dependencies = {
            'service': (DepType.PROVIDE, ['started'])
        }