import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult


class MariaDBWorker(Component):

    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/mariadb.yml"
        self.pulled = False
        self.galera = False
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'ready_to_pull',
            'mounted',
            'directories_created',
            'configured_pulled',
            'started',
            'ready'
        ]
        
        self.groups = {
            'using_docker': ['ready_to_pull','configured_pulled','started','ready']
        }

        self.transitions = {
            'mount': ('uninstalled', 'mounted', 'install', 0, self.mount),
            'create_directories': ('mounted', 'directories_created', 'install', 0, self.create_directories),
            'send_config': ('directories_created', 'configured_pulled', 'install', 0, self.send_config),
            'use_docker': ('uninstalled', 'ready_to_pull', 'install', 0, empty_transition),
            'pull': ('ready_to_pull', 'configured_pulled', 'install', 0, self.pull),
            'start': ('configured_pulled', 'started', 'install', 0, self.start),
            'go_ready': ('started', 'ready', 'install', 0, self.go_ready),
            'change_config': ('ready', 'ready', 'change_config', 0, self.change_config),
            'stop': ('ready', 'mounted', 'stop', 0, self.stop),
            'stop_uninstall': ('ready', 'mounted', 'uninstall', 0, self.stop),
            'uninstall': ('mounted', 'uninstalled', 'uninstall', 0, self.uninstall)
        }

        self.dependencies = {
            'config': (DepType.DATA_USE, ['send_config', 'change_config']),
            'pip_libs': (DepType.USE, ['using_docker']),
            'docker': (DepType.USE, ['using_docker']),
            'registry': (DepType.USE, ['pull']),
            'master_mariadb': (DepType.USE, ['start']),
            'mariadb': (DepType.PROVIDE, ['ready'])
        }
        
        self.initial_place = 'uninstalled'
        
    def mount(self):
        self.print_color("Mounting")
        #time.sleep(0.8)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-0", extra_vars={"enos_action":"deploy","db":"mariadb"})
        self.print_color("Mounted database dir (code %d) with command: %s" % (result.return_code, result.command))
        
    def create_directories(self):
        self.print_color("Creating directories")
        #time.sleep(1.3)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-1", extra_vars={"enos_action":"deploy","db":"mariadb"})
        self.print_color("Created directories (code %d) with command: %s" % (result.return_code, result.command))
        
    def send_config(self):
        self.print_color("Seonding config")
        #time.sleep(1.3)
        config = self.read("config")
        if config is "":
            self.print_color("Empty config, skipping send_config")
        else:
            self.galera = True
            self.print_color("Changing config to:\n%s"%config)
            result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-2-galera", extra_vars={"enos_action":"deploy","db":"mariadb","mariadb_config": config})
            self.print_color("Sent config (code %d) with command: %s" % (result.return_code, result.command))
        
    def pull(self):
        self.print_color("Pulling image")
        if not self.pulled:
            self.print_color("Pulling image")
            #time.sleep(6.5)
            result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-3", extra_vars={"enos_action":"deploy","db":"mariadb"})
            self.print_color("Pulled image (code %d) with command: %s" % (result.return_code, result.command))
            self.pulled = True

    def start(self):
        self.print_color("Starting container")
        #time.sleep(1.4)
        if self.galera:
            result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-4-other", extra_vars={"enos_action":"deploy","db":"mariadb", "db_host":self.host["ip"]})
        else:
            result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-4-only", extra_vars={"enos_action":"deploy","db":"mariadb", "db_host":self.host["ip"]})
        self.print_color("Started container (code %d) with command: %s" % (result.return_code, result.command))

    def go_ready(self):
        self.print_color("going ready")
        #time.sleep(5.8)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-5", extra_vars={"enos_action":"deploy", "db":"mariadb", "db_host":self.host["ip"]})
        self.print_color("Database ready (code %d) with command: %s" % (result.return_code, result.command))

    def change_config(self):
        self.print_color("Changing config")
        time.sleep(1) # TODO: check

    def stop(self):
        time.sleep(1.4)

    def uninstall(self):
        time.sleep(1.6)

    def clear_image(self):
        time.sleep(1) # TODO: check

