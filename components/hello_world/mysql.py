
from mad import PetriNet


class MySQL(object):
    """ Define and initialize a component of type MySQL:
    1. Define our component's places,
    2. Define places' transitions with their related callbacks,
    3. Define our component's ports with their methods,
    4. Initialize the component.

    """

    # 1. Here, we define four places for our component:
    places = [
        'initiated',
        'installed',
        'configured',
        'running'
    ]

    # 2. We now define their transitions, with their associated callbacks:
    transitions = [
        {'name': 'install', 'source': 'initiated', 'dest': 'installed'},
        {'name': 'configure', 'source': 'installed', 'dest': 'configured'},
        {'name': 'run', 'source': 'configured', 'dest': 'running' }
    ]

    # Callbacks can be mapped to <transition> when defined as 'func_<transition>':
    def func_install(self):
        print("(1/3) Installation of the Component MySQL")
    def func_configure(self):
        print("(2/3) Configuration of the Component MySQL")
    def func_run(self):
        print("(3/3) Component MySQL is running")

    # 3. We then define two ports, their linked elements, and their callbacks:
    ports = [
        {'name': 'mysql', 'inside_link': 'running'},
        {'name': 'mysql_address', 'inside_link': 'initiated'}
    ]

    # Methods can be mapped to <port> when defined as '<port>':
    def mysql(self):
        # Returns 'True' if the place 'running' is validated:
        return self.net.get_place('running').state
    def mysql_address(self):
        # Returns 'data' if the place 'initiated' is validated:
        return self.data if self.net.get_place('initiated').state else None

    # Data related to the dataflow port
    data = {
        'mysql_ip': '192.168.0.1',
        'mysql_port': '3306'
    }

    # 4. Initialize our component as a PetriNet, with the related places,
    # transitions, ports and set the initial place:
    def __init__(self):
        self.net = PetriNet(self, self.places, self.transitions, self.ports,
                initial='initiated')

