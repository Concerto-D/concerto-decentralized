# -*- coding: utf-8 -*-

from mad import PetriNet


class Provider(object):
    """ Define a new component of type Provider."""

    # Define the different places of the component:
    places = ['initial', 'running']

    # Define the different transitions of the component:
    transitions = [
            {'name': 'run', 'source': 'initial', 'dest': 'running'}
    ]

    # Define the different ports:
    ports = [
            {'name': 'provide', 'inside_link': 'running', 'method': 'method'}
    ]

    def __init__(self, step=False):

        # Initiate our component as a PetriNet, with its places, transitions,
        # ports and its initial place:
        self.net = PetriNet(self, self.places, self.transitions, self.ports,
                initial='initial')

    def func_run(self):
        print("Component Provider is running")

    def method(self):
        # The method 'provider_serv' returns the state of its related place:
        return self.net.get_place('running').state

