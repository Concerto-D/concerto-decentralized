#!/usr/bin/python3

import time, datetime

from concerto.all import *
from concerto.utility import Printer
from concerto.components.data_provider import DataProvider
from concerto.components.jinja2 import Jinja2, Jinja2Static
from concerto.gantt_chart import GanttChart

from components.apt_utils import AptUtils
from components.ceph import Ceph
from components.docker import Docker
from components.mariadb import MariaDB
from components.mariadb_worker import MariaDBWorker
from components.pip_libs import PipLibs
from components.registry import Registry
from components.sysbench import Sysbench
from components.sysbench_master import SysbenchMaster


class GaleraAssembly(Assembly):
    class ComponentSet():
        def __init__(self):
            self.apt_utils = None
            self.pip_libs = None
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
            ass.pip_libs = PipLibs(host)
            ass.docker = Docker(host)
            return ass
            
        @staticmethod
        def build_registry_set(host, use_ceph : bool):
            ass = GaleraAssembly.ComponentSet._build_common_set(host)
            ass.apt_utils = AptUtils(host, use_ceph)
            ass.registry = Registry(host, use_ceph)
            if use_ceph:
                ass.ceph = Ceph(host)
            return ass
            
        @staticmethod
        def _build_db_set(host):
            ass = GaleraAssembly.ComponentSet._build_common_set(host)
            ass.apt_utils = AptUtils(host, False)
            ass.sysbench = Sysbench(host)
            return ass
            
        @staticmethod
        def build_master_set(host):
            ass = GaleraAssembly.ComponentSet._build_db_set(host)
            ass.mariadb = MariaDB(host)
            ass.sysbench_master = SysbenchMaster(host)
            return ass
            
        @staticmethod
        def build_worker_set(host):
            ass = GaleraAssembly.ComponentSet._build_db_set(host)
            ass.mariadb = MariaDBWorker(host)
            return ass
    
    def __init__(self, master_host, workers_hosts, registry_host, registry_ceph_config):
        if len(workers_hosts) < 2:
            raise Exception("GaleraAssembly: error, the number of workers must be at least 2 for Galera to work")
        self.master_host = master_host
        self.workers_hosts = workers_hosts
        self.registry_host = registry_host
        self.registry_ceph_config = registry_ceph_config
        Assembly.__init__(self)
        
        # Registry
        self.registry_set = self.ComponentSet.build_registry_set(self.registry_host, use_ceph=self.registry_ceph_config['use'])
        self.add_component('registry_apt_utils', self.registry_set.apt_utils)
        self.add_component('registry_pip_libs', self.registry_set.pip_libs)
        self.add_component('registry_docker', self.registry_set.docker)
        self.add_component('registry_registry', self.registry_set.registry)
        if (self.registry_ceph_config['use']):
            self.add_component('registry_ceph', self.registry_set.ceph)
            
        self.connect('registry_apt_utils', 'apt_python',
                     'registry_pip_libs', 'apt_python')
        self.connect('registry_apt_utils', 'apt_docker',
                     'registry_docker', 'apt_docker')
        self.connect('registry_pip_libs', 'pip_libs',
                     'registry_registry', 'pip_libs')
        self.connect('registry_docker','docker',
                     'registry_registry','docker')
        if (self.registry_ceph_config['use']):
            self.connect('registry_apt_utils', 'apt_ceph',
                        'registry_ceph', 'apt_ceph')
            self.connect('registry_ceph', 'ceph',
                        'registry_registry', 'ceph')
        
        # DB Master
        self.master_set = self.ComponentSet.build_master_set(self.master_host)
        self.add_component('master_apt_utils', self.master_set.apt_utils)
        self.add_component('master_pip_libs', self.master_set.pip_libs)
        self.add_component('master_docker', self.master_set.docker)
        self.add_component('master_mariadb', self.master_set.mariadb)
        self.add_component('master_sysbench', self.master_set.sysbench)
        self.add_component('master_sysbench_master', self.master_set.sysbench_master)
        self.connect('master_apt_utils', 'apt_python',
                     'master_pip_libs', 'apt_python')
        self.connect('master_apt_utils', 'apt_docker',
                     'master_docker', 'apt_docker')
        self.connect('master_pip_libs', 'pip_libs',
                     'master_mariadb', 'pip_libs')
        self.connect('master_mariadb', 'mariadb',
                     'master_sysbench_master', 'mysql')
        self.connect('master_docker','docker',
                     'master_mariadb','docker')
        self.connect('registry_registry', 'registry',
                     'master_mariadb', 'registry')
        
        # DB Workers
        self.worker_sets = []
        for i in range(len(self.workers_hosts)):
            prefix = 'worker%d'%i
            self.worker_sets.append(self.ComponentSet.build_worker_set(self.workers_hosts[i]))
            current_worker_set = self.worker_sets[i]
            self.add_component(prefix+'_apt_utils', current_worker_set.apt_utils)
            self.add_component(prefix+'_pip_libs', current_worker_set.pip_libs)
            self.add_component(prefix+'_docker', current_worker_set.docker)
            self.add_component(prefix+'_mariadb', current_worker_set.mariadb)
            self.add_component(prefix+'_sysbench', current_worker_set.sysbench)
            self.connect(prefix+'_apt_utils', 'apt_python',
                         prefix+'_pip_libs', 'apt_python')
            self.connect(prefix+'_pip_libs', 'pip_libs',
                         prefix+'_mariadb', 'pip_libs')
            self.connect(prefix+'_apt_utils', 'apt_docker',
                         prefix+'_docker', 'apt_docker')
            self.connect(prefix+'_docker','docker',
                         prefix+'_mariadb','docker')
            self.connect('registry_registry', 'registry',
                         prefix+'_mariadb', 'registry')
            self.connect('master_mariadb', 'mariadb',
                         prefix+'_mariadb', 'master_mariadb')
    
    def _provide_data_custom(self, provider_name, data, component_name, input_port):
        dp = DataProvider(data)
        dp.force_hide_from_gantt_chart()
        dp.force_vebosity(-1)
        self.add_component(provider_name, dp)
        self.connect(provider_name, 'data',
                     component_name, input_port)
        
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
        j2.force_vebosity(-1)
        provider_name = "%s_%s"%(component_name, input_port)
        self.add_component(provider_name, j2)
        self.connect(provider_name, 'jinja2_result',
                     component_name, input_port)
        self.change_behavior(provider_name, 'generate')
    
    def _provide_jinja2_static(self, template_file_location, parameters, component_name, input_port):
        with open(template_file_location, 'r') as template_file:
            template_text = template_file.read()
        j2 = Jinja2Static(template_text, parameters)
        j2.force_hide_from_gantt_chart()
        j2.force_vebosity(-1)
        provider_name = "%s_%s"%(component_name, input_port)
        self.add_component(provider_name, j2)
        self.connect(provider_name, 'jinja2_result',
                     component_name, input_port)
        
    def _stop_provide_jinja2(self, component_name, input_port):
        provider_name = "%s_%s"%(component_name, input_port)
        self.disconnect(provider_name, 'jinja2_result',
                        component_name, input_port)
        self.del_component(provider_name)
                
        
    
    def _deploy(self, galera=False):
        def deploy_registry():
            self.change_behavior('registry_apt_utils', 'install')
            self.change_behavior('registry_pip_libs', 'install')
            self.change_behavior('registry_docker', 'install')
            self.change_behavior('registry_registry', 'install')
            self._provide_jinja2_static('templates/docker.conf.j2', {'registry_ip': self.registry_host["ip"], 'registry_port': Registry.REGISTRY_PORT}, 'registry_docker', 'config')
            if (self.registry_ceph_config['use']):
                self.change_behavior('registry_ceph', 'install')
                self._provide_jinja2_static('templates/ceph.conf.j2', {'registry_ceph_mon_host': self.registry_ceph_config['mon_host']}, 'registry_ceph', 'config')
                self._provide_data(self.registry_ceph_config['keyring_path'], 'registry_ceph', 'keyring_path')
                self._provide_data(self.registry_ceph_config['rbd'], 'registry_ceph', 'rbd')
                self._provide_data(self.registry_ceph_config['id'], 'registry_ceph', 'id')
        def deploy_master(galera=False):
            self.change_behavior('master_apt_utils', 'install')
            self.change_behavior('master_pip_libs', 'install')
            self.change_behavior('master_docker', 'install')
            self.change_behavior('master_mariadb', 'install')
            self.change_behavior('master_mariadb', 'run')
            self.change_behavior('master_sysbench', 'install')
            self.change_behavior('master_sysbench_master', 'install')
            self._provide_jinja2_static('templates/docker.conf.j2', {'registry_ip': self.registry_host["ip"], 'registry_port': Registry.REGISTRY_PORT}, 'master_docker', 'config')
            if galera:
                self._provide_jinja2_static('templates/mariadb-galera.conf.j2', {'db_ips': list([h["ip"] for h in [self.master_host]+self.workers_hosts])}, 'master_mariadb', 'config')
            else:
                self._provide_data('', 'master_mariadb', 'config')
        def deploy_worker(i, deploy_galera=False):
            prefix = 'worker%d'%i
            self.change_behavior(prefix+'_apt_utils', 'install')
            self.change_behavior(prefix+'_pip_libs', 'install')
            self.change_behavior(prefix+'_docker', 'install')
            if deploy_galera:
                self.change_behavior(prefix+'_mariadb', 'install')
            self.change_behavior(prefix+'_sysbench', 'install')
            self._provide_jinja2_static('templates/docker.conf.j2', {'registry_ip': self.registry_host["ip"], 'registry_port': Registry.REGISTRY_PORT}, prefix+'_docker', 'config')
            #dummy data
            if deploy_galera:
                self._provide_jinja2_static('templates/mariadb-galera.conf.j2', {'db_ips': list([h["ip"] for h in [self.master_host]+self.workers_hosts])}, prefix+'_mariadb', 'config')
            
        
        self.print("### DEPLOYING ####")
        Printer.st_err_tprint("DEBUG: deploying registry")
        deploy_registry()
        Printer.st_err_tprint("DEBUG: deploying master")
        deploy_master(galera=galera)
        Printer.st_err_tprint("DEBUG: deploying workers")
        for i in range(len(self.workers_hosts)):
            deploy_worker(i, deploy_galera=galera)
            
    
    
    def _deploy_cleanup(self, galera=False):
        def cleanup_registry():
            self._stop_provide_jinja2('registry_docker', 'config')
            if (self.registry_ceph_config['use']):
                self._stop_provide_jinja2('registry_ceph', 'config')
                self._stop_provide_data('registry_ceph', 'keyring_path')
                self._stop_provide_data('registry_ceph', 'id')
                self._stop_provide_data('registry_ceph', 'rdb')
        def cleanup_master():
            self._stop_provide_jinja2('master_docker', 'config')
            if galera:
                self._stop_provide_jinja2('master_mariadb', 'config')
            else:
                self._stop_provide_data('master_mariadb', 'config')
        def cleanup_worker(i, mariadb_deployed=False):
            prefix = 'worker%d'%i
            self._stop_provide_jinja2(prefix+'_docker', 'config')
            if mariadb_deployed:
                self._stop_provide_jinja2(prefix+'_mariadb', 'config')
                
    
        cleanup_registry()
        cleanup_master()
        for i in range(len(self.workers_hosts)):
            if galera:
                cleanup_worker(i, True)
            else:
                cleanup_worker(i, False)
        
        
    def deploy_mariadb(self):
        self._deploy(False)
        #time.sleep(120)
        #Printer.st_err_tprint("After 120 seconds:\n" + self.get_debug_info())
        self.wait_all()
        self.synchronize()
        Printer.st_err_tprint("Deploy MadiaDB finished")
        
    def deploy_mariadb_cleanup(self):
        self._deploy_cleanup(False)
        self.synchronize()
        
    def deploy_galera(self):
        self._deploy(True)
        #time.sleep(120)
        #Printer.st_err_tprint("After 120 seconds:\n" + self.get_debug_info())
        self.wait_all()
        self.synchronize()
        Printer.st_err_tprint("Deploy Galera finished")
        
    def deploy_galera_cleanup(self):
        self._deploy_cleanup(True)
        self.synchronize()
        
    def mariadb_to_galera(self):
        def reconf_master(mariadb_config=''):
            self.change_behavior('master_sysbench_master', 'suspend')
            self.change_behavior('master_mariadb', 'uninstall_backup')
            self._provide_jinja2_static('templates/mariadb-galera.conf.j2', {'db_ips': list([h["ip"] for h in [self.master_host]+self.workers_hosts])}, 'master_mariadb', 'config')
            self.change_behavior('master_mariadb', 'install')
            self.change_behavior('master_mariadb', 'restore_run')
            self.change_behavior('master_sysbench_master', 'install')
        def reconf_worker(i, mariadb_config=''):
            prefix = 'worker%d'%i
            self._provide_jinja2_static('templates/mariadb-galera.conf.j2', {'db_ips': list([h["ip"] for h in [self.master_host]+self.workers_hosts])}, prefix+'_mariadb', 'config')
            self.change_behavior(prefix+'_mariadb', 'install')
        
        self.print("## RECONFIGURING ##")
        for i in range(len(self.workers_hosts)):
            reconf_worker(i)
        reconf_master()
        for i in range(len(self.workers_hosts)):
            prefix = 'worker%d'%i
            self.wait(prefix+'_mariadb')
        self.synchronize()

    def mariadb_to_galera_cleanup(self):
        def cleanup_master():
            self._stop_provide_jinja2('master_mariadb', 'config')
        def cleanup_worker(i):
            prefix = 'worker%d'%i
            self._stop_provide_jinja2(prefix+'_mariadb', 'config')
                
        cleanup_master()
        for i in range(len(self.workers_hosts)):
            cleanup_worker(i)
        self.synchronize()
        

