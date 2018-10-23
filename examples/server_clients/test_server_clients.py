#!/usr/bin/python3

from madpp.all import *
import time, datetime

from client import Client
from server import Server
from examples.utils import *


class ServerClient(Assembly):
    def __init__(self):
        Assembly.__init__(self)
        self.nb_clients = 2000
        self.clients = []
        for i in range(self.nb_clients):
            new_client = Client()
            self.clients.append(new_client)
            self.add_component('client%d'%i, new_client)
        self.server = Server()
        self.add_component('server', self.server)
    
    def deploy(self):
        tprint("### DEPLOYING ####")
        for i in range(self.nb_clients):
            self.connect('client%d'%i, 'server_ip',
                        'server', 'ip')
            self.connect('client%d'%i, 'service',
                        'server', 'service')
            self.change_behavior('client%d'%i, 'install_start')
        self.change_behavior('server', 'deploy')
        tprint("Assembly: waiting clients")
        for i in range(self.nb_clients):
            self.wait('client%d'%i)
        tprint("Assembly: waiting server")
        self.wait('server')
        
    def suspend(self):
        tprint("### SUSPENDING ###")
        for i in range(self.nb_clients):
            self.change_behavior('client%d'%i, 'stop')
        for i in range(self.nb_clients):
            self.wait('client%d'%i)
        self.change_behavior('server', 'stop')
        self.wait('server')
        
    def restart(self):
        tprint("### RESTARTING ###")
        
        for i in range(self.nb_clients):
            self.change_behavior('client%d'%i, 'install_start')
        self.change_behavior('server', 'deploy')
        tprint("Assembly: waiting clients")
        for i in range(self.nb_clients):
            self.wait('client%d'%i)
        tprint("Assembly: waiting server")
        self.wait('server')
        
    
def time_test() -> float:
    tprint_show(False)
    
    start_time : float = time.clock()
    
    sca = ServerClient()
    sca.deploy()
    
    tprint("Main: waiting a little before reconfiguring")
    time.sleep(3)
    
    sca.suspend()
    tprint("Main: server maintenance")
    time.sleep(5)
    
    tprint("Main: maintenance over")
    sca.restart()
    
    end_time : float = time.clock()
    total_time = end_time-start_time
    print("Total time in seconds: %f"%total_time)
    
    sca.terminate()
    return total_time
        

if __name__ == '__main__':
    time_test()
