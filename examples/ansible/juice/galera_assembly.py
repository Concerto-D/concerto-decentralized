#!/usr/bin/python3

import time, datetime

from madpp.all import *
from madpp.utility import Printer
from madpp.components.data_provider import DataProvider
from madpp.components.jinja2 import Jinja2
from madpp.gantt_chart import GanttChart

from components.apt_utils import AptUtils
from components.ceph import Ceph
from components.docker import Docker
from components.mariadb import MariaDB
from components.python import Python
from components.registry import Registry
from components.sysbench import Sysbench
from components.sysbench_master import SysbenchMaster


class GaleraAssembly(Assembly):
    class ComponentSet():
        def __init__(self):
            self.apt_utils = None
            self.python = None
            self.docker = None
            self.ceph = None
            self.registry = None
            self.mariadb = None
            self.galera_master = None
            self.galera_worker = None
            self.sysbench_master = None
            self.sysbench = None
            
        @staticmethod
        def _build_common_set(host):
            ass = GaleraAssembly.ComponentSet()
            ass.apt_utils = AptUtils(host)
            ass.python = Python(host)
            ass.docker = Docker(host)
            return ass
            
        @staticmethod
        def build_registry_set(host):
            ass = GaleraAssembly.ComponentSet._build_common_set(host)
            ass.ceph = Ceph(host)
            ass.registry = Registry(host)
            return ass
            
        @staticmethod
        def _build_db_set(host):
            ass = GaleraAssembly.ComponentSet._build_common_set(host)
            ass.mariadb = MariaDB(host)
            ass.sysbench = Sysbench(host)
            return ass
            
        @staticmethod
        def build_master_set(host):
            ass = GaleraAssembly.ComponentSet._build_db_set(host)
            ass.sysbench_master = SysbenchMaster(host)
            return ass
            
        @staticmethod
        def build_worker_set(host):
            ass = GaleraAssembly.ComponentSet._build_db_set(host)
            return ass
    
    def __init__(self, master_host, workers_hosts, registry_host, registry_ceph_mon_host):
        if len(workers_hosts) < 2:
            raise Exception("GaleraAssembly: error, the number of workers must be at least 2 for Galera to work")
        self.master_host = master_host
        self.workers_hosts = workers_hosts
        self.registry_host = registry_host
        self.registry_ceph_mon_host = registry_ceph_mon_host
        Assembly.__init__(self)
        
        # Registry
        self.registry_set = self.ComponentSet.build_registry_set(registry_host)
        self.add_component('registry_apt_utils', self.registry_set.apt_utils)
        self.add_component('registry_python', self.registry_set.python)
        self.add_component('registry_docker', self.registry_set.docker)
        self.add_component('registry_ceph', self.registry_set.ceph)
        self.add_component('registry_registry', self.registry_set.registry)
        self.connect('registry_apt_utils', 'apt_utils',
                     'registry_docker', 'apt_utils')
        self.connect('registry_python', 'python_full',
                     'registry_registry', 'python_full')
        self.connect('registry_ceph', 'ceph',
                     'registry_registry', 'ceph')
        self.connect('registry_docker', 'docker',
                     'registry_registry', 'docker')
        
        # DB Master
        self.master_set = self.ComponentSet.build_master_set(master_host)
        self.add_component('master_apt_utils', self.master_set.apt_utils)
        self.add_component('master_python', self.master_set.python)
        self.add_component('master_docker', self.master_set.docker)
        self.add_component('master_mariadb', self.master_set.mariadb)
        self.add_component('master_sysbench', self.master_set.sysbench)
        self.add_component('master_sysbench_master', self.master_set.sysbench_master)
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
        for i in range(len(self.workers_hosts)):
            prefix = 'worker%d'%i
            self.worker_sets.append(self.ComponentSet.build_worker_set(self.workers_hosts[i]))
            current_worker_set = self.worker_sets[i]
            self.add_component(prefix+'_apt_utils', current_worker_set.apt_utils)
            self.add_component(prefix+'_python', current_worker_set.python)
            self.add_component(prefix+'_docker', current_worker_set.docker)
            self.add_component(prefix+'_mariadb', current_worker_set.mariadb)
            self.add_component(prefix+'_sysbench', current_worker_set.sysbench)
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
        self.change_behavior(provider_name, 'provide')
        
    def _provide_data(self, data, component_name, input_port):
        self._provide_data_custom("%s_%s"%(component_name, input_port), data, component_name, input_port)
    
    def _stop_provide_data_custom(self, provider_name, component_name, input_port):
        self.disconnect(provider_name, 'data',
                        component_name, input_port)
        self.del_component(provider_name)
        
    def _stop_provide_data(self, component_name, input_port):
        self._stop_provide_data_custom("%s_%s"%(component_name, input_port), component_name, input_port)
    
    def _provide_jinja2(self, template_file_location, parameters, component_name, input_port):
        with open(template_file_location, 'r') as template_file:
            template_text = template_file.read()
        var_parameters_names = []
        const_parameters_values = {}
        for p in parameters:
            if parameters[p] is None:
                var_parameters_names.append(p)
            else:
                const_parameters_values[p] = parameters[p]
        j2 = Jinja2(template_text, var_parameters_names, const_parameters_values)
        j2.force_hide_from_gantt_chart()
        provider_name = "%s_%s"%(component_name, input_port)
        self.add_component(provider_name, j2)
        self.connect(provider_name, 'jinja2_result',
                     component_name, input_port)
        self.change_behavior(provider_name, 'generate')
        
    def _stop_provide_jinja2(self, component_name, input_port):
        provider_name = "%s_%s"%(component_name, input_port)
        self.disconnect(provider_name, 'jinja2_result',
                        component_name, input_port)
        self.del_component(provider_name)
                
        
    
    def _deploy(self, galera=False):
        def deploy_registry():
            self.change_behavior('registry_apt_utils', 'install')
            self.change_behavior('registry_python', 'install')
            self.change_behavior('registry_docker', 'install')
            self.change_behavior('registry_ceph', 'install')
            self.change_behavior('registry_registry', 'install')
            #dummy data
            self._provide_jinja2('templates/docker.conf.j2', {'registry_ip': self.registry_host, 'registry_port': None}, 'registry_docker', 'config')
            self._provide_jinja2('templates/ceph.conf.j2', {'registry_ceph_mon_host': self.registry_ceph_mon_host}, 'registry_ceph', 'config')
            self._provide_data('', 'registry_ceph', 'id')
            self._provide_data('', 'registry_ceph', 'rdb')
        def deploy_master(mariadb_config='', mariadb_command=''):
            self.change_behavior('master_apt_utils', 'install')
            self.change_behavior('master_python', 'install')
            self.change_behavior('master_docker', 'install')
            self.change_behavior('master_mariadb', 'install')
            self.change_behavior('master_sysbench', 'install')
            self.change_behavior('master_sysbench_master', 'install')
            #dummy data
            self._provide_jinja2('templates/docker.conf.j2', {'registry_ip': self.registry_host, 'registry_port': None}, 'master_docker', 'config')
            self._provide_data(mariadb_config, 'master_mariadb', 'config')
            self._provide_data(mariadb_command, 'master_mariadb', 'command')
            self._provide_data('', 'master_mariadb', 'root_pw')
            self._provide_data('', 'master_sysbench_master', 'db_credentials')
            self._provide_data('', 'master_sysbench_master', 'user_credentials')
            self._provide_data('', 'master_sysbench_master', 'my_ip')
        def deploy_worker(i, deploy_mariadb=False, mariadb_config='', mariadb_command=''):
            prefix = 'worker%d'%i
            self.change_behavior(prefix+'_apt_utils', 'install')
            self.change_behavior(prefix+'_python', 'install')
            self.change_behavior(prefix+'_docker', 'install')
            if deploy_mariadb:
                self.change_behavior(prefix+'_mariadb', 'install')
            self.change_behavior(prefix+'_sysbench', 'install')
            self._provide_jinja2('templates/docker.conf.j2', {'registry_ip': self.registry_host, 'registry_port': None}, prefix+'_docker', 'config')
            #dummy data
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
            self._stop_provide_data('registry_ceph', 'config')
            self._stop_provide_data('registry_ceph', 'id')
            self._stop_provide_data('registry_ceph', 'rdb')
        def cleanup_master():
            self._stop_provide_data('master_docker', 'config')
            self._stop_provide_data('master_mariadb', 'config')
            self._stop_provide_data('master_mariadb', 'command')
            self._stop_provide_data('master_mariadb', 'root_pw')
            self._stop_provide_data('master_sysbench_master', 'db_credentials')
            self._stop_provide_data('master_sysbench_master', 'user_credentials')
            self._stop_provide_data('master_sysbench_master', 'my_ip')
        def cleanup_worker(i, mariadb_deployed=False):
            prefix = 'worker%d'%i
            self._stop_provide_data(prefix+'_docker', 'config')
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
            self.change_behavior('master_sysbench_master', 'suspend')
            self.change_behavior('master_mariadb', 'uninstall')
            self.change_behavior('master_mariadb', 'install')
            self.change_behavior('master_sysbench_master', 'install')
            #dummy data
            #self._provide_data(mariadb_config, 'master_mariadb', 'config')
            #self._provide_data(mariadb_command, 'master_mariadb', 'command')
            #self._provide_data('', 'master_mariadb', 'root_pw')
        def reconf_worker(i, mariadb_config='', mariadb_command=''):
            prefix = 'worker%d'%i
            self.change_behavior(prefix+'_mariadb', 'install')
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
        

