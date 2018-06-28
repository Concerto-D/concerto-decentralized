# -*- coding: utf-8 -*-

from mad import PetriNet


class UserProvider(object):
    """ Define a new component of type User."""

    # Define the different places of the component:
    places = ['initial', 'running']

    # Define the different transitions of the component:
    transitions = [
            {'name': 'run', 'source': 'initial', 'dest': 'running'}
    ]

    # Define the different ports:
    ports = [
            {'name': 'use', 'inside_link': 'run'},
            {'name': 'provide', 'inside_link': 'running', 'method': 'method'},
    ]

    def __init__(self, step=False):

        # Initiate our component as a PetriNet, with its places, transitions,
        # ports and its initial place:
        self.net = PetriNet(self, self.places, self.transitions, self.ports,
                initial='initial')

    # Transition callbacks are defined here:
    def func_run(self):
        print("Component ProviderUser is running.")

    # This method is defined to implement the 'provide' port:
    def method(self):
        return self.net.get_place('running').state

