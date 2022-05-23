from concerto.all import *


class ServerMysql(Component):

    def create(self):
        self.places = [
            'undeployed',
            'allocated',
            'configured',
            'running'
        ]

        self.groups = {
            'using_bdd': ['running', 'configured']
        }

        self.transitions = {
            'allocate': ('undeployed', 'allocated', 'deploy', 0, self.allocate),
            'configure': ('allocated', 'configured', 'deploy', 0, self.configure),
            'run': ('configured', 'running', 'deploy', 0, self.run),
            'update': ('running', 'allocated', 'stop', 0, self.update),
            'cleanup': ('running', 'allocated', 'stop', 0, self.cleanup),
            'undeploy': ('allocated', 'undeployed', 'undeploy', 0, self.undeploy)
        }

        self.dependencies = {
            'ip': (DepType.DATA_PROVIDE, ['allocated']),
            'bdd': (DepType.USE, ['using_bdd']),
            'service': (DepType.PROVIDE, ['running'])
        }
        
        self.initial_place = 'undeployed'

    def __init__(self):
        # self.my_ip = None
        Component.__init__(self)

    def allocate(self):
        self.print_color("allocating resources")
        time.sleep(6.)
        self.my_ip = "123.124.1.2"
        self.write('ip', self.my_ip)
        self.print_color("finished allocation (IP: %s)" % self.my_ip)

    def configure(self):
        self.print_color("configuring")
        time.sleep(4.)
        self.print_color("configured")

    def run(self):
        self.print_color("preparing to run")
        time.sleep(4.)
        self.print_color("running")

    def update(self):
        self.print_color("updating")
        time.sleep(3.)
        self.print_color("updated")

    def cleanup(self):
        self.print_color("cleaning up")
        time.sleep(2.) 
        self.print_color("cleaned up")

    def undeploy(self):
        self.print_color("undeploying")
        time.sleep(2.)
        self.print_color("undeployed")
