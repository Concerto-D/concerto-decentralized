import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult

class Docker(Component):
    
    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/docker.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'run_mounted',
            'installed',
            'config_changed'
        ]
        
        self.groups = {
            'using_apt_docker': ['installed', 'config_changed']
        }

        self.transitions = {
            'mount_run': ('uninstalled', 'run_mounted', 'install', 0, self.mount_run),
            'use_apt_docker': ('run_mounted', 'installed', 'install', 0, empty_transition),
            'change_config': ('installed', 'config_changed', 'change_config', 0, self.change_config),
            'restart': ('config_changed', 'installed', 'change_config', 0, self.restart)
        }

        self.dependencies = {
            'config': (DepType.DATA_USE, ['change_config']),
            'apt_docker': (DepType.USE, ['using_apt_docker']),
            'docker': (DepType.PROVIDE, ['installed'])
        }
        
        self.initial_place = 'uninstalled'
        
    def mount_run(self):
        self.print_color("Mouting /run")
        result = call_ansible_on_host(self.host, self.playbook, "docker-0", extra_vars={"enos_action":"deploy"})
        self.print_color("Mounted /run (code %d) with command: %s" % (result.return_code, result.command))
    
    def change_config(self):
        config = self.read('config')
        self.print_color("Changing config to:\n%s"%config)
        #time.sleep(3)
        result = call_ansible_on_host(self.host, self.playbook, "docker-4", extra_vars={
            "enos_action":"deploy",
            "docker_config":config,
        })
        self.print_color("Changed config (code %d) with command: %s" % (result.return_code, result.command))
        
    def restart(self):
        self.print_color("Restarting")
        #time.sleep(3) /+/
        result = call_ansible_on_host(self.host, self.playbook, "docker-5", extra_vars={"enos_action":"deploy"})
        self.print_color("Restarted (code %d) with command: %s" % (result.return_code, result.command))

