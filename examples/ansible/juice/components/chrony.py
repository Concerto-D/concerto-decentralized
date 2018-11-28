import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult


class Chrony(Component):
    
    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/scaffolding.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'installed',
            'config_changed'
        ]

        self.transitions = {
            'install': ('uninstalled', 'installed', 'install', 0, self.install),
            'change_config': ('installed', 'config_changed', 'change_config', 0, self.change_config),
            'restart': ('config_changed', 'installed', 'change_config', 0, self.restart)
        }

        self.dependencies = {
            'chrony': (DepType.PROVIDE, ['installed']),
            'config': (DepType.DATA_USE, ['change_config'])
        }
        
        self.initial_place = 'uninstalled'
        

    def install(self):
        #time.sleep(4.5)
        result = call_ansible_on_host(self.host, self.playbook, "chrony-0", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Installed Chrony (code %d) with command: %s" % (result.return_code, result.command))

    def change_config(self):
        self.print_color("Changing config to:\n%s"%self.read('config'))
        #time.sleep(2)
        result = call_ansible_on_host(self.host, self.playbook, "chrony-1", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Changed config (code %d) with command: %s" % (result.return_code, result.command))

    def restart(self):
        #time.sleep(2) !!
        result = call_ansible_on_host(self.host, self.playbook, "chrony-2", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Restarted (code %d) with command: %s" % (result.return_code, result.command))

