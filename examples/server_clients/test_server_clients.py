#!/usr/bin/python3

from madpp.all import *
from madpp.utility import Printer
import time, datetime

from client import Client
from server import Server
from examples.utils import *


class ServerClient(Assembly):
    def __init__(self, nb_clients):
        self.nb_clients = nb_clients
        Assembly.__init__(self)
        
        self.clients = []
        for i in range(self.nb_clients):
            self.clients.append(Client())
            self.add_component(self.client_name(i), self.clients[i])
        
        self.server = Server()
        self.add_component('server', self.server)
        self.synchronize()
    
    @staticmethod
    def client_name(id : int):
        return 'client%d'%id
    
    def deploy(self):
        print("### DEPLOYING ####")
        for i in range(self.nb_clients):
            self.connect(self.client_name(i), 'server_ip',
                    'server', 'ip')
            self.connect(self.client_name(i), 'service',
                    'server', 'service')
            self.change_behavior(self.client_name(i), 'install_start')
        self.change_behavior('server', 'deploy')
        for i in range(self.nb_clients):
            self.wait(self.client_name(i))
        self.synchronize()
        
    def suspend(self):
        print("### SUSPENDING ###")
        for i in range(self.nb_clients):
            self.change_behavior(self.client_name(i), 'stop')
        self.change_behavior('server', 'stop')
        self.wait('server')
        self.synchronize()
        
    def restart(self):
        print("### RESTARTING ###")
        for i in range(self.nb_clients):
            self.change_behavior(self.client_name(i), 'install_start')
        self.change_behavior('server', 'deploy')
        for i in range(self.nb_clients):
            self.wait(self.client_name(i))
        self.synchronize()
        

def time_test(nb_clients : int, verbosity : int = 0, print_time : bool = False) -> float:
    start_time : float = time.clock()
    
    Printer.st_tprint("Main: creating the assembly")
    sca = ServerClient(nb_clients)
    sca.set_verbosity(verbosity)
    sca.set_print_time(print_time)
    
    Printer.st_tprint("Main: deploying the assembly")
    sca.deploy()
    
    Printer.st_tprint("Main: waiting a little before reconfiguring")
    time.sleep(3)
    
    sca.suspend()
    Printer.st_tprint("Main: waiting a little before restarting")
    time.sleep(5)
    
    sca.restart()
    
    end_time : float = time.clock()
    total_time = end_time-start_time
    print("Total time in seconds: %f"%total_time)
    
    sca.terminate()
    return total_time
    
        

if __name__ == '__main__':
    time_test(
        nb_clients = 1000,
        verbosity = -1,
        print_time = True
    )
