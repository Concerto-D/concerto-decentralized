# -*- coding: utf-8 -*-
""" This component is part of the use/provide toy example which depicts
how MAD components can exchange information. This component is the HW_Client
counterpart, whose places, transitions and ports are depicted as follow:

+--------------------------------------------------------------+
|                                                              |
|                     HW_Client Component                      |
|                                                              |
|                 +-------------------------+                  |
|                 |                         |                  |
|                 |        +-------+        |                  |
|                 |        |running|        |                  |
|                 |        +---+---+        |                  |
|    using_hw     |            ^            |                  |
|      (use)      |            |            |                  |
|            +--------------> +-+ run       |                  |
|                 |            |            |                  |
|                 |       +----+-----+      |                  |
|                 |       |configured|      |                  |
|                 |       +----+-----+      |                  |
|    hw_ref_in    |            ^            |                  |
|      (use)      |            |            |                  |
|            +--------------> +-+ configure |                  |
|                 |            |            |                  |
|                 |       +----+----+       |                  |
|                 |       |installed|       |                  |
|                 |       +----+----+       |                  |
|                 |            ^            |                  |
|                 |            |            |                  |
|                 |           +-+ install   |                  |
|                 |            |            |                  |
|                 |  +---------+---------+  |                  |
|                 |  |initiated (initial)|  |                  |
|                 |  +-------------------+  |                  |
|                 |                         |                  |
|                 +-------------------------+                  |
|                                                              |
+--------------------------------------------------------------+


"""

from mad import PetriNet
import requests, time, threading

class HW_Client(object):
    """ Define a new component of type HW_Client."""

    MYCOLOR = "\x1b[36m" # CYAN
    RESET = "\x1b[0m" # RESET
    
    # This empty variable will be filled by a Provider component:
    hw_ref = None
    
    # Define the different places of the component:
    places = ['initiated', 'installed', 'configured', 'running']

    # Define the different transitions of the component:
    transitions = [
            {'name': 'install', 'source': 'initiated', 'dest': 'installed'},
            {'name': 'configure', 'source': 'installed', 'dest': 'configured'},
            {'name': 'run', 'source': 'configured', 'dest': 'running'}
    ]

    # Define the different ports - the first one is a 'provide' port attached
    # to the state 'running', while the two remaining are 'use' ports, attached
    # to different transitions:
    ports = [
            {'name': 'using_hw', 'inside_link': 'run'},
            {'name': 'hw_ref_in', 'inside_link': 'configure'}
    ]

    def __init__(self, step=False):

        # Initiate our component as a PetriNet, with its places, transitions,
        # ports and its initial place:
        self.net = PetriNet(self, self.places, self.transitions, self.ports,
                initial='initiated')

    # Transition callbacks are defined here:
    def func_install(self):
        print(self.MYCOLOR+"[HW_Client] (1/3) Installation."+self.RESET)

    def func_configure(self):
        # The configure transition has a 'from_data' port which is used
        # to transfer data from the provider to the user component.
        # This callback is only fired if the two components are connected and
        # if the remote port is activated.
        # The port creates a local method called after its name, which gives a
        # reference to the related remote method.
        print(self.MYCOLOR+"[HW_Client] (2/3) Configuring...."+self.RESET)
        self.hw_ref = getattr(self, 'hw_ref_in')()
        print(self.MYCOLOR+"[HW_Client] (2/3) Got configution data : %s" % self.hw_ref+self.RESET)

    def func_run(self):
        print(self.MYCOLOR+"[HW_Client] (3/3) Running: launching a thread..."+self.RESET)
        self.thread = threading.Thread(target=self.myrun)
        self.thread.start()
        print(self.MYCOLOR+"[HW_Client] (3/3) Running: done"+self.RESET)

    # This method is defined to implement the 'provide' port:
    def another_serv(self):
        return self.net.get_place('running').state

    ############################################################

    def myrun(self):
        print(self.MYCOLOR+"[HW_Client/run] thread = %s" % self.thread+self.RESET)
        url = "http://" +  self.hw_ref['provider_ip'] + ":" + self.hw_ref['provider_port']
        print(self.MYCOLOR+"[HW_Client/run] mget "+url+" ...."+self.RESET)
        r = requests.get(url)
        print(r.text)
        print(self.MYCOLOR+"[HW_Client/run] got : "+r.text)

    def finish(self):
        print(self.MYCOLOR+"[HW_Client] Waiting end..."+self.RESET)
        self.thread.join()
        print(self.MYCOLOR+"[HW_Client] ended."+self.RESET)
