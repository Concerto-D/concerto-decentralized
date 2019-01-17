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
    
    def deploy(self):
        self.print("### DEPLOYING ####")
        self.client = Client()
        self.server = Server()
        self.add_component('client', self.client)
        self.add_component('server', self.server)
        self.connect('client', 'server_ip',
                    'server', 'ip')
        self.connect('client', 'service',
                    'server', 'service')
        self.change_behavior('client', 'install_start')
        self.change_behavior('server', 'deploy')
        self.wait('client')
        self.synchronize()
        
    def suspend(self):
        self.print("### SUSPENDING ###")
        self.change_behavior('client', 'stop')
        self.change_behavior('server', 'stop')
        self.wait('server')
        self.synchronize()
        
    def restart(self):
        self.print("### RESTARTING ###")
        self.change_behavior('client', 'install_start')
        self.change_behavior('server', 'deploy')
        self.wait('client')
        self.synchronize()
        

def time_test(verbosity : int = 0, printing : bool = False, print_time : bool = False) -> float:
    start_time : float = time.perf_counter()
    
    if printing: Printer.st_tprint("Main: creating the assembly")
    sca = ServerClient()
    sca.set_use_gantt_chart(True)
    sca.set_verbosity(verbosity)
    sca.set_print_time(print_time)
    
    if printing: Printer.st_tprint("Main: deploying the assembly")
    sca.deploy()
    
    if printing: Printer.st_tprint("Main: waiting a little before reconfiguring")
    time.sleep(3)
    
    sca.suspend()
    if printing: Printer.st_tprint("Main: waiting a little before restarting")
    time.sleep(5)
    
    sca.restart()
    
    end_time : float = time.perf_counter()
    total_time = end_time-start_time
    if printing: Printer.st_tprint("Total time in seconds: %f"%total_time)
    
    sca.terminate()
    gc : GanttChart = sca.get_gantt_chart()
    gc.export_gnuplot("results.gpl")
    return total_time
    
        

if __name__ == '__main__':
    time_test(
        verbosity = 2,
        printing = False,
        print_time = True
    )
