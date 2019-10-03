#!/usr/bin/python3

from concerto.all import *


class SwitchComp(Component):

    def create(self):
        self.places = [
            'initial',
            'small',
            'big1',
            'big2'
        ]
        
        def choosing_f(component_instance, current_behavior):
            if component_instance.read('value') < 5:
                return [0]
            else:
                return [1, 2]
        
        self.switches = [
            ('choosing', choosing_f) 
        ]

        self.transitions = {
            'enter_switch': ('initial', 'choosing', 'run', 0, self.enter_switch),
            'leave_small': ('choosing', 'small', 'run', 0, self.leave_small),
            'leave_big1': ('choosing', 'big1', 'run', 0, self.leave_big1),
            'leave_big2': ('choosing', 'big2', 'run', 0, self.leave_big2)
        }

        self.dependencies = {
            'value': (DepType.DATA_USE, ['choosing'])
        }
        
        self.initial_place = 'initial'

    def enter_switch(self):
        self.print_color("entering switch")

    def leave_small(self):
        self.print_color("small")

    def leave_big1(self):
        self.print_color("big (1)")

    def leave_big2(self):
        self.print_color("big (2)")


class ValueProvider(Component):
    
    def create(self):
        self.places = [
            'initial',
            'providing'
        ]

        self.transitions = {
            'provide': ('initial', 'providing', 'run', 0, self.provide)
        }

        self.dependencies = {
            'value': (DepType.DATA_PROVIDE, ['providing'])
        }
        
        self.initial_place = 'initial'

    def provide(self):
        import time
        time.sleep(5)
        self.write('value', 3)



class SwitchTestAssembly(Assembly):
    def __init__(self):
        self.switch_comp = SwitchComp()
        self.value_provider = ValueProvider()
        Assembly.__init__(self)
    
    def run(self):
        self.print("### RUNNING ####")
        self.add_component('switch_comp', self.switch_comp)
        self.add_component('value_provider', self.value_provider)
        self.connect('switch_comp', 'value',
                    'value_provider', 'value')
        self.push_b('switch_comp', 'run')
        self.push_b('value_provider', 'run')
        self.wait_all()
        self.synchronize()



if __name__ == '__main__':
    sta = SwitchTestAssembly()
    sta.set_verbosity(1)
    sta.run()
    sta.terminate()
