from concerto.all import *
from concerto.utility import empty_transition


class UserNTrans(Component):
    
    def __init__(self, nb_trans : int):
        self.nb_trans = nb_trans
        Component.__init__(self)

    def create(self):
        self.places = [
            'waiting',
            'configured',
            'started'
        ]
        
        self.initial_place = 'waiting'

        self.transitions = {
            'init': ('waiting', 'configured', 'start', 0, empty_transition)
        }
        for i in range(0,int(self.nb_trans)):
            name = "t" + str(i)
            self.transitions[name] = ('configured', 'started', 'start', 0, empty_transition)

        self.dependencies = {
            'service': (DepType.USE, ['init'])
        }
