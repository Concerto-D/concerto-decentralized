import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult


class PipLibs(Component):
    
    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/piplibs.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'uninstalled_python',
            'installed'
        ]

        self.transitions = {
            'use_python': ('uninstalled', 'uninstalled_python', 'install', 0, empty_transition),
            'install': ('uninstalled_python', 'installed', 'install', 0, self.install)
        }
        
        self.groups = {
            'using_apt_python': ['uninstalled_python', 'installed']
        }

        self.dependencies = {
            'apt_python': (DepType.USE, ['using_apt_python']),
            'pip_libs': (DepType.PROVIDE, ['installed']),
        }
        
        self.initial_place = 'uninstalled'
        

    def install(self):
        #time.sleep(24)
        result = call_ansible_on_host(self.host, self.playbook, "piplibs-0", extra_vars={"enos_action":"deploy"})
        self.print_color("Installed pip libraries (code %d) with command: %s" % (result.return_code, result.command))

