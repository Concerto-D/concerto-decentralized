import time

from concerto.all import *
from concerto.utility import *
from concerto.plugins.ansible import call_ansible_on_host, AnsibleCallResult

class AptUtils(Component):
    
    def __init__(self, host, install_ceph):
        self.host = host
        self.playbook = "ansible/aptutils.yml"
        self.install_ceph = install_ceph
        Component.__init__(self)

    def create(self):
        self.places = [
            'uninstalled',
            'utils',
            'ceph',
            'python',
            'docker'
        ]
        
        self.groups = {
            'providing_apt_utils': ['utils', 'python', 'docker'],
            'providing_apt_python': ['python', 'docker'],
            'providing_apt_docker': ['docker']
        }
        if (self.install_ceph):
            self.groups['providing_apt_ceph'] = ['ceph', 'python', 'docker']
            self.groups['providing_apt_utils'].append('ceph')

        self.transitions = {
            'install_utils': ('uninstalled', 'utils', 'install', 0, self.install_utils),
            'install_docker': ('python', 'docker', 'install', 0, self.install_docker)
        }
        if (self.install_ceph):
            self.transitions['install_ceph'] = ('utils', 'ceph', 'install', 0, self.install_ceph)
            self.transitions['install_python'] = ('ceph', 'python', 'install', 0, self.install_python)
        else:
            self.transitions['install_python'] = ('utils', 'python', 'install', 0, self.install_python)

        self.dependencies = {
            'apt_utils': (DepType.PROVIDE, ['providing_apt_utils']),
            'apt_python': (DepType.PROVIDE, ['providing_apt_python']),
            'apt_docker': (DepType.PROVIDE, ['providing_apt_docker'])
        }
        if (self.install_ceph):
            self.dependencies['apt_ceph'] = (DepType.PROVIDE, ['providing_apt_ceph'])
        
        self.initial_place = 'uninstalled'
        

    def install_utils(self):
        #time.sleep(12.5)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "aptutils-0", extra_vars={"enos_action":"deploy"})
        self.print_color("Installed apt_utils (code %d) with command: %s" % (result.return_code, result.command))
        

    def install_ceph(self):
        #time.sleep(20.6)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "aptutils-ceph", extra_vars={"enos_action":"deploy"})
        self.print_color("Installed ceph (code %d) with command: %s" % (result.return_code, result.command))
        

    def install_python(self):
        #time.sleep(20.6)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "aptutils-python", extra_vars={"enos_action":"deploy"})
        self.print_color("Installed python (code %d) with command: %s" % (result.return_code, result.command))
        

    def install_docker(self):
        #time.sleep(20.6)
        result = call_ansible_on_host(self.host["ip"], self.playbook, "aptutils-docker", extra_vars={"enos_action":"deploy"})
        self.print_color("Installed docker (code %d) with command: %s" % (result.return_code, result.command))

