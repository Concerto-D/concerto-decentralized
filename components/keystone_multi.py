
import os
from mad import PetriNet
#from utils.extra import run_ansible
#from utils.constants import ANSIBLE_DIR


class Keystone(object):
    """ Define a new component of type Keystone. """

    # Data related to the dataflow port
    data = {
        'keystone_ip': '192.168.0.1',
        'keystone.port': '3306'
    }
    
    # Define the different places of the component
    places = ['initiated', 'provisioned', 'db_created', 'installed',
            'configured', 'running']

    # Define the different transitions of the component
    transitions = [
            {'name': 'provision', 'source': 'initiated', 'dest': 'provisioned'},
            {'name': 'db_create', 'source': 'provisioned', 'dest': 'db_created'},
            {'name': 'install', 'source': 'provisioned', 'dest': 'installed'},
            {'name': 'db_init', 'source': 'db_created', 'dest': 'configured'},
            {'name': 'configure', 'source': 'installed', 'dest': 'configured'},
            {'name': 'register', 'source': 'provisioned', 'dest': 'configured'},
            {'name': 'run', 'source': 'configured', 'dest': 'running' }
    ]

    # Define the different ports
    ports = [
            {'name': 'keystone_address', 'inside_link': 'initiated'},
            {'name': 'keystone', 'inside_link': 'running'},
            {'name': 'mysql_address', 'inside_link': 'configure'},
            {'name': 'mysql', 'inside_link': 'run'}
    ]

    def __init__(self):
        # Initiate our component as a PetriNet, with the related places and the
        # initial one
        self.net = PetriNet(self, self.places, self.transitions, self.ports,
                initial='initiated')

    # Default callbacks can be defined with the name 'func_<transition_name>'
    def func_provision(self):
        print("(1/4) Provision Keystone machine")
    def func_db_create(self):
        print("(2/4) [Parallel] Create Keystone databases")
        playbook = os.path.join(ANSIBLE_DIR, 'test.yml')
        inventory = os.path.join(ANSIBLE_DIR, 'inventory')
        extra_vars = self.data
        #run_ansible(playbooks, inventory, extra_vars, tags, on_error_continue)
        #run_ansible([playbook], inventory, extra_vars)
    def func_install(self):
        print("(2/4) [Parallel] Install Keystone service")
    def func_register(self):
        print("(2/4) [Parallel] Register Keystone service")
    def func_db_init(self):
        print("(3/4) [Parallel] Initialize Keystone databases")
    def func_configure(self):
        print("(3/4) [Parallel] Configure Keystone service")
    def func_run(self):
        print("(4/4) Configure Keystone service")

    # Provide ports must be implemented
    def keystone(self):
        return self.net.get_place('running').state

    def keystone_address(self):
        return self.data if self.net.get_place('initiated').state else None

