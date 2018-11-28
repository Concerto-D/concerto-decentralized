import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult


class MariaDB(Component):

    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/scaffolding.yml"
        self.pulled = False
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'mounted',
            'configured_pulled',
            'started',
            'ready'
        ]
        
        self.groups = {
        }

        self.transitions = {
            'mount': ('uninstalled', 'mounted', 'install', 0, self.mount),
            'config1': ('mounted', 'configured_pulled', 'install', 0, self.config1),
            'config2': ('mounted', 'configured_pulled', 'install', 0, self.config2),
            'pull': ('uninstalled', 'configured_pulled', 'install', 0, self.pull),
            'start': ('configured_pulled', 'started', 'install', 0, self.start),
            'go_ready': ('started', 'ready', 'install', 0, self.go_ready),
            'change_config': ('ready', 'ready', 'change_config', 0, self.change_config),
            'stop': ('ready', 'mounted', 'stop', 0, self.stop),
            'stop_uninstall': ('ready', 'mounted', 'uninstall', 0, self.stop),
            'uninstall': ('mounted', 'uninstalled', 'uninstall', 0, self.uninstall)
        }

        self.dependencies = {
            'config': (DepType.DATA_USE, ['config1', 'change_config']),
            'command': (DepType.DATA_USE, ['start']),
            'root_pw': (DepType.DATA_USE, ['start']),
            'python_full': (DepType.USE, ['start']),
            'docker': (DepType.USE, ['start']),
            'registry': (DepType.USE, ['start']),
            'mariadb': (DepType.PROVIDE, ['ready'])
        }
        
        self.initial_place = 'uninstalled'
        
    def mount(self):
        #time.sleep(0.8)
        result = call_ansible_on_host(self.host, self.playbook, "mariadb-0", extra_vars={"enos_action":"deploy","monitor":"false","db":"mariadb"})
        self.print_color("Mounted database dir (code %d) with command: %s" % (result.return_code, result.command))
        
    def config1(self):
        time.sleep(1.3)
        
    def config2(self):
        time.sleep(1.3)
        
    def pull(self):
        if not self.pulled:
            self.print_color("Pulling image")
            #time.sleep(6.5)
            result = call_ansible_on_host(self.host, self.playbook, "mariadb-3", extra_vars={"enos_action":"deploy","monitor":"false","db":"mariadb"})
            self.print_color("Pulled image (code %d) with command: %s" % (result.return_code, result.command))
            self.pulled = True

    def start(self):
        #time.sleep(1.4)
        result = call_ansible_on_host(self.host, self.playbook, "mariadb-4", extra_vars={"enos_action":"deploy","monitor":"false","db":"mariadb"})
        self.print_color("Started container (code %d) with command: %s" % (result.return_code, result.command))

    def go_ready(self):
        #time.sleep(5.8)
        result = call_ansible_on_host(self.host, self.playbook, "mariadb-5", extra_vars={"enos_action":"deploy","monitor":"false","db":"mariadb"})
        self.print_color("Database ready (code %d) with command: %s" % (result.return_code, result.command))

    def change_config(self):
        time.sleep(1) # TODO: check

    def stop(self):
        time.sleep(1.4)

    def uninstall(self):
        time.sleep(1.6)

    def clear_image(self):
        time.sleep(1) # TODO: check

