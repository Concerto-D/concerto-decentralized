
from mad import PetriNet


class MySQL(object):
    """ Define a new component of type MySQL. """

    ### Definition of the component elements:
    # Define the different places of the component:
    places = ['initiated', 'installed', 'configured', 'running']

    # Define the different transitions of the component:
    transitions = [
            {'name': 'install', 'source': 'initiated', 'dest': 'installed'},
            {'name': 'run', 'source': 'configured', 'dest': 'running' }
    ]

    # Define the different ports of the component:
    ports = [
            {'name': 'mysql', 'inside_link': 'running'},
            {'name': 'mysql_address', 'inside_link': 'initiated'}
    ]

    ### Definition of the component customizations:
    # Data related to the dataflow port
    data = {
        'mysql_ip': '192.168.0.1',
        'mysql_port': '3306'
    }

    def __init__(self):
        # Initiate our component as a PetriNet, with the related places,
        # transitions, ports and set the initial state
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

        # This variable will be used to show how conditions work
        self.count = 0

    # Default callbacks can be defined with the name 'func_<transition_name>'
    def func_install(self):
        print("(1/3) Installation of the Component MySQL")

    def func_configure(self):
        print("(2/3) Configuration of the Component MySQL")

    def func_run(self):
        print("(3/3) Component MySQL is running")

    # Customized callbacks can be defined here, and must be added during the
    # transition initialization
    def create_config_dir(self):
        print("  1. Create configuration directories")

    def generate_config_files(self):
        print("  2. Generate configuration files")

    # Definitions of the methods used by provide ports:
    def mysql(self):
        # returns 'True' if the place 'running' is validated
        return self.net.get_place('running').state

    def mysql_address(self):
        # returns 'data' if the place 'initiated' is validated
        return self.data if self.net.get_place('initiated').state else None

