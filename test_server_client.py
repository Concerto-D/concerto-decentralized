from mad import *
import time


class Client(Component):

    def create(self):
        self.places = [
            'off',
            'configured',
            'running'
        ]

        self.transitions = {
            'configure': ('off', 'configured', 'install_start', 0, self.configure),
            'start': ('configured', 'running', 'install_start', 0, self.start),
            'suspend': ('configured', 'started', 'stop', 0, self.suspend)
        }

        self.dependencies = {
            'server_ip': (DepType.DATA_USE, ['configure']),
            'service': (DepType.USE, ['start'])
        }
        
        self.initial_place = 'off'

    def __init__(self):
        self.server_ip = None
        Component.__init__(self)

    def configure(self):
        print("Client: configuration (1/2)")
        time.sleep(1)
        print("Client: waiting for server IP")
        self.server_ip = self.read('server_ip')
        print("Client: configuration (2/2) [server IP: %s]" % self.server_ip)
        time.sleep(1)
        print("Client: configured")

    def start(self):
        print("Client: starting")
        time.sleep(1)
        print("Client: running")

    def suspend(self):
        print("Client: suspending")
        time.sleep(2)
        print("Client: suspended")


class Server(Component):

    def create(self):
        self.places = [
            'undeployed',
            'allocated',
            'running',
            'maintenance'
        ]

        self.transitions = {
            'allocate': ('undeployed', 'allocated', 'deploy', 0, self.allocate),
            'run': ('allocated', 'running', 'deploy', 0, self.run),
            'suspend': ('running', 'maintenance', 'stop', 0, self.suspend),
            'restart': ('maintenance', 'allocated', 'deploy', 1, self.restart)
        }

        self.dependencies = {
            'ip': (DepType.DATA_PROVIDE, ['allocated']),
            'service': (DepType.PROVIDE, ['running'])
        }
        
        self.initial_place = 'undeployed'

    def __init__(self):
        self.my_ip = None
        Component.__init__(self)

    def allocate(self):
        print("Server: allocating resources")
        time.sleep(4)
        self.my_ip = "123.124.1.2"
        print("Server: got IP %s" % self.my_ip)
        self.write('ip', self.my_ip)
        print("Server: finished allocation")

    def run(self):
        print("Server: preparing to run")
        time.sleep(4)
        print("Server: running")

    def suspend(self):
        print("Server: suspending")
        time.sleep(1)
        print("Server: suspended")

    def restart(self):
        print("Server: restarting")
        time.sleep(0.5)
        

if __name__ == '__main__':

    # Client
    client = Client()

    # Server
    server = Server()
    
    # Assembly
    ass = Assembly()
    #ass.add_component('client', client)
    ass.add_component('server', server)
    #ass.connect('client', 'server_ip',
    #            'server', 'ip')
    #ass.connect('client', 'service',
    #            'server', 'service')
    #ass.change_behavior('client', 'install_start')
    ass.change_behavior('server', 'deploy')
