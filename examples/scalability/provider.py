from concerto.all import *


class Provider(Component):

    echo1 = "test1"
    echo2 = "test2"

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]
        
        self.initial_place = 'waiting'

        self.transitions = {
            'start': ('waiting', 'started', 'start', 0, self.testargs, (self.echo1,
                                                                self.echo2))
        }

        self.dependencies = {
            'service': (DepType.PROVIDE, ['started'])
        }

    def testargs(self, arg1, arg2):
        self.print_color("arg1=" + str(arg1) + " and arg2=" + str(arg2))
