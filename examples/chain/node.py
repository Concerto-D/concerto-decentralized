from mad import *


class Node(Component):

    def __init__(self, first=False, last=False):
        self.first = first
        self.last = last
        super().__init__()
        
    def create(self):
        self.places = [
            'waiting',
            'started'
        ]

        self.transitions = {
            'start': ('waiting', 'started', self.mt_run)
        }

        if self.first:
            self.dependencies = {
                'p': (DepType.PROVIDE, ['started'])
            }
        elif self.last:
            self.dependencies = {
                'u': (DepType.USE, ['start'])
            }
        else:
            self.dependencies = {
                'u': (DepType.USE, ['start']),
                'p': (DepType.PROVIDE, ['started'])
            }

    def mt_run(self):
        print(self.name+" run!")
