#!/usr/bin/python3

import time, datetime

from concerto.all import *
from concerto.utility import Printer
from concerto.components.data_provider import DataProvider
from concerto.gantt_chart import GanttChart

from apt_utils import AptUtils
from ceph import Ceph
from chrony import Chrony
from docker import Docker
from mariadb import MariaDB
from python import Python
from registry import Registry
from sysbench import Sysbench
from sysbench_master import SysbenchMaster


class GaleraAssembly(Assembly):
    class ComponentSet():
        def __init__(self):
            self.apt_utils = None
            self.python = None
            self.docker = None
            self.ceph = None
            self.registry = None
            self.chrony = None
            self.mariadb = None
            self.galera_master = None
            self.galera_worker = None
            self.sysbench_master = None
            self.sysbench = None
            
        @staticmethod
        def _build_common_set():
            ass = GaleraAssembly.ComponentSet()
            ass.apt_utils = AptUtils()
            ass.python = Python()
            ass.docker = Docker()
            ass.chrony = Chrony()
            return ass
            
        @staticmethod
        def build_registry_set():
            ass = GaleraAssembly.ComponentSet._build_common_set()
            ass.ceph = Ceph()
            ass.registry = Registry()
            return ass
            
        @staticmethod
        def _build_db_set():
            ass = GaleraAssembly.ComponentSet._build_common_set()
            ass.mariadb = MariaDB()
            ass.sysbench = Sysbench()
            return ass
            
        @staticmethod
        def build_master_set():
            ass = GaleraAssembly.ComponentSet._build_db_set()
            ass.sysbench_master = SysbenchMaster()
            return ass
            
        @staticmethod
        def build_worker_set():
            ass = GaleraAssembly.ComponentSet._build_db_set()
            return ass
    
    def __init__(self, nb_workers = 2):
        if nb_workers < 2:
            raise Exception("GaleraAssembly: error, the number of workers must be at least 2 for Galera to work")
        self.nb_workers = nb_workers
        Assembly.__init__(self)
        
        # Registry
        self.registry_set = self.ComponentSet.build_registry_set()
        self.add_component('registry_apt_utils', self.registry_set.apt_utils)
        self.add_component('registry_python', self.registry_set.python)
        self.add_component('registry_docker', self.registry_set.docker)
        self.add_component('registry_ceph', self.registry_set.ceph)
        self.add_component('registry_registry', self.registry_set.registry)
        self.add_component('registry_chrony', self.registry_set.chrony)
        self.connect('registry_apt_utils', 'apt_utils',
                     'registry_docker', 'apt_utils')
        self.connect('registry_python', 'python_full',
                     'registry_registry', 'python_full')
        self.connect('registry_ceph', 'ceph',
                     'registry_registry', 'ceph')
        self.connect('registry_docker', 'docker',
                     'registry_registry', 'docker')
        
        # DB Master
        self.master_set = self.ComponentSet.build_master_set()
        self.add_component('master_apt_utils', self.master_set.apt_utils)
        self.add_component('master_python', self.master_set.python)
        self.add_component('master_docker', self.master_set.docker)
        self.add_component('master_mariadb', self.master_set.mariadb)
        self.add_component('master_sysbench', self.master_set.sysbench)
        self.add_component('master_sysbench_master', self.master_set.sysbench_master)
        self.add_component('master_chrony', self.master_set.chrony)
        self.connect('master_apt_utils', 'apt_utils',
                     'master_docker', 'apt_utils')
        self.connect('master_python', 'python_full',
                     'master_mariadb', 'python_full')
        self.connect('master_docker', 'docker',
                     'master_mariadb', 'docker')
        self.connect('master_mariadb', 'mariadb',
                     'master_sysbench_master', 'mysql')
        self.connect('registry_registry', 'registry',
                     'master_mariadb', 'registry')
        
        # DB Workers
        self.worker_sets = []
        for i in range(self.nb_workers):
            prefix = 'worker%d'%i
            self.worker_sets.append(self.ComponentSet.build_worker_set())
            current_worker_set = self.worker_sets[i]
            self.add_component(prefix+'_apt_utils', current_worker_set.apt_utils)
            self.add_component(prefix+'_python', current_worker_set.python)
            self.add_component(prefix+'_docker', current_worker_set.docker)
            self.add_component(prefix+'_mariadb', current_worker_set.mariadb)
            self.add_component(prefix+'_sysbench', current_worker_set.sysbench)
            self.add_component(prefix+'_chrony', current_worker_set.chrony)
            self.connect(prefix+'_apt_utils', 'apt_utils',
                         prefix+'_docker', 'apt_utils')
            self.connect(prefix+'_python', 'python_full',
                         prefix+'_mariadb', 'python_full')
            self.connect(prefix+'_docker', 'docker',
                         prefix+'_mariadb', 'docker')
            self.connect('registry_registry', 'registry',
                         prefix+'_mariadb', 'registry')
    
    def _provide_data_custom(self, provider_name, data, component_name, input_port):
        dp = DataProvider(data)
        dp.force_hide_from_gantt_chart()
        self.add_component(provider_name, dp)
        self.connect(provider_name, 'data',
                     component_name, input_port)
        self.push_b(provider_name, 'provide')
        
    def _provide_data(self, data, component_name, input_port):
        self._provide_data_custom("%s_%s"%(component_name, input_port), data, component_name, input_port)
    
    def _stop_provide_data_custom(self, provider_name, component_name, input_port):
        self.disconnect(provider_name, 'data',
                        component_name, input_port)
        self.del_component(provider_name)
        
    def _stop_provide_data(self, component_name, input_port):
        self._stop_provide_data_custom("%s_%s"%(component_name, input_port), component_name, input_port)
        
    
    def _deploy(self, galera=False):
        def deploy_registry():
            self.push_b('registry_apt_utils', 'install')
            self.push_b('registry_python', 'install')
            self.push_b('registry_docker', 'install')
            self.push_b('registry_ceph', 'install')
            self.push_b('registry_registry', 'install')
            self.push_b('registry_chrony', 'install')
            #dummy data
            self._provide_data('', 'registry_docker', 'config')
            self._provide_data('', 'registry_chrony', 'config')
            self._provide_data('', 'registry_ceph', 'config')
            self._provide_data('', 'registry_ceph', 'id')
            self._provide_data('', 'registry_ceph', 'rdb')
        def deploy_master(mariadb_config='', mariadb_command=''):
            self.push_b('master_apt_utils', 'install')
            self.push_b('master_python', 'install')
            self.push_b('master_docker', 'install')
            self.push_b('master_mariadb', 'install')
            self.push_b('master_sysbench', 'install')
            self.push_b('master_sysbench_master', 'install')
            self.push_b('master_chrony', 'install')
            #dummy data
            self._provide_data('', 'master_docker', 'config')
            self._provide_data('', 'master_chrony', 'config')
            self._provide_data(mariadb_config, 'master_mariadb', 'config')
            self._provide_data(mariadb_command, 'master_mariadb', 'command')
            self._provide_data('', 'master_mariadb', 'root_pw')
            self._provide_data('', 'master_sysbench_master', 'db_credentials')
            self._provide_data('', 'master_sysbench_master', 'user_credentials')
            self._provide_data('', 'master_sysbench_master', 'my_ip')
        def deploy_worker(i, deploy_mariadb=False, mariadb_config='', mariadb_command=''):
            prefix = 'worker%d'%i
            self.push_b(prefix+'_apt_utils', 'install')
            self.push_b(prefix+'_python', 'install')
            self.push_b(prefix+'_docker', 'install')
            if deploy_mariadb:
                self.push_b(prefix+'_mariadb', 'install')
            self.push_b(prefix+'_sysbench', 'install')
            self.push_b(prefix+'_chrony', 'install')
            #dummy data
            self._provide_data('', prefix+'_docker', 'config')
            self._provide_data('', prefix+'_chrony', 'config')
            if deploy_mariadb:
                self._provide_data(mariadb_config, prefix+'_mariadb', 'config')
                self._provide_data(mariadb_command, prefix+'_mariadb', 'command')
                self._provide_data('', prefix+'_mariadb', 'root_pw')
            
        
        self.print("### DEPLOYING ####")
        deploy_registry()
        deploy_master()
        for i in range(self.nb_workers):
            if galera:
                deploy_worker(i, True)
            else:
                deploy_worker(i, False)
    
    
    def _deploy_cleanup(self, galera=False):
        def cleanup_registry():
            self._stop_provide_data('registry_docker', 'config')
            self._stop_provide_data('registry_chrony', 'config')
            self._stop_provide_data('registry_ceph', 'config')
            self._stop_provide_data('registry_ceph', 'id')
            self._stop_provide_data('registry_ceph', 'rdb')
        def cleanup_master():
            self._stop_provide_data('master_docker', 'config')
            self._stop_provide_data('master_chrony', 'config')
            self._stop_provide_data('master_mariadb', 'config')
            self._stop_provide_data('master_mariadb', 'command')
            self._stop_provide_data('master_mariadb', 'root_pw')
            self._stop_provide_data('master_sysbench_master', 'db_credentials')
            self._stop_provide_data('master_sysbench_master', 'user_credentials')
            self._stop_provide_data('master_sysbench_master', 'my_ip')
        def cleanup_worker(i, mariadb_deployed=False):
            prefix = 'worker%d'%i
            self._stop_provide_data(prefix+'_docker', 'config')
            self._stop_provide_data(prefix+'_chrony', 'config')
            if mariadb_deployed:
                self._stop_provide_data(prefix+'_mariadb', 'config')
                self._stop_provide_data(prefix+'_mariadb', 'command')
                self._stop_provide_data(prefix+'_mariadb', 'root_pw')
                
    
        cleanup_registry()
        cleanup_master()
        for i in range(self.nb_workers):
            if galera:
                cleanup_worker(i, True)
            else:
                cleanup_worker(i, False)
        
        
    def deploy_mariadb(self):
        self._deploy(False)
        self.wait('master_sysbench_master')
        self.synchronize()
        
    def deploy_mariadb_cleanup(self):
        self._deploy_cleanup(False)
        self.synchronize()
        
    def deploy_galera(self):
        self._deploy(True)
        self.wait('master_sysbench_master')
        self.synchronize()
        
    def deploy_galera_cleanup(self):
        self._deploy_cleanup(True)
        self.synchronize()
        
    def mariadb_to_galera(self):
        def reconf_master(mariadb_config='', mariadb_command=''):
            self.push_b('master_sysbench_master', 'suspend')
            self.push_b('master_mariadb', 'uninstall')
            self.push_b('master_mariadb', 'install')
            self.push_b('master_sysbench_master', 'install')
            #dummy data
            #self._provide_data(mariadb_config, 'master_mariadb', 'config')
            #self._provide_data(mariadb_command, 'master_mariadb', 'command')
            #self._provide_data('', 'master_mariadb', 'root_pw')
        def reconf_worker(i, mariadb_config='', mariadb_command=''):
            prefix = 'worker%d'%i
            self.push_b(prefix+'_mariadb', 'install')
            #dummy data
            self._provide_data(mariadb_config, prefix+'_mariadb', 'config')
            self._provide_data(mariadb_command, prefix+'_mariadb', 'command')
            self._provide_data('', prefix+'_mariadb', 'root_pw')
            
        
        self.print("## RECONFIGURING ##")
        for i in range(self.nb_workers):
            reconf_worker(i)
        reconf_master()
        for i in range(self.nb_workers):
            prefix = 'worker%d'%i
            self.wait(prefix+'_mariadb')
        self.synchronize()
        

