#!/usr/bin/python3

from concerto.all import *
from concerto.utility import Printer
import time, datetime

from server_clients_assembly import ServerClients
        

def time_test(nb_clients : int, verbosity : int = 0, printing : bool = False, print_time : bool = False) -> float:
    start_time : float = time.perf_counter()
    
    if printing: Printer.st_tprint("Main: creating the assembly")
    sca = ServerClients(nb_clients)
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
    return total_time
    

if __name__ == '__main__':
    time_test(
        nb_clients = 3,
        verbosity = 1,
        printing = True,
        print_time = True
    )
