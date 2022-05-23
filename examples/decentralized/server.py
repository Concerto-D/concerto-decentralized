from concerto.all import *


class Server(Component):

    def create(self):
        self.places = [
            'undeployed',
            'allocated',
            'running'
        ]

        self.transitions = {
            'allocate': ('undeployed', 'allocated', 'deploy', 0, self.allocate),
            'run': ('allocated', 'running', 'deploy', 0, self.run),
            'update': ('running', 'allocated', 'stop', 0, self.update),
            'cleanup': ('running', 'allocated', 'stop', 0, self.cleanup),
            'undeploy': ('allocated', 'undeployed', 'undeploy', 0, self.undeploy)
        }

        self.dependencies = {
            # 'ip': (DepType.DATA_PROVIDE, ['allocated']),
            'service': (DepType.PROVIDE, ['running'])
        }
        
        self.initial_place = 'undeployed'

    def __init__(self):
        # self.my_ip = None
        Component.__init__(self)

    def allocate(self):
        self.print_color("allocating resources")
        time.sleep(6.)
        # self.my_ip = "123.124.1.2"
        # self.write('ip', self.my_ip)
        # self.print_color("finished allocation (IP: %s)" % self.my_ip)

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
