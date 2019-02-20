from concerto.all import *
from components.python2 import Python2
from components.apache2 import Apache2


class LampAssembly(Assembly):
    def __init__(self):
        Assembly.__init__(self)
        self.python2 = Python2("econome-4", "lamp-playbook.yml")
        self.web = Apache2("econome-4", "lamp-playbook.yml")
        #self.web = Web("hosts", "plb_web.yml")
        #self.db = Db("hosts", "plb_db.yml")
        
    def deploy(self):
        self.add_component("python2", self.python2)
        self.add_component("web", self.web)
        #self.add_component("db", self.db)
        self.push_b("python2", "install")
        self.wait("python2") # Temporary
        self.push_b("web", "install")
        #self.push_b("db", "install")
        self.wait("python2")
        self.wait("web")
        #self.wait("db")
        self.synchronize()


#=======================================
if __name__ == '__main__':
    ass = LampAssembly()
    ass.deploy()
    ass.terminate()
