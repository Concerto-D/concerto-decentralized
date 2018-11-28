import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult

class Docker(Component):
    
    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/scaffolding.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'run_mounted',
            'repo_key',
            'repo',
            'installed',
            'config_changed'
        ]
        
        self.groups = {
            'using_apt_utils': ['run_mounted', 'repo_key', 'repo', 'installed']
        }

        self.transitions = {
            'use_apt_utils': ('uninstalled', 'run_mounted', 'install', 0, self.mount_run),
            'to_repo_key': ('run_mounted', 'repo_key', 'install', 0, self.to_repo_key),
            'to_repo': ('repo_key', 'repo', 'install', 0, self.to_repo),
            'to_installed': ('repo', 'installed', 'install', 0, self.to_installed),
            'change_config': ('installed', 'config_changed', 'change_config', 0, self.change_config),
            'restart': ('config_changed', 'installed', 'change_config', 0, self.restart)
        }

        self.dependencies = {
            'config': (DepType.DATA_USE, ['change_config']),
            'apt_utils': (DepType.USE, ['using_apt_utils']),
            'docker': (DepType.PROVIDE, ['installed'])
        }
        
        self.initial_place = 'uninstalled'
        
    def mount_run(self):
        result = call_ansible_on_host(self.host, self.playbook, "docker-0", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Mounted /run (code %d) with command: %s" % (result.return_code, result.command))
        
    def to_repo_key(self):
        #time.sleep(3)
        result = call_ansible_on_host(self.host, self.playbook, "docker-1", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Added repository key (code %d) with command: %s" % (result.return_code, result.command))

    def to_repo(self):
        #time.sleep(3.2)
        result = call_ansible_on_host(self.host, self.playbook, "docker-2", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Added repository (code %d) with command: %s" % (result.return_code, result.command))

    def to_installed(self):
        #time.sleep(24)
        result = call_ansible_on_host(self.host, self.playbook, "docker-3", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Installed Docker (code %d) with command: %s" % (result.return_code, result.command))
    
    #TODO stop cheating
    def change_config(self):
        #time.sleep(3)
        self.print_color("Changing config to:\n%s"%self.read('config'))
        result = call_ansible_on_host(self.host, self.playbook, "docker-4", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Changed config (code %d) with command: %s" % (result.return_code, result.command))
        
    def restart(self):
        #time.sleep(3) /+/
        result = call_ansible_on_host(self.host, self.playbook, "docker-5", extra_vars={"enos_action":"deploy","monitor":"false"})
        self.print_color("Restarted (code %d) with command: %s" % (result.return_code, result.command))

