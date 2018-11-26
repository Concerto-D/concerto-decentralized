from subprocess import run

from madpp.all import *

class Python2(Component):

    def __init__(self, inventory, playbook):
        self.inventory = inventory
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
        tag = "python2-0"
        command = "ansible-playbook -vv -i " + self.inventory + " " + self.playbook + " --tags \"" + tag + "\""
        self.print_color(command)
        return run(command, shell=True).returncode
        #return run(["ansible-playbook",
                    #"-vv",
                    #"-i", self.inventory,
                    #self.playbook,
                    #"--tags", "\"" + tag +"\""],
                #shell=True).returncode
        self.print_color("Installed Python 2")
