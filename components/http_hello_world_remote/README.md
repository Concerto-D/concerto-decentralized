
# User-Provider example 

This toy example aims at showing how MAD components can share data. It
involves two MAD components:

1. `Provider`;

2. `User`.

The proposed assembly and the related components are depicted as follow: 

```
        Provider Component                               User Component                   
                                                                                       
  +---------------------------+                  +---------------------------+             
  |                           | provider_serv    |                           |  user_serv  
  |         +-------+         |   (provide)      |         +-------+         |  (provide)  
  |         |running| +----------------+         |         |running| +----------->        
  |         +---+---+         |        |         |         +---+---+         |             
  |             ^             |        |         |             ^             |             
  |             |             |        |         |             |             |             
  |            +-+ run        |        +--------------------> +-+ run        |             
  |             |             |    provider_serv |             |             |             
  |        +----+-----+       |        (use)     |        +----+-----+       |             
  |        |configured|       |                  |        |configured|       |             
  |        +----+-----+       |                  |        +----+-----+       |             
  |             ^             |    provider_data |             ^             |             
  |             |             |        (use)     |             |             |             
  |            +-+ configure  |        +--------------------> +-+ configure  |             
  |             |             |        |         |             |             |             
  |        +----+----+        |        |         |        +----+----+        |             
  |        |installed|        |        |         |        |installed|        |             
  |        +----+----+        |        |         |        +----+----+        |             
  |             ^             |        |         |             ^             |             
  |             |             |        |         |             |             |             
  |            +-+ install    |        |         |            +-+ install    |             
  |             |             |        |         |             |             |             
  |   +---------+---------+   |        |         |   +---------+---------+   |             
  |   |initiated (initial)| +----------+         |   |initiated (initial)|   |             
  |   +-------------------+   | provider_data    |   +-------------------+   |             
  |                           |   (provide)      |                           |             
  +---------------------------+                  +---------------------------+             
                                                                                      
```

## Description of the components

In terms of states and transitions, both components are similar. They are composed of:

* 4 states: 'initiated" (the initial state), 'installed', 'configured' and 'running'.

* and 3 transitions: 'install', 'configure' and 'run'.

### Provider ports

Their ports however, differ. The Provider component has two 'provide' ports:

* `provider_data` (provide): attached to the `initiated` state, it aims at
  providing data about the provider (e.g. IP address and port). This can be
  used to exchange data between two components;

* `provider_serv` (provide): attached to the `running` state, it returns 'True'
  if its related state is active. This can be used to express a functional
  dependency between components.
  
### User ports

The User component has three ports: two 'use' ports, and one 'provide' port:

* `provider_data` (use): the 'use' counterpart of the `provider_data` port is
  attached to the `configure` transition. It aims at fetching data from the Provider
  (e.g. IP address and port). Its attached transition can only be fired if:
  * the User `installed` state is active;
  * the Provider `initiated` state is active (which activates its related
    `provider_data` port);
  * User and Provider are connected.
  

* `provider_serv` (use): the 'use' counterpart of the `provider_serv` port is
  attached to the `run` transition. It aims at fetching data from the Provider
  (e.g. IP address and port). Its attached transition can only be fired if:
  * the User `configured` state is active;
  * the Provider `running` state is active (which activates its related
    `provider_serv` port);
  * User and Provider are connected.

* `user_serv` (provide): attached to the `running` state, it returns 'True'
  if its related state is active. This can be used to express a functional
  dependency with other components (not included in this example).

## Play with the example

Fire a terminal at the project root path and run `python3` (`ipython3` is
preferred) from there:

``` bash
python/mad $ python3
Python 3.6.4 (default, Dec 23 2017, 19:07:07)
[GCC 7.2.1 20171128] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from assembly import Assembly
>>> from components.user_provider.user import User
>>> from components.user_provider.provider import Provider
>>>
>>>
>>> # Instanciate the two components:
>>> user = User()
>>> provider = Provider()
>>>
>>> # Instanciate the assembly:
>>> assembly = Assembly([
>>>     [user, 'user'],
>>>     [provider, 'provider']
>>> ])
>>>
>>> # Run the deployment while the two components are not connected:
>>> assembly.auto_run()
(1/3) Installation of the component User.
(1/3) Installlation of the component Provider.
[User] Successfully moved from initiated to installed

[Provider] Successfully moved from initiated to installed

(2/3) Configuration of the component Provider.
fail: Condition "provider_data" from the "configure" transition is not valid
[Provider] Successfully moved from installed to configured
[User] Failed to move from installed to configured


(3/3) Component Provider is running
[User] Deployment is not finished
  Current status: {'installed'}
[Provider] Successfully moved from configured to running

[Provider] Reach the final place.

>>> # Check the current state:
>>> assembly.check_dep()
user not in final state
False
>>> user.current_places
{'installed'}
>>> provider.current_places
{'running'}

>>> # Connect the two components which leads to finish the deployment:
>>> assembly.auto_connect('user', 'provider')
Place "configured" of "User" is not activated for now.
(2/3) Configuration of the component User.
User received the following data: {'provider_ip': '192.168.0.1', 'provider_port': '3306'},
Configuration can proceed.
[User] Successfully moved from installed to configured

(3/3) Component User is running.
[User] Successfully moved from configured to running

>>> # Check the current state:
>>> assembly.check_dep()
True
>>> user.current_places
{'running'}
>>> provider.current_places
{'running'}
```

