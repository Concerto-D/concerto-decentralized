import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult


class MariaDB(Component):

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
            'ready',
            'running',
            'backuped',
            'stopped'
        ]
        
        self.groups = {
            'using_docker': ['ready_to_pull','configured_pulled','started','ready', 'running', 'backuped', 'stopped']
        }

        self.transitions = {
            'mount': ('uninstalled', 'mounted', 'install', 0, self.mount),
            'create_directories': ('mounted', 'directories_created', 'install', 0, self.create_directories),
            'send_config': ('directories_created', 'configured_pulled', 'install', 0, self.send_config),
            'use_docker': ('uninstalled', 'ready_to_pull', 'install', 0, empty_transition),
            'pull': ('ready_to_pull', 'configured_pulled', 'install', 0, self.pull),
            'start': ('configured_pulled', 'started', 'install', 0, self.start),
            'go_ready': ('started', 'ready', 'install', 0, self.go_ready),
            'run': ('ready', 'running', 'run', 0, empty_transition),
            'restore_run': ('ready', 'running', 'restore_run', 0, self.restore_backup),
            
            'uninstallb_backup': ('running', 'backuped', 'uninstall_backup', 0, self.backup),
            'uninstallb_stop': ('backuped', 'stopped', 'uninstall_backup', 0, self.stop),
            'uninstallb': ('stopped', 'uninstalled', 'uninstall_backup', 0, self.uninstall),
            'uninstall_stop': ('running', 'stopped', 'uninstall', 0, self.stop),
            'uninstall': ('stopped', 'uninstalled', 'uninstall', 0, self.uninstall)
        }

        self.dependencies = {
            'config': (DepType.DATA_USE, ['send_config', 'change_config']),
            'pip_libs': (DepType.USE, ['using_docker']),
            'docker': (DepType.USE, ['using_docker']),
            'registry': (DepType.USE, ['pull']),
            'mariadb': (DepType.PROVIDE, ['running'])
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
            result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-4-first", extra_vars={"enos_action":"deploy","db":"mariadb", "db_host":self.host["ip"]})
        else:
            result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-4-only", extra_vars={"enos_action":"deploy","db":"mariadb", "db_host":self.host["ip"]})
        self.print_color("Started container (code %d) with command: %s" % (result.return_code, result.command))

    def go_ready(self):
        self.print_color("Going ready")
        #time.sleep(5.8)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-5", extra_vars={"enos_action":"deploy", "db":"mariadb", "db_host":self.host["ip"]})
        self.print_color("Database ready (code %d) with command: %s" % (result.return_code, result.command))
        
    def restore_backup(self):
        self.print_color("Restoring backup")
        result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-restore", extra_vars={"enos_action":"backup", "db":"mariadb", "db_host":self.host["ip"]})
        self.print_color("Database restored (code %d) with command: %s" % (result.return_code, result.command))

    def backup(self):
        self.print_color("Creating backup")
        result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-backup", extra_vars={"enos_action":"backup", "db":"mariadb", "db_host":self.host["ip"]})
        self.print_color("Database backuped (code %d) with command: %s" % (result.return_code, result.command))

    def stop(self):
        self.print_color("Stopping mariadb")
        #time.sleep(1.4)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-d0", extra_vars={"enos_action":"destroy","db":"mariadb"})
        self.print_color("Stopped container (code %d) with command: %s" % (result.return_code, result.command))

    def uninstall(self):
        self.print_color("Uninstall mariadb")
        #time.sleep(1.6)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "mariadb-d1", extra_vars={"enos_action":"destroy","db":"mariadb"})
        self.print_color("Unmounted /database (code %d) with command: %s" % (result.return_code, result.command))

    def clear_image(self):
        time.sleep(1) # TODO: check

