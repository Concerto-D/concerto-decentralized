
import os
import time
from mad import PetriNet
from utils.extra import run_ansible
from utils.constants import ANSIBLE_DIR


class MySQL(object):
    """ Define a new component of type MySQL. """

    # Data related to the dataflow port
    data = {
        'mysql_ip': '192.168.0.1',
        'mysql_port': '3306'
    }

    # Define the different places of the component
    places = ['initiated', 'provisioned', 'db_created', 'installed',
            'configured', 'running']

    # Define the different transitions of the component
    # We define here two branches from 'provisioned' to 'configured'
    transitions = [
            {'name': 'provision', 'source': 'initiated', 'dest': 'provisioned'},
            {'name': 'db_create', 'source': 'provisioned', 'dest': 'db_created'},
            {'name': 'install', 'source': 'provisioned', 'dest': 'installed'},
            {'name': 'db_init', 'source': 'db_created', 'dest': 'configured'},
            {'name': 'configure', 'source': 'installed', 'dest': 'configured'},
            {'name': 'run', 'source': 'configured', 'dest': 'running' }
    ]

    ports = [
            {'name': 'mysql', 'inside_link': 'running'},
            {'name': 'mysql_address', 'inside_link': 'initiated'}
    ]

    def __init__(self):
        # This variable will be used to show how conditions work
        self.count = 0

        # Initiate our component as a PetriNet, with the related places and the
        # initial one
        self.net = PetriNet(self, self.places, self.transitions, self.ports,
                initial='initiated')

    # Default callbacks can be defined with the name 'func_<transition_name>'
    def func_provision(self):
        print("(1/4) Provision MySQL machine")
    def func_db_create(self):
        #return 1 #fake error
        print("(2/4) [Parallel] Create MySQL databases")
    def func_install(self):
        print("(2/4) [Parallel] Install MySQL service")
    def func_db_init(self):
        #return 1 #fake error
        print("(3/4) [Parallel] Initialize MySQL databases")
    def func_configure(self):
        print("(3/4) [Parallel] Configure MySQL service")
    def func_run(self):
        print("(4/4) Configure MySQL service")

    # Provide Interfaces
    def mysql(self):
        return self.net.get_place('running').state

    def mysql_address(self):
        return self.data if self.net.get_place('initiated').state else None

