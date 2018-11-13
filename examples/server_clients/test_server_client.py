#!/usr/bin/python3

from madpp.all import *
from madpp.utility import Printer
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
        print("### DEPLOYING ####")
        self.connect('client', 'server_ip',
                    'server', 'ip')
        self.connect('client', 'service',
                    'server', 'service')
        self.change_behavior('client', 'install_start')
        self.change_behavior('server', 'deploy')
        self.wait('client')
        self.synchronize()
        
    def suspend(self):
        print("### SUSPENDING ###")
        self.change_behavior('client', 'stop')
        self.change_behavior('server', 'stop')
        self.wait('server')
        self.synchronize()
        
    def restart(self):
        print("### RESTARTING ###")
        self.change_behavior('client', 'install_start')
        self.change_behavior('server', 'deploy')
        self.wait('client')
        self.synchronize()
        

def time_test(verbosity : int = 0, print_time : bool = False) -> float:
    start_time : float = time.clock()
    
    Printer.st_tprint("Main: creating the assembly")
    sca = ServerClient()
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
        verbosity = 0,
        print_time = True
    )
