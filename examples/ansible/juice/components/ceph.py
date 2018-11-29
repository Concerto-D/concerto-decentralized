import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult

class Ceph(Component):
    
    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/registry.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'installed',
            'configured',
            'kernel_module_added',
            'rdb_map_added',
            'fact_set',
            'registry_directory_created',
            'running',
            #'rdb_map_pl'
        ]

        self.transitions = {
            'install': ('uninstalled', 'installed', 'install', 0, self.install),
            'configure_conf': ('installed', 'configured', 'install', 0, self.configure_conf),
            'configure_keyring': ('installed', 'configured', 'install', 0, self.configure_keyring),
            'add_rdb_kernel_module': ('configured', 'kernel_module_added', 'install', 0, self.add_rdb_kernel_module),
            'add_rdb_map': ('kernel_module_added', 'rdb_map_added', 'install', 0, self.add_rdb_map),
            'set_fact': ('rdb_map_added', 'fact_set', 'install', 0, self.set_fact),
            'create_registry_directory': ('fact_set', 'registry_directory_created', 'install', 0, self.create_registry_directory),
            'mount_registry': ('registry_directory_created', 'running', 'install', 0, self.mount_registry),
            #'add_rdb_mapping': ('running', 'running', 'add_rdb_mapping', 0, self.add_rdb_mapping),
            #'get_rdb_mapping': ('running', 'rdb_map_pl', 'get_rdb_mapping', 0, self.get_rdb_mapping),
            #'get_rdb_mapping2': ('rdb_map_pl', 'running', 'get_rdb_mapping', 0, empty_transition)
        }

        self.dependencies = {
            'config': (DepType.DATA_USE, ['configure_conf']),
            'keyring': (DepType.DATA_USE, ['configure_keyring']),
            'rdb': (DepType.DATA_USE, ['add_rdb_map', 'mount_registry']),
            'id': (DepType.DATA_USE, ['add_rdb_map', 'set_fact']),
            #'rdb_map': (DepType.DATA_PROVIDE, ['rdb_map_pl']),
            'ceph': (DepType.PROVIDE, ['running'])
        }
        
        self.initial_place = 'uninstalled'
        

    def install(self):
        #time.sleep(20.6)
        result = call_ansible_on_host(self.host, self.playbook, "ceph-0", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Installed Ceph (code %d) with command: %s" % (result.return_code, result.command))

    def configure_conf(self):
        self.print_color("Using config:\n%s"%self.read('config'))
        #time.sleep(1.2)
        result = call_ansible_on_host(self.host, self.playbook, "ceph-1", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Copied configuration (code %d) with command: %s" % (result.return_code, result.command))

    def configure_keyring(self):
        #time.sleep(1.1)
        result = call_ansible_on_host(self.host, self.playbook, "ceph-2", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Copied keyring (code %d) with command: %s" % (result.return_code, result.command))
        
    def add_rdb_kernel_module(self):
        result = call_ansible_on_host(self.host, self.playbook, "ceph-3", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Added rdb kernel module (code %d) with command: %s" % (result.return_code, result.command))
        
    def add_rdb_map(self):
        result = call_ansible_on_host(self.host, self.playbook, "ceph-4", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Added rdb map (code %d) with command: %s" % (result.return_code, result.command))
        
    def set_fact(self):
        result = call_ansible_on_host(self.host, self.playbook, "ceph-5", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Fact set (code %d) with command: %s" % (result.return_code, result.command))
        
    def create_registry_directory(self):
        result = call_ansible_on_host(self.host, self.playbook, "ceph-6", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Created registry directory (code %d) with command: %s" % (result.return_code, result.command))
    
    def mount_registry(self):
        #time.sleep(0.8)
        result = call_ansible_on_host(self.host, self.playbook, "ceph-7", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Copied keyring (code %d) with command: %s" % (result.return_code, result.command))

    #def add_rdb_mapping(self):
        #self.print_color("Adding rdb mapping (id: %s): %s"%(self.read('id'),self.read('rdb')))
        ##time.sleep(0.8)

    #def get_rdb_mapping(self):
        #rdb_map = "PLACEHOLDER"
        #self.print_color("Writing rdb map (id: %s) to output port: %s"%(self.read('id'),rdb_map))
        #self.write("rdb_map",rdb_map)
        ##time.sleep(0.7)

