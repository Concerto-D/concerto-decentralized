# Concerto

This is a preliminary implementation in Python 3 of the Concerto reconfiguration model.
Authors: Maverick Chardet, Hélène Coullon, Christian Perez {first}.{last}@inria.fr
Licence: GNU GPL v3

## Getting started

TODO: this introduction needs to be reworked to explain everything in more detail.

Concerto is a reconfiguration model which allows to describe distributed software as an evolving assembly of components.

### Component

A component usually represents a module of a distributed application, but can actually represent anything, as long as it
can express its interface (the services and data it needs to work properly and the services and data it provides)
explicitely. This is done by using ports. There are four types of ports: service use (using a service), service provide 
(providing a service), data use (using a piece of data) and data provide (providing a piece of data). Each component also
defines a life-cycle represented as a state-machine (possibly presenting parallel transitions like Petri-nets). A place 
(a state of the state-machine) represents a milestone in the life-cycle of the component. A transition between two places
allows a token (which marks a currently active place) to go from one place to another by executing an action tied to the
transition. In this implementation, an action is a Python function. Transitions are labeled with a behavior. A transition
can only be executed if it is labeled by the current active behavior of the component. The ports of a component are bound
to places, transitions or groups of places to indicate that a service/data is used/provided when the corresponding place,
transition or group is active. A group is active if there is at least one token in one of the places it contains or one
of the transitions going from one place it contains to another place it also contains.

TODO: input and output docks, input docks sets

To define a component type, declare a new class extending `concerto.component.Component` (tip:
import `Component` either from `concerto.component` or from `concerto.all`). Declare a `create` method (with no
arguments), which must initialize five properties:
- `self.places`: list of names of places
- `self.groups`: dictionary mapping a group name to a list of the names of the places it contains
- `self.transitions`: dictionary mapping a transition name to a tuple `(init, dest, bhv, set, f [, args])` where:
  * `init` is the name of the initial place of the transition
  * `dest` is the name of the destination place of the transition
  * `bhv` is the name of the behavior the transition is labelled with
  * `set` is the id of the input docks set relative to the behavior (usually 0)
  * `f` is a Python callable (usually a reference to a method declared within the class itself)
  * `args` is an optional list of parameters to pass to `f`
- `self.dependencies`: dictionary mapping a port name to a tuple `(type, bindings)` where:
  * `type` is a value of the enumeration `concerto.dependency.DepType` (USE, PROVIDE, DATA_USE or DATA_PROVIDE)
  * `bindings` is a list of names of places, groups or transitions the port is bound to.
- `self.initial_place`: name of the place which should hold a token when the component is created

Example (from `/examples/server_clients/client.py`):

```python
from concerto.all import *

class Client(Component):

    def create(self):
        self.places = [
            'off',
            'installed',
            'configured',
            'running',
            'paused'
        ]
        
        self.groups = {
            'using_service': ['running', 'paused']
        }

        self.transitions = {
            'install1': ('off', 'installed', 'install_start', 0, self.install1),
            'install2': ('off', 'configured', 'install_start', 0, self.install2),
            'configure': ('installed', 'configured', 'install_start', 0, self.configure),
            'start': ('configured', 'running', 'install_start', 0, self.start),
            'suspend1': ('running', 'paused', 'stop', 0, self.suspend1),
            'suspend2': ('paused', 'configured', 'stop', 0, self.suspend2)
        }

        self.dependencies = {
            'server_ip': (DepType.DATA_USE, ['configure']),
            'service': (DepType.USE, ['using_service'])
        }
        
        self.initial_place = 'off'
```

The constructor of the `concerto.component.Component` class will call `create`. Keep in mind that if you override the
`__init__` function, you must call  explicitely the constructor of the parent class. If the `create` function uses anything
this is initialized in the `__init__` function, call `Component.__init__` after their initialization.

For complete examples, please look at the components declared in the `examples` directory, such as
`/examples/server_clients/client.py`.


### Assembly

An assembly is a possibly continuously evolving collection of component instances interconnected by their ports. Initially,
an assembly is empty. Reconfiguration operations, written using the ScoreL language, can be applied to it to add or remove
components, connect or disconnect their ports, push a behavior to the queue of behaviors of a component or wait until a
component's queue is empty.

