import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult


class Python(Component):
    
    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/scaffolding.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'vanilla',
            'full'
        ]

        self.transitions = {
            'install_python': ('uninstalled', 'vanilla', 'install', 0, self.install_python),
            'install_libs': ('vanilla', 'full', 'install', 0, self.install_libs)
        }
        
        self.groups = {
            'providing_python': ['vanilla', 'full']
        }

        self.dependencies = {
            'python': (DepType.PROVIDE, ['providing_python']),
            'python_full': (DepType.PROVIDE, ['full'])
        }
        
        self.initial_place = 'uninstalled'
        

    def install_python(self):
        #time.sleep(24)
        result = call_ansible_on_host(self.host, self.playbook, "python-0", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Installed Python (code %d) with command: %s" % (result.return_code, result.command))

    def install_libs(self):
        #time.sleep(16)
        result = call_ansible_on_host(self.host, self.playbook, "python-1", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Installed Python libs (code %d) with command: %s" % (result.return_code, result.command))

