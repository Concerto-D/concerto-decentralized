# -*- coding: utf-8 -*-
""" This component is part of the use/provide toy example which depicts
how MAD components can exchange information. This component is the User
counterpart, whose places, transitions and ports are depicted as follow:

+--------------------------------------------------------------+
|                                                              |
|                        User Component                        |
|                                                              |
|                 +-------------------------+                  |
|                 |                         |  user_serv       |
|                 |        +-------+        |  (provide)       |
|                 |        |running| +----------->             |
|                 |        +---+---+        |                  |
|  provider_serv  |            ^            |                  |
|      (use)      |            |            |                  |
|            +--------------> +-+ run       |                  |
|                 |            |            |                  |
|                 |       +----+-----+      |                  |
|                 |       |configured|      |                  |
|                 |       +----+-----+      |                  |
|  provider_data  |            ^            |                  |
|      (use)      |            |            |                  |
|            +--------------> +-+ configure |                  |
|                 |            |            |                  |
|                 |       +----+----+       |                  |
|                 |       |installed|       |                  |
|                 |       +----+----+       |                  |
|                 |            ^            |                  |
|                 |            |            |                  |
|                 |           +-+ install   |                  |
|                 |            |            |                  |
|                 |  +---------+---------+  |                  |
|                 |  |initiated (initial)|  |                  |
|                 |  +-------------------+  |                  |
|                 |                         |                  |
|                 +-------------------------+                  |
|                                                              |
+--------------------------------------------------------------+


"""

from mad import PetriNet
from utils.extra import printerr


class User(object):
    """ Define a new component of type User."""

    # This empty variable will be filled by a Provider component:
    provider_data = None
    
    # Define the different places of the component:
    places = ['initiated', 'installed', 'configured', 'running']

    # Define the different transitions of the component:
    transitions = [
            {'name': 'install', 'source': 'initiated', 'dest': 'installed'},
            {'name': 'configure', 'source': 'installed', 'dest': 'configured'},
            {'name': 'run', 'source': 'configured', 'dest': 'running'}
    ]

    # Define the different ports - the first one is a 'provide' port attached
    # to the state 'running', while the two remaining are 'use' ports, attached
    # to different transitions:
    ports = [
            {'name': 'user_serv', 'inside_link': 'running'},
            {'name': 'provider_serv', 'inside_link': 'run'},
            {'name': 'provider_data', 'inside_link': 'configure'}
    ]

    def __init__(self, step=False):

        # Initiate our component as a PetriNet, with its places, transitions,
        # ports and its initial place:
        self.net = PetriNet(self, self.places, self.transitions, self.ports,
                initial='initiated')

    # Transition callbacks are defined here:
    def func_install(self):
        printerr("(1/3) Installation of the component User.")

    def func_configure(self):
        # The configure transition has a 'provider_data' port which is used
        # to transfer data from the provider to the user component.
        # This callback is only fired if the two components are connected and
        # if the remote port is activated.
        # The port creates a local method called after its name, which gives a
        # reference to the related remote method.
        printerr("(2/3) Configuration of the component User.")
        self.provider_data = getattr(self, 'provider_data')()
        printerr("User received the following data: %s, \n"
              "Configuration can proceed." % self.provider_data)

    def func_run(self):
        printerr("(3/3) Component User is running.")

    # This method is defined to implement the 'provide' port:
    def user_serv(self):
        return self.net.get_place('running').state

