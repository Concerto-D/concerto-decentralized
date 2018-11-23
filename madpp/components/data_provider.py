from madpp.component import Component
from madpp.dependency import DepType

class DataProvider(Component):
    
    def __init__(self, data):
        Component.__init__(self)
        self.data = data

    def create(self):
        self.places = [
            'init',
            'providing'
        ]

        self.transitions = {
            'provide': ('init', 'providing', 'provide', 0, self.provide)
        }

        self.dependencies = {
            'data': (DepType.DATA_PROVIDE, ['providing'])
        }
        
        self.initial_place = 'init'
    
    def provide(self):
        self.write('data', self.data)
