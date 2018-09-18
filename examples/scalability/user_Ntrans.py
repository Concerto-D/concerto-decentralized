from mad import *
from examples.scalability.transitions import *


class UserNTrans(Component):

    def create(self):
        self.places = [
            'waiting',
            'configured',
            'started'
        ]

        self.transitions = {
            'init': ('waiting', 'configured', DryRun().run),
            't0': ('configured', 'started', DryRun().run)
        }

        self.dependencies = {
            'service': (DepType.USE, ['init'])
        }

    def createTransitions(self, nbtrans):
        for i in range(1,int(nbtrans)):
            name = "t" + str(i)
            self.add_transition(name, 'configured', 'started', DryRun().run)