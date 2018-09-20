from mad import *
from subprocess import run

#=======================================
class Common(Component):

    inventory = ""
    playbook = ""

    def init(self, inventory, playbook):
        self.inventory = inventory
        self.playbook = playbook

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]

        self.transitions = {
            'start': ('waiting', 'started', self.start)
        }

        self.dependencies = {
            'prov': (DepType.PROVIDE, ['started'])
        }

    def start(self):
        print("ansible-playbook -i " + self.inventory + " " + self.playbook)
        return run(["ansible-playbook",
                    "-i", self.inventory,
                    self.playbook]).returncode

#=======================================
class Web(Component):

    inventory = ""
    playbook = ""

    def init(self, inventory, playbook):
        self.inventory = inventory
        self.playbook = playbook

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]

        self.transitions = {
            'start': ('waiting', 'started', self.start)
        }

        self.dependencies = {
            'prov': (DepType.PROVIDE, ['started']),
            'use': (DepType.USE, ['start'])
        }

    def start(self):
        print("ansible-playbook -i " + self.inventory + " " + self.playbook)
        return run(["ansible-playbook",
                    "-i", self.inventory,
                    self.playbook]).returncode

#=======================================
class Db(Component):

    inventory = ""
    playbook = ""

    def init(self, inventory, playbook):
        self.inventory = inventory
        self.playbook = playbook

    def create(self):
        self.places = [
            'waiting',
            'started'
        ]

        self.transitions = {
            'start': ('waiting', 'started', self.start)
        }

        self.dependencies = {
            'use': (DepType.USE, ['start'])
        }

    def start(self):
        print("ansible-playbook -i " + self.inventory + " " + self.playbook)
        return run(["ansible-playbook",
                    "-i", self.inventory,
                    self.playbook]).returncode

#=======================================
if __name__ == '__main__':

    # Composant common
    common = Common()
    common.init("host", "plb_common.yml")

    # Composant web
    web = Web()
    web.init("host", "plb_web.yml")

    # Composant db
    db = Db()
    db.init("host", "plb_db.yml")

    ass = Assembly()
    ass.addComponent('common', common)
    ass.addComponent('web', web)
    ass.addComponent('db', db)
    ass.addConnection(common, 'prov', web, 'use')
    ass.addConnection(web, 'prov', db, 'use')

    mad = Mad(ass)
    mad.run()