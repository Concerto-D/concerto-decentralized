# MAD Model

A lightweight implementation of the MAD model in Python.

## Documentation

A complete documentation, including a getting started is available online at 
https://mad.readthedocs.io/en/v0.2/

# Files descriptions

## assembly.py
This file represents the implementation of an assembly so as defined by the 
Madeus model. An assembly is composed of:
* a set of component instances
* a set of connections between components (use-provide dependencies)
* a run function
This object is the entry point for the end-user to describe its complete 
software deployment.

## component.py
A component is the object to represent a software module. It is composed of:
* a set of places
* a set of docks
* a set of transitions
* a set of ports
* a set of bindings represented by arrays within a component. A binding can 
link a use port to a transition, or a provide port to a place.

## connection.py
A connection link a provide port (data or service) to a use port. A provide 
port can be connected multiple times to use ports.

## place.py
A place is a very simple object that holds or not a token.

### dock.py
A dock is attached to a place. It can be an input or output dock, and it can 
holds or not a token. This object is used to handle threads creations and joins.

## transition.py
A transition represents a connection between an output dock of a place and an
input dock of another place. A transition is associated to an action or a 
function to perform. Finally, a transition can also holds a token or not.

## use.py
This object represents a use port. In Madeus a use port is not implemented, 
thus it represents a dependency more than a usual use port of component models. 
Actually, in Madeus, a use port is bound to a transition in which the user is 
responsible for real use actions. Two types of use dependencies exists within
Madeus and  are described below. As each type has a different runtime 
semantics we need to distinguish the two types.
### serv-use.py
This port represents a service dependency. It means that an external services
will be used by the transition to which the port is bound.
### data-use.py
This port represents a data dependency. It means that an external data will 
be used by the transition to which the port is bound.

## provide.py
This port is the dual of the use port. As the use port it is not implemented.
 As for the use port, two type of provide ports are offered by Madeus.
### serv-provide.py
This port represents a service dependency (the provide side of the 
dependency). Such port is bound to a group of places in which the component 
provides its service. In Madeus we consider that a given software module to 
deploy will already handle some external interfaces such as for instance rest
API. Thus, the user does not necessarily has to handle the implementation of 
this port that is most of the time already implemented within the module to 
deploy.
### data-provide.py
This port represents a data dependency (the provide side of the dependency). 
This port is bound to a place but is filled during the transition that 
precedes the place. As for the use port the user has to implement the data 
transition herself. This can be performed within the data-provide (push mode)
or within the data-use (pull mode).

## engine.py
The engine is responsible for the execution of the deployment by following 
the seven rules of the formal Madeus model:
* firing a transition
* ending a transition
* from input docks to a place (join)
* from place to output docks (fork)
* enabling use-provide connection
* disabling use-provide connection
* enabling data-use-provide connection
The engine is responsible for the management of threads during fork and join 
phases.
An engine is composed of an assembly and a current configuration of the assembly

## configuration.py
A configuration is used by the engine to handle the evolution of the 
deployment process. A configuration is composed of:
* a list of token and their position in the assembly (docks, places, 
transitions)
* the status of each connection (between two ports): enable or disable
* data associated to each data provide