import time

from concerto.all import *
from concerto.utility import *
from concerto.plugins.ansible import call_ansible_on_host, AnsibleCallResult


class Sysbench(Component):
    
    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/sysbench.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'installed'
        ]

        self.transitions = {
            'install': ('uninstalled', 'installed', 'install', 0, self.install),
        }

        self.dependencies = {
            'sysbench_dir': (DepType.PROVIDE, ['installed'])
        }
        
        self.initial_place = 'uninstalled'
        

    def install(self):
        #time.sleep(0.7)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "sysbench-0", extra_vars={"enos_action": "deploy"})
        self.print_color("Sysbench directory created (code %d) with command: %s" % (result.return_code, result.command))