def time_test(verbosity : int = 0, printing : bool = False, print_time : bool = False) -> float:
    
    if printing: Printer.st_tprint("Main: creating the assembly")
    deploy_start_time : float = time.clock()
    gass = GaleraAssembly()
    gass.set_verbosity(verbosity)
    gass.set_print_time(print_time)
    gass.set_use_gantt_chart(True)
    
    if printing: Printer.st_tprint("Main: deploying the assembly")
    gass.deploy_mariadb()
    deploy_end_time : float = time.clock()
    #gass.deploy_mariadb_cleanup()
    
    if printing: Printer.st_tprint("Main: waiting before reconfiguration")
    time.sleep(5)
    
    if printing: Printer.st_tprint("Main: reconfiguring to Galera")
    reconf_start_time : float = time.clock()
    gass.mariadb_to_galera()
    reconf_end_time : float = time.clock()
    
    total_deploy_time = deploy_end_time - deploy_start_time
    total_reconf_time = reconf_end_time - reconf_start_time
    total_time = total_deploy_time+total_reconf_time
    if printing: Printer.st_tprint("Total time in seconds: %f (deploy: %f, reconf: %f)"%(total_time, total_deploy_time, total_reconf_time))
    
    gass.terminate(debug=True)
    gc : GanttChart = gass.get_gantt_chart()
    gc.export_gnuplot("results.gpl")
    return total_time
    
        

if __name__ == '__main__':
    time_test(
        verbosity = 1,
        printing = True,
        print_time = True
    )
