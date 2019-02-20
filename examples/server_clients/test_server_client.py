#!/usr/bin/python3

from concerto.all import *
from concerto.utility import Printer
import time, datetime

from client import Client
from server import Server
from examples.utils import *


class ServerClient(Assembly):
    def __init__(self, t_sa=4., t_sr=4., t_su=1., t_sc=0.5, t_ci1=1., t_ci2=1., t_cc=1., t_cr=1., t_cs1=2., t_cs2=0.):
        self.t_sa = t_sa
        self.t_sr = t_sr
        self.t_su = t_su
        self.t_sc = t_sc
        self.t_ci1 = t_ci1
        self.t_ci2 = t_ci2
        self.t_cc = t_cc
        self.t_cr = t_cr
        self.t_cs1 = t_cs1
        self.t_cs2 = t_cs2
        self.server = Server(t_sa=self.t_sa, t_sr=self.t_sr, t_su=self.t_su, t_sc=self.t_sc)
        self.client = Client(t_ci1=self.t_ci1, t_ci2=self.t_ci2, t_cc=self.t_cc, t_cr=self.t_cr, t_cs1=self.t_cs1, t_cs2=self.t_cs2)
        Assembly.__init__(self)
    
    def deploy(self):
        self.print("### DEPLOYING ####")
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
        
    def maintain(self):
        self.print("### MAINTAINING ###")
        self.change_behavior('client', 'stop')
        self.change_behavior('server', 'stop')
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
    gc.export_json("results.json")
    return total_time


def time_test_params(verbosity : int = -1, printing : bool = True, print_time : bool = False,
                     t_sa=4., t_sr=4., t_su=1., t_sc=0.5, t_ci1=1., t_ci2=1., t_cc=1., t_cr=1., t_cs1=2., t_cs2=0.):
    
    if printing: Printer.st_tprint("Main: creating the assembly")
    sca = ServerClient(t_sa, t_sr, t_su, t_sc, t_ci1, t_ci2, t_cc, t_cr, t_cs1, t_cs2)
    sca.set_use_gantt_chart(False)
    sca.set_verbosity(verbosity)
    sca.set_print_time(print_time)
    
    if printing: Printer.st_tprint("Main: deploying the assembly")
    deploy_start_time : float = time.perf_counter()
    sca.deploy()
    deploy_end_time : float = time.perf_counter()
    total_deploy_time = deploy_end_time-deploy_start_time
    
    if printing: Printer.st_tprint("Main: waiting a little before reconfiguring")
    time.sleep(1)
    
    if printing: Printer.st_tprint("Main: reconfiguring the assembly")
    reconf_start_time : float = time.perf_counter()
    sca.maintain()
    reconf_end_time : float = time.perf_counter()
    total_reconf_time = reconf_end_time-reconf_start_time
    
    total_time = total_deploy_time+total_reconf_time
    Printer.st_tprint("Total time in seconds: %f\n  deploy: %f\n  reconf: %f"%(total_time,total_deploy_time,total_reconf_time))
    
    deploy_theoretical_time = max(t_sa+t_sr,t_cr+max(t_ci2,t_cc+max(t_ci1,t_sa)))
    reconf_theoretical_time = max(t_cs1+t_cs2+t_cr,t_sr+t_cs1+max(t_su,t_sc))
    total_theoretical_time = deploy_theoretical_time + reconf_theoretical_time
    Printer.st_tprint("Theoretical time in seconds: %f\n  deploy: %f\n  reconf: %f"%(total_theoretical_time,deploy_theoretical_time,reconf_theoretical_time))
    
    sca.terminate()
    return total_deploy_time, total_reconf_time, deploy_theoretical_time, reconf_theoretical_time


def random_tests(nb_trials, min_value=0., max_value=10.):
    from random import uniform
    from json import dumps
    from sys import stderr
    results = {
        "trials": [],
        "max_distance_deploy": 0.,
        "max_distance_reconf": 0.
    }
    for i in range(nb_trials):
        print("Trial %d/%d"%(i+1,nb_trials), file=stderr)
        t_sa  = uniform(min_value,max_value)
        t_sr  = uniform(min_value,max_value)
        t_su  = uniform(min_value,max_value)
        t_sc  = uniform(min_value,max_value)
        t_ci1 = uniform(min_value,max_value)
        t_ci2 = uniform(min_value,max_value)
        t_cc  = uniform(min_value,max_value)
        t_cr  = uniform(min_value,max_value)
        t_cs1 = uniform(min_value,max_value)
        t_cs2 = uniform(min_value,max_value)
        trial = {
            "t_sa": t_sa,
            "t_sr": t_sr,
            "t_su": t_su,
            "t_sc": t_sc,
            "t_ci1": t_ci1,
            "t_ci2": t_ci2,
            "t_cc": t_cc,
            "t_cr": t_cr,
            "t_cs1": t_cs1,
            "t_cs2": t_cs2
        }
        real_deploy, real_reconf, theoretical_deploy, theoretical_reconf = time_test_params(verbosity=-1, printing = False, print_time = False,
                     t_sa=t_sa, t_sr=t_sr, t_su=t_su, t_sc=t_sc, t_ci1=t_ci1, t_ci2=t_ci2, t_cc=t_cc, t_cr=t_cr, t_cs1=t_cs1, t_cs2=t_cs2)
        distance_deploy = abs(real_deploy-theoretical_deploy)
        distance_reconf = abs(real_reconf-theoretical_reconf)
        trial["real_deploy"] = real_deploy
        trial["real_reconf"] = real_reconf
        trial["theoretical_deploy"] = theoretical_deploy
        trial["theoretical_reconf"] = theoretical_reconf
        trial["distance_deploy"] = distance_deploy
        trial["distance_reconf"] = distance_reconf
        results["trials"].append(trial)
        if (distance_deploy) > results["max_distance_deploy"]:
            results["max_distance_deploy"] = distance_deploy
        if (distance_reconf) > results["max_distance_reconf"]:
            results["max_distance_reconf"] = distance_reconf
    print(dumps(results, indent='\t'))
        
    
        

if __name__ == '__main__':
    #time_test(
        #verbosity = 2,
        #printing = False,
        #print_time = True
    #)
    #time_test_params(
        #t_sa  = 4. ,
        #t_sr  = 4. ,
        #t_su  = 1. ,
        #t_sc  = 0.5,
        #t_ci1 = 1. ,
        #t_ci2 = 1. ,
        #t_cc  = 1. ,
        #t_cr  = 1. ,
        #t_cs1 = 2. ,
        #t_cs2 = 0.
    #)
    #time_test_params(
        #t_sa  = 5. ,
        #t_sr  = 3. ,
        #t_su  = 8. ,
        #t_sc  = 7. ,
        #t_ci1 = 4. ,
        #t_ci2 = 10. ,
        #t_cc  = 2.5 ,
        #t_cr  = 2 ,
        #t_cs1 = 1. ,
        #t_cs2 = 1.5
    #)
    random_tests(300)
