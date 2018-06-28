# -*- coding: utf-8 -*-
""" This component is part of the use/provide toy example which depicts
how MAD components can exchange information. This component is the Provider
counterpart, whose places, transitions and ports are depicted as follow:

+--------------------------------------------------------------+
|                                                              |
|                      Provider Component                      |
|                                                              |
|                 +-------------------------+                  |
|                 |                         | provider_serv    |
|                 |        +-------+        |   (provide)      |
|                 |        |running| +----------->             |
|                 |        +---+---+        |                  |
|                 |            ^            |                  |
|                 |            |            |                  |
|                 |           +-+ run       |                  |
|                 |            |            |                  |
|                 |       +----+-----+      |                  |
|                 |       |configured|      |                  |
|                 |       +----+-----+      |                  |
|                 |            ^            |                  |
|                 |            |            |                  |
|                 |           +-+ configure |                  |
|                 |            |            |                  |
|                 |       +----+----+       |                  |
|                 |       |installed|       |                  |
|                 |       +----+----+       |                  |
|                 |            ^            |                  |
|                 |            |            |                  |
|                 |           +-+ install   |                  |
|                 |            |            | provider_data    |
|                 |  +---------+---------+  |   (provide)      |
|                 |  |initiated (initial)| +----->             |
|                 |  +-------------------+  |                  |
|                 |                         |                  |
|                 +-------------------------+                  |
|                                                              |
+--------------------------------------------------------------+


"""

from mad import PetriNet
from utils.extra import printerr


class Provider(object):
    """ Define a new component of type Provider."""

    # The provider contains some data that must be used by another component:
    data = {
        'provider_ip': '192.168.0.1',
        'provider_port': '3306'
    }

    # Define the different places of the component:
    places = ['initiated', 'installed', 'configured', 'running']

    # Define the different transitions of the component:
    transitions = [
            {'name': 'install', 'source': 'initiated', 'dest': 'installed'},
            {'name': 'configure', 'source': 'installed', 'dest': 'configured'},
            {'name': 'run', 'source': 'configured', 'dest': 'running'}
    ]

    # Define the different ports - both of them are 'provide' ports, attached
    # to different places:
    ports = [
            {'name': 'provider_data', 'inside_link': 'initiated'},
            {'name': 'provider_serv', 'inside_link': 'running'}
    ]

    def __init__(self, step=False):

        # Initiate our component as a PetriNet, with its places, transitions,
        # ports and its initial place:
        self.net = PetriNet(self, self.places, self.transitions, self.ports,
                initial='initiated')

    # Transition callbacks are defined here:
    def func_install(self):
        printerr("(1/3) Installlation of the component Provider.")

    def func_configure(self):
        printerr("(2/3) Configuration of the component Provider.")

    def func_run(self):
        printerr("(3/3) Component Provider is running")

    # Two methods are defined to implement the 'provide' ports:
    def provider_data(self):
        # The method 'provider_data' returns data if the related place is
        # activated:
        return self.data if self.net.get_place('initiated').state else None

    def provider_serv(self):
        # The method 'provider_serv' returns the state of its related place:
        return self.net.get_place('running').state

