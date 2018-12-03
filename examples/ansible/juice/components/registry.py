import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult


class Registry(Component):
    
    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/registry.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'uninstalled_ceph',
            'ceph_c',
            'ceph_m',
            'r_started',
            'r_ready'
        ]
        
        self.groups = {
            'using_ceph': ['uninstalled_ceph', 'ceph_c', 'ceph_m', 'r_started', 'r_ready']
        }

        self.transitions = {
            'use_ceph': ('uninstalled', 'uninstalled_ceph', 'install', 0, empty_transition),
            'to_ceph_c': ('uninstalled_ceph', 'ceph_c', 'install', 0, self.to_ceph_c),
            'to_ceph_m': ('ceph_c', 'ceph_m', 'install', 0, self.to_ceph_m),
            'start_r': ('ceph_m', 'r_started', 'install', 0, self.start_r),
            'to_ready': ('r_started', 'r_ready', 'install', 0, self.to_ready)
        }

        self.dependencies = {
            'docker': (DepType.USE, ['start_r']),
            'python_full': (DepType.USE, ['start_r']),
            'ceph': (DepType.USE, ['using_ceph']),
            'registry': (DepType.PROVIDE, ['r_ready'])
        }
        
        self.initial_place = 'uninstalled'
        
    def to_ceph_c(self):
        time.sleep(0.8)

    def to_ceph_m(self):
        time.sleep(1.2)

    def start_r(self):
        #time.sleep(6.7)
        result = call_ansible_on_host(self.host, self.playbook, "registry-0", extra_vars={"enos_action":"deploy","monitor":"false", "registry_type":"internal"})
        self.print_color("Installed Python (code %d) with command: %s" % (result.return_code, result.command))

    def to_ready(self):
        #time.sleep(3)
        result = call_ansible_on_host(self.host, self.playbook, "registry-1", extra_vars={"enos_action":"deploy","monitor":"false", "registry_type":"internal"})
        self.print_color("Installed Python (code %d) with command: %s" % (result.return_code, result.command))

