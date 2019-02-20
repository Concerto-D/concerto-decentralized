from concerto.all import *
from concerto.plugins.ansible import call_ansible_on_host, AnsibleCallResult

class Python2(Component):

    def __init__(self, host, playbook):
        self.host = host
        self.playbook = playbook
        Component.__init__(self)

    def create(self):
        self.places = [
            'waiting',
            'installed'
        ]

        self.transitions = {
            'install': ('waiting', 'installed', 'install', 0, self.install)
        }

        self.dependencies = {
            'python2': (DepType.PROVIDE, ['installed'])
        }
        
        self.initial_place = 'waiting'

    def install(self):
        self.print_color("Installing Python 2")
        result = call_ansible_on_host(self.host, self.playbook, "python2-0")
        self.print_color("Installed Python 2 (code %d) with command: %s" % (result.return_code, result.command))