To define an assembly, declare a new class extending `concerto.assembly.Assembly` (tip: import `Assembly` either from
`concerto.assembly` or from `concerto.all`). To define a new reconfiguration, create a new method ending with those two
instructions (you can do otherwise if you know what you're doing):

```python
# Here goes your ScoreL program
self.wait_all() # Waits for all the components to finish their queued behaviors (ensures the reconfiguration is finished)
self.synchronize() # Synchronizes with the execution thread, returning when the reconfiguration is actually finished
```

Before those, you can write any ScoreL program using the following `Assembly` methods:
- `add_component(c, ref)`: adds a component instance to the assembly, where `c` is an arbitrary string identifier for the component and `ref` is a reference to an instance of the Python class of the desired component
- `del_component(c)`: deletes a component instance from the assembly, where `c` is the identifier of the component to remove
- `connect(c1, p1, c2, p2)`: connects the port `p1` of component `c1` and the port `p2` of component `c2`
- `disconnect(c1, p1, c2, p2)`: disconnects the port `p1` of component `c1` and the port `p2` of component `c2`
- `push_b(c, behavior)`: adds the behavior `behavior` to the queue of component `c`
- `wait(c)`: waits until component `c` has an empty queue before executing the next instructions
- `wait_all()`: waits until all the components of the assembly have empty queues before executing the next instructions

Note that these methods add the corresponding ScoreL instructions to a queue of instructions to apply to the assembly. As
a consequence, none of them are blocking. In order to wait until the last instruction was actually applied, you can call
the `synchronize()` instruction.

Example (from `examples/server_clients/server_client_assembly.py`):
```python
from concerto.all import *

from client import Client
from server import Server

class ServerClient(Assembly):
    def __init__(self, ...):
        ...
        self.server = Server(...)
        self.client = Client(...)
        Assembly.__init__(self)
    
    def deploy(self):
        self.print("### DEPLOYING ####")
        self.add_component('client', self.client)
        self.add_component('server', self.server)
        self.connect('client', 'server_ip',
                    'server', 'ip')
        self.connect('client', 'service',
                    'server', 'service')
        self.push_b('client', 'install_start')
        self.push_b('server', 'deploy')
        self.wait('client') # In this case, equivalent to self.wait_all()
        self.synchronize()
```

Note that here the Python instances of the Client and Server classes were declared in `__init__` as properties of the assembly.
This is only one of many ways to do it. One could for instance construct the instances directly inside the `add_component`
calls.

For complete examples, please look at the assemblies declared in the `examples` directory, such as
`/examples/server_clients/server_client_assembly.py`.


### Implementation-specific use of Assembly objects

The simpliest way to execute a Concerto reconfiguration is to only declare an instance of an assembly and execute the first
reconfiguration (usually deployment), possibly followed by others. Finally, a call to the `terminate()` method waits for
all the reconfigurations to be finished and kills the execution thread of the assembly.

Example (modified extract from from `examples/server_clients/test_server_client.py`):
```python
from server_client_assembly import ServerClient

sca = ServerClient()

sca.deploy()
sca.suspend()
sca.restart()

sca.terminate()
```

Our implementation however provides additional functionality. These `Assembly` methods can be called before the first reconfiguration
is called:
- `set_use_gantt_chart(b)`: if `b` is `True`, records the start and end time of transitions and behaviors' execections
so that a Gantt Chart can be exported at the end (in JSON or GNUplot format). (default: `False`)
- `set_verbosity(verbosity)`: if `verbosity` is `-1`, any call that components make to the `Component.t_print` function will
be skipped, and no debug information will be printed. If `verbosity` is `0`, only calls to `Component.t_print` will print. If
`verbosity` is `1`, limited debug information will be printed. If `verbosity` is `2` or more, full debug information will be printed.
(default: `0`)
- `set_print_time(b)`: if `b` is `True`, `Component.t_print` and debug printing functions will print the time before the message. If
`b` is false, they will not. (default: `True`)
- `set_dryrun(b)`: if `b` is `True`, the transitions executed by the components will all be replaces by `pass` and do nothing. This
allows to check for the well-formedness of the assembly. (default: `False`)

These `Assembly` methods can be called after `terminate` is called:
- `get_gantt_chart()`: if `set_use_gantt_chart(True)` was called, returns a `concerto.gantt_chart.GanttChart` object. The GanttChart
methods `export_json(file_name)` and `export_gnuplot(file_name, title='')` can then be used to export the Gantt chart.

Note that it is possible to customize the verbosity of a specific component, or hide this component from the resulting Gantt chart
by calling the following `Component` methods on a `Component` Python object:
- `force_vebosity(forced_verobisty)`
- `force_hide_from_gantt_chart()`

Example (modified extract from from `examples/server_clients/test_server_client.py`):
```python
from server_client_assembly import ServerClient

sca = ServerClient()
sca.set_use_gantt_chart(True)
sca.set_verbosity(-1)
sca.set_print_time(False)

# The following is possible because server and client are declared as properties in ServerClient.__init__()
sca.server.force_vebosity(2)
sca.client.force_hide_from_gantt_chart()

sca.deploy()
sca.suspend()
sca.restart()

sca.terminate()

gc : GanttChart = sca.get_gantt_chart()
gc.export_gnuplot("results_server.gpl", "Gantt chart with the Server component only")
gc.export_json("results_server.json")
```
