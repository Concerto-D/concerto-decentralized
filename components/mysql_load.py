
from mad import PetriNet


class MySQL(object):
    """ Define a new component of type MySQL. """

    # Data related to the dataflow port
    data = {
        'mysql_ip': '192.168.0.1',
        'mysql_port': '3306'
    }

    # Define the different places of the component
    places = ['initiated', 'installed', 'configured', 'loading', 'running']

    # Define the different transitions of the component
    transitions = [
            {'name': 'install', 'source': 'initiated', 'dest': 'installed'},
            {'name': 'load', 'source': 'configured', 'dest': 'configured'},
            {'name': 'run', 'source': 'configured', 'dest': 'running',
                'conditions': 'is_loaded' }
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

        # Set dynamically new transitions
        # Callbacks can be given during the transition initialization
        self.net.add_transition(name='configure',
                source='installed',
                dest='configured',
                callbacks=[
                    'create_config_dir',            # provide callbacks as a string
                    self.generate_config_files      # provide callbacks as a callable
                ])

    # Default callbacks can be defined with the name 'func_<transition_name>'
    def func_install(self):
        print("Installation of the Component MySQL")

    # Callbacks can be defined here, and must be added during the transition
    # initialization
    def create_config_dir(self):
        print("Create configuration directories")

    def generate_config_files(self):
        print("Generate configuration files")

    # This callback is used to show how conditions work
    def func_load(self):
        self.count += 1
        print("Loading: %s" % self.count)

    # Conditions must return `True` or `False`
    def is_loaded(self):
        print("Check if (loading=%s) >= 2" % self.count)
        return self.count >= 2
    
    # Provide Interfaces
    def mysql(self):
        return self.net.get_place('running').state

    def mysql_address(self):
        return self.data if self.net.get_place('initiated').state else None

