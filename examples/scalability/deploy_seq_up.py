#!/usr/bin/python3

import sys
import time, datetime

from concerto.all import *

from examples.scalability.provider import Provider
from examples.scalability.user import User
from examples.scalability.userprovider import UserProvider
from examples.utils import *


class DeploySeqUp(Assembly):
    def __init__(self, nb_comp : int):
        self.nb_comp = nb_comp
        
        Assembly.__init__(self)
        
        self.provider = Provider()
        self.add_component('provider', self.provider)
        
        # list of user-providers
        self.ups = []

        # user-providers created only if N > 2
        for i in range(0, self.nb_comp-2):
            self.ups.append(UserProvider())
            self.add_component(self.name_for_up(i), self.ups[i])
            if i > 0:
                self.connect(self.name_for_up(i-1), 'servicep',
                                  self.name_for_up(i), 'serviceu')
            else:
                self.connect('provider', 'service',
                                  self.name_for_up(i), 'serviceu')

        # last user
        self.user = User()
        self.add_component('user', self.user)
        if self.nb_comp <= 2:
            self.connect('provider', 'service', 'user', 'serviceu')
        else:
            self.connect(self.name_for_up(self.nb_comp-3), 'servicep',
                              'user', 'serviceu')
        self.synchronize()
            
    def deploy(self):
        self.change_behavior('provider', 'start')
        for i in range(0, self.nb_comp-2):
            self.change_behavior(self.name_for_up(i), 'start')
        self.change_behavior('user', 'start')
        self.wait('user')
        self.synchronize()
    
    @staticmethod
    def name_for_up(id : int):
        return "up" + str(id)


def time_test(nb_comp : int, printing : bool = False) -> float:
    if nb_comp < 2:
        print("*** Warning: at least 2 components are deployed by this "
        "example. 2 components will be deployed.\n")
        nb_comp = 2
    
    start_time : float = time.perf_counter()

    ass = DeploySeqUp(nb_comp)
    ass.set_verbosity(-1)
    ass.deploy()
    
    end_time : float = time.perf_counter()
    total_time = end_time-start_time
    if (printing): print("Total time in seconds: %f"%total_time)
    
    ass.terminate()
    return total_time



if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("*** Error: missing parameter!\n")
        print("deploy_seq_up.py <number of components to deploy "
              "sequentially>\n")
        sys.exit(-1)
    
    nb_comp = int(sys.argv[1])
    time_test(
        nb_comp=nb_comp,
        printing=True
    )
