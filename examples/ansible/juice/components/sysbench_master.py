import time

from madpp.all import *
from madpp.utility import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult


class SysbenchMaster(Component):
    
    def __init__(self, host):
        self.host = host
        self.playbook = "ansible/sysbenchmaster.yml"
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'uninstalled_mysql',
            'user',
            'database',
            'suspended'
        ]
        
        self.groups = {
            'using_mysql': ['uninstalled_mysql', 'user', 'database']
        }

        self.transitions = {
            'use_mysql': ('uninstalled', 'uninstalled_mysql', 'install', 0, empty_transition),
            'to_user': ('uninstalled_mysql', 'user', 'install', 0, self.to_user),
            'to_database': ('user', 'database', 'install', 0, self.to_database),
            'suspend': ('database', 'suspended', 'suspend', 0, self.suspend),
            'restart': ('suspended', 'database', 'install', 1, self.restart)
        }

        self.dependencies = {
            'mysql': (DepType.USE, ['using_mysql']),
            'my_ip': (DepType.DATA_USE, ['to_user','to_database']),
            'user_credentials': (DepType.DATA_USE, ['to_user']),
            'db_credentials': (DepType.DATA_USE, ['to_user']),
            'sysbench_db': (DepType.PROVIDE, ['database'])
        }
        
        self.initial_place = 'uninstalled'
        
    def to_user(self):
        my_ip = self.read('my_ip')
        user_credentials = self.read('user_credentials')
        db_credentials = self.read('db_credentials')
        self.print_color("Going to user with ip \'%s\', user credentials \'%s\' and DB credentials \'%s\'"%(my_ip, user_credentials, db_credentials))
        #time.sleep(0.9)
        result = call_ansible_on_host(self.host, self.playbook, "sysbenchmaster-0", extra_vars={"enos_action": "deploy", "hostname": self.host})
        self.print_color("Create MariaDB sbtest user (code %d) with command: %s" % (result.return_code, result.command))

    def to_database(self):
        my_ip = self.read('my_ip')
        self.print_color("Going to database with ip \'%s\'"%my_ip)
        #time.sleep(0.9)
        result = call_ansible_on_host(self.host, self.playbook, "sysbenchmaster-1", extra_vars={"enos_action": "deploy", "hostname": self.host})
        self.print_color("Created MariaDB sbtest database (code %d) with command: %s" % (result.return_code, result.command))

    def suspend(self):
        time.sleep(0)

    def restart(self):
        time.sleep(0)