def time_test(master_host, workers_hosts, registry_host, registry_ceph_mon_host, nb_db_entries, verbosity : int = 0, printing : bool = False, print_time : bool = False) -> float:
    from subprocess import run, CompletedProcess
    from json import dump
    from concerto.plugins.ansible import call_ansible_on_host
    
    if printing: Printer.st_tprint("Main: creating the assembly")
    deploy_start_time : float = time.perf_counter()
    gass = GaleraAssembly(master_host, workers_hosts, registry_host, registry_ceph_mon_host)
    gass.set_verbosity(verbosity)
    gass.set_print_time(print_time)
    gass.set_use_gantt_chart(True)
    
    if printing: Printer.st_tprint("Main: deploying the assembly")
    gass.deploy_mariadb()
    deploy_end_time : float = time.perf_counter()
    if printing: Printer.st_tprint("Main: cleaning up the assembly")
    gass.deploy_mariadb_cleanup()
    
    if nb_db_entries > 0:
        if printing: Printer.st_tprint("Main: sending database content")
        if printing: Printer.st_err_tprint("Main: sending database content")
        command = "cd experiments/db_builder/;python3 generate_db.py %d > ../../data.sql"%nb_db_entries
        completed_process = run(command, shell=True, check=False)
        if completed_process.returncode is not 0:
            raise Exception("Error: Could not generate DB data")
        with open('data.sql') as sql_file:
            sql_data=sql_file.read()
        call_ansible_on_host(master_host["ip"], "ansible/experiment.yml", "send-data-to-db", extra_vars={"data": sql_data})
    else:
        open('data.sql', "a").close() # create an empty file to be sure it is there
        if printing: Printer.st_tprint("Main: not sending database content (0 entries)")
        if printing: Printer.st_err_tprint("Main: not sending database content (0 entries)")
    
    if printing: Printer.st_tprint("Main: waiting 10 seconds before reconfiguring")
    if printing: Printer.st_err_tprint("Main: waiting 10 seconds before reconfiguring")
    time.sleep(10)
    
    if printing: Printer.st_tprint("Main: reconfiguring to Galera")
    reconf_start_time : float = time.perf_counter()
    gass.mariadb_to_galera()
    reconf_end_time : float = time.perf_counter()
    if printing: Printer.st_tprint("Main: cleaning up the assembly")
    gass.mariadb_to_galera_cleanup()
    
    total_deploy_time = deploy_end_time - deploy_start_time
    total_reconf_time = reconf_end_time - reconf_start_time
    total_time = total_deploy_time+total_reconf_time
    if printing: Printer.st_tprint("Total time in seconds: %f (deploy: %f, reconf: %f)"%(total_time, total_deploy_time, total_reconf_time))
    
    gass.terminate()
    gc : GanttChart = gass.get_gantt_chart()
    gc.export_gnuplot("results.gpl")
    gc.export_json("results.json")
    with open("times.json", "w") as results_file:
        dump({"total_time": total_time, "total_deploy_time": total_deploy_time, "total_reconf_time": total_reconf_time}, results_file)
    return total_time, total_deploy_time, total_reconf_time
    

def load_config(conf_file_location):
    from json import load
    with open(conf_file_location, "r") as file:
        conf = load(file)
    return conf


if __name__ == '__main__':
    config = load_config("concerto_config.json")
    master_host = config['master_host']
    workers_hosts = config['workers_hosts']
    registry_host = config['registry_host']
    registry_ceph_config = config['ceph']
    nb_db_entries = config['nb_db_entries']
    time_test(
        master_host, workers_hosts, registry_host, registry_ceph_config, nb_db_entries,
        verbosity = 1,
        printing = True,
        print_time = True
    )
