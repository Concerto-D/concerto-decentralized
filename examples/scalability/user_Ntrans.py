from mad import *
from examples.scalability.transitions import *


class UserNTrans(Component):

    places = [
        'waiting',
        'configured',
        'started'
    ]

    transitions = {
        'init': (DryRun(), 'waiting', 'configured'),
        't0': (DryRun(), 'configured', 'started')
    }

    dependencies = {
        'service': (DepType.USE, ['init'])
    }

    def createTransitions(self, nbtrans):
        for i in range(1,int(nbtrans)):
            name = "t" + str(i)
            self.add_transition(name, DryRun(), 'configured', 'started')