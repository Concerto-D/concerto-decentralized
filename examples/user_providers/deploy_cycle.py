import sys
from mad import *

# p: provide
# u: use
#              A                           B
#
#            ready   ~ pa          pb ~  ready
#              ^                           ^
#              |                           |
#           (start)  ~ ua ------        (start)  
#              |               |           |
#           launched ~ pa <--  --> pb ~ launched
#              ^            |              ^
#              |            |              |
#           (launch)        ------ ub ~ (launch)
#              |                           |
#           waiting                     waiting

class ComponentA(Component):
      
    def create(self):
        self.places = [
            'waiting',
            'launched',
            'ready'
        ]
        self.transitions = {
            'launch': ('waiting', 'launched', self.mt_launch),
            'start': ('launched', 'ready', self.mt_ready)
        }
        self.dependencies = {
            'pa': (DepType.PROVIDE, ['launched', 'ready']),
            'ua': (DepType.USE, ['start'])
        }

    def mt_launch(self):
        print("A: launch")        
    def mt_ready(self):
        print("A: ready")
        
class ComponentB(Component):
      
    def create(self):
        self.places = [
            'waiting',
            'launched',
            'ready'
        ]
        self.transitions = {
            'launch': ('waiting', 'launched', self.mt_launch),
            'start': ('launched', 'ready', self.mt_ready)
        }
        self.dependencies = {
            'pb': (DepType.PROVIDE, ['launched', 'ready']),
            'ub': (DepType.USE, ['launch'])
        }

    def mt_launch(self):
        print("B: launch")        
    def mt_ready(self):
        print("B: ready")
        
if __name__ == '__main__':

        # Composant Provider
        ass = Assembly()

        a = ComponentA()
        b = ComponentB()
        ass.addComponent("a", a)
        ass.addComponent("b", b)
        ass.addConnection(a, 'pa', b, 'ub')
        ass.addConnection(a, 'ua', b, 'pb')
        
        mad = Mad(ass)
        mad.run(True)
