# -*- coding: utf-8 -*-
""" This component is part of the use/provide toy example to depict how MAD
works.

"""

from mad import PetriNet


class Keystone(object):
    """ Define a new component of type Keystone. """

    # Data related to the dataflow port
    data = {
        'keystone_ip': '192.168.0.1',
        'keystone.port': '3306'
    }

    # This field will be filled by a MySQL component
    mysql_data = None
    
    # Define the different places of the component
    places = ['initiated', 'installed', 'configured', 'running']

    # Define the different transitions of the component
    transitions = [
            {'name': 'install', 'source': 'initiated', 'dest': 'installed'},
            {'name': 'configure', 'source': 'installed', 'dest': 'configured'},
            {'name': 'run', 'source': 'configured', 'dest': 'running'}
    ]

    # Define the different ports
    ports = [
            {'name': 'keystone_address', 'inside_link': 'initiated'},
            {'name': 'keystone', 'inside_link': 'running'},
            {'name': 'mysql_address', 'inside_link': 'configure'},
            {'name': 'mysql', 'inside_link': 'run'}
    ]

    def __init__(self, step=False):

        # Initiate our component as a PetriNet, with the related places and the
        # initial one
        self.net = PetriNet(self, self.places, self.transitions, self.ports,
                initial='initiated')

    # Default callbacks can be defined with the name 'func_<transition_name>'
    def func_install(self):
        print("(1/3) Installation of the Component Keystone")

    def func_configure(self):
        # The configure transition has a 'mysql_address' port which allows to
        # fetch data from a MySQL component. This callback is fired only if the
        # link is created between both components, so we can reach MySQL
        # information through the method called by the port's name:
        print("(2/3) Configuration of the Component Keystone")
        self.mysql_data = getattr(self, 'mysql_address')()
        print("MySQL received: %s, \n Configuration can proceed." %
                self.mysql_data)

    def func_run(self):
        print("(3/3) Component Keystone is running")

    # Provide ports must be implemented
    def keystone(self):
        return self.net.get_place('running').state

    def keystone_address(self):
        return self.data if self.net.get_place('initiated').state else None

