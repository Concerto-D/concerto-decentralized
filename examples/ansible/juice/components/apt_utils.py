import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult

class AptUtils(Component):
    
    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/registry.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'installed'
        ]

        self.transitions = {
            'install': ('uninstalled', 'installed', 'install', 0, self.install)
        }

        self.dependencies = {
            'apt_utils': (DepType.PROVIDE, ['installed'])
        }
        
        self.initial_place = 'uninstalled'
        

    def install(self):
        #time.sleep(12.5)
        result = call_ansible_on_host(self.host, self.playbook, "aptutils-0", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Installed apt_utils (code %d) with command: %s" % (result.return_code, result.command))

