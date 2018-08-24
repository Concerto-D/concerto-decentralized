from mad import *
from examples.scalability.transitions import *


class UserNTrans(Component):

    places = [
        'waiting',
        'configured',
        'started'
    ]

    transitions = {
        'init': ('waiting', 'configured', DryRun().run),
        't0': ('configured', 'started', DryRun().run)
    }

    dependencies = {
        'service': (DepType.USE, ['init'])
    }

    def createTransitions(self, nbtrans):
        for i in range(1,int(nbtrans)):
            name = "t" + str(i)
            self.add_transition(name, 'configured', 'started', DryRun().run)