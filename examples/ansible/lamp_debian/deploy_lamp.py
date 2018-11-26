from madpp.all import *
from components.python2 import Python2


class LampAssembly(Assembly):
    def __init__(self):
        Assembly.__init__(self)
        self.python2 = Python2("econome-4,", "lamp-playbook.yml")
        #self.common = Common("hosts", "plb_common.yml")
        #self.web = Web("hosts", "plb_web.yml")
        #self.db = Db("hosts", "plb_db.yml")
        
    def deploy(self):
        self.add_component("python2", self.python2)
        #self.add_component("common", self.common)
        #self.add_component("web", self.web)
        #self.add_component("db", self.db)
        self.change_behavior("python2", "install")
        #self.change_behavior("common", "start")
        #self.change_behavior("web", "start")
        #self.change_behavior("db", "start")
        self.wait("python2")
        #self.wait("common")
        #self.wait("web")
        #self.wait("db")
        self.synchronize()


#=======================================
if __name__ == '__main__':
    ass = LampAssembly()
    ass.deploy()
    ass.terminate()
