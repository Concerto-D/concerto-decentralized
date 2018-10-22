#!/usr/bin/python3

from madpp.all import *
import time, datetime

from client import Client
from server import Server
from examples.utils import *


class ServerClient(Assembly):
    def __init__(self):
        Assembly.__init__(self)
        self.client = Client()
        self.server = Server()
        self.add_component('client', self.client)
        self.add_component('server', self.server)
    
    def deploy(self):
        tprint("### DEPLOYING ####")
        self.connect('client', 'server_ip',
                    'server', 'ip')
        self.connect('client', 'service',
                    'server', 'service')
        self.change_behavior('client', 'install_start')
        self.change_behavior('server', 'deploy')
        tprint("Assembly: waiting client")
        self.wait('client')
        tprint("Assembly: waiting server")
        self.wait('server')
        
    def suspend(self):
        tprint("### SUSPENDING ###")
        self.change_behavior('client', 'stop')
        self.wait('client')
        self.change_behavior('server', 'stop')
        self.wait('server')
        
    def restart(self):
        tprint("### RESTARTING ###")
        
        self.change_behavior('client', 'install_start')
        self.change_behavior('server', 'deploy')
        tprint("Assembly: waiting client")
        self.wait('client')
        tprint("Assembly: waiting server")
        self.wait('server')
        
        
        

if __name__ == '__main__':
    tprint_show(False)
    
    sca = ServerClient()
    
    start_time : float = time.clock()
    sca.deploy()
    
    tprint("Main: waiting a little before reconfiguring")
    time.sleep(3)
    
    sca.suspend()
    tprint("Main: server maintenance")
    time.sleep(5)
    
    tprint("Main: maintenance over")
    sca.restart()
    
    end_time : float = time.clock()
    print("Total time in seconds: %f"%(end_time-start_time))
    
    sca.terminate()
