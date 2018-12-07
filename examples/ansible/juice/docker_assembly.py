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


class DockerAssembly(Assembly):
    
    def __init__(self, host):
        self.host = host
        Assembly.__init__(self)
        
        # Registry
        self.docker_component = Docker(self.host)
        self.add_component('docker', self.docker_component)
        self.apt_utils_component = AptUtils(self.host)
        self.add_component('apt_utils', self.apt_utils_component)
        self.connect('docker', 'apt_utils',
                     'apt_utils', 'apt_utils')
    
    def _provide_data_custom(self, provider_name, data, component_name, input_port):
        dp = DataProvider(data)
        dp.force_hide_from_gantt_chart()
        dp.force_vebosity(-1)
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
        j2.force_vebosity(-1)
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
                
        
    
    def deploy(self):
        self.print("### DEPLOYING ####")
        self.change_behavior('apt_utils', 'install')
        self.change_behavior('docker', 'install')
        self._provide_jinja2('templates/docker.conf.j2', {'registry_ip': self.registry_host, 'registry_port': Registry.REGISTRY_PORT}, 'docker', 'config')
        self.change_behavior('docker', 'change_config')
        self.wait('docker')
        self.wait('apt_utils')
        self.synchronize()
    
    
    def deploy_cleanup(self):
        self._provide_jinja2('docker', 'install')
        
        

def time_test(master_host, verbosity : int = 0, printing : bool = False, print_time : bool = False) -> float:
    
    if printing: Printer.st_tprint("Main: creating the assembly")
    deploy_start_time : float = time.perf_counter()
    dass = DockerAssembly(master_host)
    dass.set_verbosity(verbosity)
    dass.set_print_time(print_time)
    dass.set_use_gantt_chart(True)
    
    if printing: Printer.st_tprint("Main: deploying the assembly")
    dass.deploy()
    deploy_end_time : float = time.perf_counter()
    #dass.deploy_mariadb_cleanup()
    
    total_deploy_time = deploy_end_time - deploy_start_time
    if printing: Printer.st_tprint("Total deploy time in seconds: %f"%(total_deploy_time))
    
    dass.terminate(debug=True)
    gc : GanttChart = dass.get_gantt_chart()
    gc.export_gnuplot("results.gpl")
    return total_deploy_time
    

def load_config(conf_file_location):
    from json import load
    with open(conf_file_location, "r") as file:
        conf = load(file)
    return conf


if __name__ == '__main__':
    config = load_config("docker_config.json")
    master_host = config['master_host']
    time_test(
        master_host,
        verbosity = 1,
        printing = True,
        print_time = True
    )
