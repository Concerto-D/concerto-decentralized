#!/usr/bin/python3

import time, datetime
from typing import Dict, Tuple, List, Set

from madpp.all import *
from madpp.gantt_chart import GanttChart

from server import Server
from dep import Dep
from examples.utils import *


class ServerDeps(Assembly):
    # deps_times: for each dependency, [config time on server, allocation time on dep, update time on dep]
    def __init__(self, t_sa : float, t_sc : List[float], t_sr : float, t_ss : List[float], t_sp : List[float], t_di : List[float], t_dr : List[float], t_du : List[float]):
        Assembly.__init__(self)
        self.server = Server(t_sa, t_sc, t_sr, t_ss, t_sp)
        self.nb_deps = len(t_sc)
        self.deps = [Dep(i, t_di[i], t_dr[i], t_du[i]) for i in range(self.nb_deps)]
            
    @staticmethod
    def dep_name(i : int):
        return "dep%d"%i
            
    
    def deploy(self):
        self.print("### DEPLOYING ###")
        self.add_component('server', self.server)
        for i in range(len(self.deps)):
            self.add_component(self.dep_name(i), self.deps[i])
            self.connect(self.dep_name(i), 'service',
                         'server', Server.name_for_dep_service(i))
            self.connect(self.dep_name(i), 'ip',
                         'server', Server.name_for_dep_ip(i))
        self.change_behavior('server', 'deploy')
        for i in range(len(self.deps)):
            self.change_behavior(self.dep_name(i), 'deploy')
        self.wait('server')
        self.synchronize()
        
    def update(self):
        self.print("### UPDATING ####")
        self.change_behavior('server', 'suspend')
        for i in range(len(self.deps)):
            self.change_behavior(self.dep_name(i), 'update')
        
        self.change_behavior('server', 'deploy')
        for i in range(len(self.deps)):
            self.change_behavior(self.dep_name(i), 'deploy')
        self.wait('server')
        self.synchronize()
    

def time_test(verbosity : int = -1, printing : bool = True, print_time : bool = False,
              t_sa=1., t_sc=[1.], t_sr=1., t_ss=[1.], t_sp=[1.], t_di=[1.], t_dr=[1.], t_du=[1.]):
    
    nb_deps = len(t_sc)
    if printing: Printer.st_tprint("Main: creating the assembly")
    sda = ServerDeps(t_sa, t_sc, t_sr, t_ss, t_sp, t_di, t_dr, t_du)
    sda.set_verbosity(verbosity)
    sda.set_print_time(print_time)
    sda.set_use_gantt_chart(False)
    
    if printing: Printer.st_tprint("Main: deploying the assembly")
    deploy_start_time : float = time.perf_counter()
    sda.deploy()
    deploy_end_time : float = time.perf_counter()
    
    if printing: Printer.st_tprint("Main: waiting a little before updating")
    time.sleep(1)
    
    if printing: Printer.st_tprint("Main: updating")
    update_start_time : float = time.perf_counter()
    sda.update()
    update_end_time : float = time.perf_counter()
    
    if printing: Printer.st_tprint("Main: update finished")
    
    deploy_time = deploy_end_time - deploy_start_time
    update_time = update_end_time - update_start_time
    total_time = deploy_time + update_time
    Printer.st_tprint("Total time in seconds: %f\n  deploy: %f\n  reconf: %f"%(total_time,deploy_time,update_time))
    
    deploy_theoretical_time = max(max([t_di[i]+t_dr[i] for i in range(nb_deps)]), t_sr+max([t_sc[i]+max(t_sa,t_di[i]) for i in range(nb_deps)]))
    reconf_theoretical_time = max(max([t_du[i]+t_ss[i]+t_dr[i] for i in range(nb_deps)]),t_sr+max([t_ss[i]+t_sp[i] for i in range(nb_deps)]))
    total_theoretical_time = deploy_theoretical_time + reconf_theoretical_time
    Printer.st_tprint("Theoretical time in seconds: %f\n  deploy: %f\n  reconf: %f"%(total_theoretical_time,deploy_theoretical_time,reconf_theoretical_time))
    
    sda.terminate()
    return total_time
    

if __name__ == '__main__':
    time_test(
        t_sa=2.,
        t_sc=[3., 1.],
        t_sr=6.,
        t_ss=[4., 8.],
        t_sp=[5., 7.],
        t_di=[0.5, 1.5],
        t_dr=[2.5, 3.5],
        t_du=[4.5, 5.5]
    )
