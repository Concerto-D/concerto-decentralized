import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult


class Registry(Component):
    
    REGISTRY_PORT = 4000
    
    def __init__(self, host, use_ceph : bool):
        self.host = host
        self.use_ceph = use_ceph
        self.playbook = "ansible/registry.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'uninstalled_ceph',
            'r_started',
            'r_ready'
        ]
        
        self.groups = {
            'using_ceph': ['uninstalled_ceph', 'r_started', 'r_ready']
        }

        self.transitions = {
            'use_ceph': ('uninstalled', 'uninstalled_ceph', 'install', 0, empty_transition),
            'start_r': ('uninstalled_ceph', 'r_started', 'install', 0, self.start_r),
            'to_ready': ('r_started', 'r_ready', 'install', 0, self.to_ready)
        }

        self.dependencies = {
            'docker': (DepType.USE, ['start_r']),
            'pip_libs': (DepType.USE, ['start_r']),
            'registry': (DepType.PROVIDE, ['r_ready'])
        }
        if self.use_ceph:
            self.dependencies['ceph'] = (DepType.USE, ['using_ceph'])
        
        self.initial_place = 'uninstalled'
        
    # TODO: REMOVE
    def to_ceph_c(self):
        time.sleep(0.8)

    # TODO: REMOVE
    def to_ceph_m(self):
        time.sleep(1.2)

    def start_r(self):
        #time.sleep(6.7)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "registry-0", extra_vars={"enos_action":"deploy", "registry_ip": self.host["ip"], "registry_port":self.REGISTRY_PORT})
        self.print_color("Started registry (code %d) with command: %s" % (result.return_code, result.command))

    def to_ready(self):
        #time.sleep(3)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "registry-1", extra_vars={"enos_action":"deploy", "registry_ip": self.host["ip"], "registry_port":self.REGISTRY_PORT})
        self.print_color("Made registry ready (code %d) with command: %s" % (result.return_code, result.command))