def time_test(master_host, workers_hosts, registry_host, registry_ceph_mon_host, verbosity : int = 0, printing : bool = False, print_time : bool = False) -> float:
    
    if printing: Printer.st_tprint("Main: creating the assembly")
    deploy_start_time : float = time.perf_counter()
    gass = GaleraAssembly(master_host, workers_hosts, registry_host, registry_ceph_mon_host)
    gass.set_verbosity(verbosity)
    gass.set_print_time(print_time)
    gass.set_use_gantt_chart(True)
    
    if printing: Printer.st_tprint("Main: deploying the assembly")
    gass.deploy_mariadb()
    deploy_end_time : float = time.perf_counter()
    #gass.deploy_mariadb_cleanup()
    
    if printing: Printer.st_tprint("Main: waiting before reconfiguration")
    time.sleep(5)
    
    if printing: Printer.st_tprint("Main: reconfiguring to Galera")
    reconf_start_time : float = time.perf_counter()
    gass.mariadb_to_galera()
    reconf_end_time : float = time.perf_counter()
    
    total_deploy_time = deploy_end_time - deploy_start_time
    total_reconf_time = reconf_end_time - reconf_start_time
    total_time = total_deploy_time+total_reconf_time
    if printing: Printer.st_tprint("Total time in seconds: %f (deploy: %f, reconf: %f)"%(total_time, total_deploy_time, total_reconf_time))
    
    gass.terminate(debug=True)
    gc : GanttChart = gass.get_gantt_chart()
    gc.export_gnuplot("results.gpl")
    return total_time
    

def load_config(conf_file_location):
    from json import load
    with open(conf_file_location, "r") as file:
        conf = load(file)
    return conf


if __name__ == '__main__':
    config = load_config("madpp_config.json")
    master_host = config['master_host']
    workers_hosts = config['workers_hosts']
    registry_host = config['registry_host']
    ceph_mon_host = config['ceph_mon_host']
    time_test(
        master_host, workers_hosts, registry_host, ceph_mon_host,
        verbosity = 1,
        printing = True,
        print_time = True
    )
