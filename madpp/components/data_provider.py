from madpp.component import Component
from madpp.dependency import DepType

class DataProvider(Component):
    
    def __init__(self, data):
        Component.__init__(self)
        self.write('data', data)

    def create(self):
        self.places = [
            'providing'
        ]

        self.dependencies = {
            'data': (DepType.DATA_PROVIDE, ['providing'])
        }
        
        self.initial_place = 'providing'
