from madpp.all import *
from subprocess import run

#=======================================
class Common(Component):

    def __init__(self, inventory, playbook):
        self.inventory = inventory
        self.playbook = playbook
        Component.__init__(self)

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]

        self.transitions = {
            'start': ('waiting', 'started', 'start', 0, self.start)
        }

        self.dependencies = {
            'prov': (DepType.PROVIDE, ['started'])
        }
        
        self.initial_place = 'waiting'

    def start(self):
        print("ansible-playbook -i " + self.inventory + " " + self.playbook)
        return run(["ansible-playbook",
                    "-i", self.inventory,
                    self.playbook]).returncode

#=======================================
class Web(Component):

    def __init__(self, inventory, playbook):
        self.inventory = inventory
        self.playbook = playbook
        Component.__init__(self)

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]

        self.transitions = {
            'start': ('waiting', 'started', 'start', 0, self.start)
        }

        self.dependencies = {
            'prov': (DepType.PROVIDE, ['started']),
            'use': (DepType.USE, ['start'])
        }
        
        self.initial_place = 'waiting'

    def start(self):
        print("ansible-playbook -i " + self.inventory + " " + self.playbook)
        return run(["ansible-playbook",
                    "-i", self.inventory,
                    self.playbook]).returncode

#=======================================
class Db(Component):

    def __init__(self, inventory, playbook):
        self.inventory = inventory
        self.playbook = playbook
        Component.__init__(self)

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]

        self.transitions = {
            'start': ('waiting', 'started', 'start', 0, self.start)
        }

        self.dependencies = {
            'use': (DepType.USE, ['start'])
        }
        
        self.initial_place = 'waiting'

    def start(self):
        print("ansible-playbook -i " + self.inventory + " " + self.playbook)
        return run(["ansible-playbook",
                    "-i", self.inventory,
                    self.playbook]).returncode

#=======================================
class PlbAssembly(Assembly):
    def __init__(self):
        Assembly.__init__(self)
        self.common = Common("host", "plb_common.yml")
        self.web = Web("host", "plb_web.yml")
        self.db = Db("host", "plb_db.yml")
        
    def deploy(self):
        self.add_component("common", self.common)
        self.add_component("web", self.web)
        self.add_component("db", self.db)
        self.change_behavior("common", "start")
        self.change_behavior("web", "start")
        self.change_behavior("db", "start")
        self.wait("common")
        self.wait("web")
        self.wait("db")
        self.synchronize()


#=======================================
if __name__ == '__main__':
    ass = PlbAssembly()
    ass.deploy()
