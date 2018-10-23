#!/usr/bin/python3

import sys
import time, datetime

from madpp.all import *

from examples.scalability.provider import Provider
from examples.scalability.user_Ntrans import UserNTrans
from examples.utils import *


class DeployParUp(Assembly):
    def __init__(self, nb_comp : int, nb_trans : int):
        self.nb_comp = nb_comp
        self.nb_trans = nb_trans
        
        Assembly.__init__(self)
        
        self.provider = Provider()
        self.add_component('provider', self.provider)
        self.users = []
        for i in range(0, self.nb_comp):
            self.users.append(UserNTrans(self.nb_trans))
            self.add_component(self.name_for_user(i), self.users[i])
            
    def deploy(self):
        for i in range(0, self.nb_comp):
            self.connect('provider', 'service',
                         self.name_for_user(i), 'service')
        self.change_behavior('provider', 'start')
        for i in range(0, self.nb_comp):
            self.change_behavior(self.name_for_user(i), 'start')
        print("Waiting provider")
        self.wait('provider')
        for i in range(0, self.nb_comp):
            print("Waiting user_n_trans %d"%i)
            self.wait(self.name_for_user(i))
    
    @staticmethod
    def name_for_user(id : int):
        return "u" + str(id)
        

def time_test(nb_comp : int, nb_trans : int) -> float:
    tprint_show(False)
    
    if nb_comp < 1:
        print("*** Warning: at least 1 user component is deployed by "
                "this example. 1 component will be deployed.\n")
        nb_comp = 1
    if nb_trans < 1:
        print("*** Warning: at least 1 transition is needed inside the "
                "user components. 1 transition will be deployed.\n")
        nb_trans = 1
    
    start_time : float = time.clock()
        
    tprint("Creating assembly")

    ass = DeployParUp(nb_comp, nb_trans)
        
    tprint("Deploying")

    ass.deploy()
    
    end_time : float = time.clock()
    total_time = end_time-start_time
    print("Total time in seconds: %f"%total_time)
    
    ass.terminate()
    return total_time
    
        

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("*** Error: missing parameters!\n")
        print("deploy_par_up.py <number of user components> <number of "
              "transitions inside user components>\n")
        sys.exit(-1)
    
    nb_comp = int(sys.argv[1])
    nb_trans = int(sys.argv[2])
    time_test(nb_comp, nb_trans)
