from madpp.all import *
from madpp.plugins.ansible import call_ansible_on_host, AnsibleCallResult

class Apache2(Component):

    def __init__(self, host, playbook):
        self.host = host
        self.playbook = playbook
        Component.__init__(self)

    def create(self):
        self.places = [
            'waiting',
            'installed',
            'enabled',
            'configured',
            'removed_default_index',
            'uploaded_index',
            'running'
        ]

        self.transitions = {
            'install': ('waiting', 'installed', 'install', 0, self.install),
            'enable': ('installed', 'enabled', 'install', 0, self.enable),
            'configure': ('enabled', 'configured', 'install', 0, self.configure),
            'remove_default_index': ('configured', 'removed_default_index', 'install', 0, self.remove_default_index),
            'upload_index': ('removed_default_index', 'uploaded_index', 'install', 0, self.upload_index),
            'reboot': ('uploaded_index', 'running', 'install', 0, self.reboot)
        }

        self.dependencies = {
            'apache2': (DepType.PROVIDE, ['running'])
        }
        
        self.initial_place = 'waiting'

    def install(self):
        self.print_color("Installing Apache 2")
        result = call_ansible_on_host(self.host, self.playbook, "apache2-0")
        self.print_color("Installed Apache 2 (code %d) with command: %s" % (result.return_code, result.command))

    def enable(self):
        self.print_color("Enabling Apache 2")
        result = call_ansible_on_host(self.host, self.playbook, "apache2-1")
        self.print_color("Enabled Apache 2 (code %d) with command: %s" % (result.return_code, result.command))

    def configure(self):
        self.print_color("Configuring Apache 2")
        result = call_ansible_on_host(self.host, self.playbook, "apache2-2")
        self.print_color("Configured Apache 2 (code %d) with command: %s" % (result.return_code, result.command))

    def remove_default_index(self):
        self.print_color("Removing default index of Apache 2")
        result = call_ansible_on_host(self.host, self.playbook, "apache2-3")
        self.print_color("Removed default index of Apache 2 (code %d) with command: %s" % (result.return_code, result.command))

    def upload_index(self):
        self.print_color("Uploading index to Apache 2")
        result = call_ansible_on_host(self.host, self.playbook, "apache2-4")
        self.print_color("Uploaded index to Apache 2 (code %d) with command: %s" % (result.return_code, result.command))

    def reboot(self):
        self.print_color("Rebooting Apache 2")
        result = call_ansible_on_host(self.host, self.playbook, "apache2-5")
        self.print_color("Rebooted Apache 2 (code %d) with command: %s" % (result.return_code, result.command))
