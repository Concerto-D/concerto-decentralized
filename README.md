
# MAD Model

A lightweight implementation of the MAD model in Python.


## Installation

MAD has different dependencies as listed in `requirements.txt`. A simple way to
install them is to use `pip`. To that end, python3-pip must be installed on
your system (the installation procedure depends on your system - for instance,
type `sudo apt-get install python3-pip` for debian-based distributions).

Before going further, please be sure python3-pip is installed. This can be checked
by typing: `which pip3`, which should return the path to `python3-pip`.

Once python3-pip is installed, you can either install the dependencies in a
virtual environment (recommended) or in the user directory.

### Using a virtual environment

Run `make install_deps` to install the dependencies in a virtual environment
(venv). This target create a `venv` directory which contains all the required
dependencies. You can afterward remove those dependencies by deleting the
`venv` directory. This way keeps your system clean.

Anytime you want to call `mad`, be sure the virtual environment is activated:
```bash
$ source venv/bin/activate
```

### Without a virtual environment

If you don't want to bother with a virtual environment, you can install the
dependencies in the user directory by typing: `make install_deps_user`.


## Getting Started

### 1. Component definition

Here is the definition of a component which describes the deployment of a MySQL
server, contained in the file `./components/hello_world/mysql.py`:

```python

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

```

#### Explore the component

To explore the previous MySQL component, run `python3`:

```python

from components.hello_world.mysql import MySQL

# Instantiate the MySQL component:
>>> mysql = MySQL()

# Get the component's places:
>>> mysql.places
['initiated', 'installed', 'configured', 'running']

# Get the component's transitions:
>>> mysql.transitions
[{'dest': 'installed', 'name': 'install', 'source': 'initiated'},
 {'dest': 'configured', 'name': 'configure', 'source': 'installed'},
 {'dest': 'running', 'name': 'run', 'source': 'configured'}]

# Get the component's ports:
>>> mysql.ports
[{'inside_link': 'running', 'name': 'mysql'},
 {'inside_link': 'initiated', 'name': 'mysql_address'}

```


#### 2. Play manually with the component

```python

# Initialize the component (activate the initial state)
>>> mysql.net.initialize()

# Get the current place in the PetriNet:
>>> mysql.current_places
{'initiated'}

# Get the possible transitions:
mysql.net.get_current_transitions()
['install']

# Run the transition:
>>> mysql.install()
(1/3) Installation of the Component MySQL

# Check the new position:
>>> mysql.current_places
{'installed'}

>>> mysql.configure()                                                                
(2/3) Configuration of the Component MySQL

>>> mysql.net.get_current_transitions()
['run']

# Get to the last place:
>>> mysql.run()
(3/3) Component MySQL is running

# Check if there is available transitions:
>>> mysql.net.get_current_transitions()
[]

```

### 3. Automatic deployment of the component

An `assembly` object can be used to automatically deploy components. To depict
assemblies, we are going to use a component with parallel transitions. Such
component, based on the previous one, can be found in
`./components/hello_world/parallel_mysql.py`. Open this file to understand the
component's internals. Then run the following with `python3`:

```python

from components.hello_world.parallel_mysql import MySQL
from assembly import Assembly

# Initialize a MySQL component:
>>> mysql = MySQL()

# Initialize an assembly to manage the `mysql` component:
>>> assembly = Assembly([[mysql, 'mysql']])

# Trigger automatic deployment of the assembly:
>>> assembly.auto_run()
(1/2) [Parallel] Install the Component MySQL
(1/2) [Parallel] Bootstrap the Component MySQL
[MySQL] Successfully moved from initiated to ready

(2/2) Component MySQL is running
[MySQL] Successfully moved from ready to running

[MySQL] Successfully moved from initiated to ready

[MySQL] Successfully moved from initiated to ready

[MySQL] Reach the final place.

```

### 4. Play with multiple components

A set of pre-defined components are available in the `components/` directory.
In this example, we deploy both MySQL and Keystone:

```python

from components.keystone_multi import Keystone
from components.mysql import MySQL
from assembly import Assembly

# Initialize two components:
>>> mysql = MySQL()
>>> keystone = Keystone()

# Initialize an assembly to manage both components:
>>> assembly = Assembly([[mysql, 'mysql'], [keystone, 'keystone']])

# Let the assembly deploy automatically the components:
>>> assembly.auto_run()
# This operation must fail at some point because `keystone` has dependencies
# with `mysql`.

# While `mysql` has reached its final place, `keystone` is stuck because we
# have not connected these components.
>>> mysql.current_places
{'running'}
>>> keystone.current_places
{'configured', 'installed'}

# Let's connect both components:
>>> assembly.auto_connect('mysql', 'keystone')
# When ports are connected, they notify the automaton which continues the
# deployment where it was stuck.

>>> mysql.current_places
{'running'}
>>> keystone.current_places
{'running'}

```

