from mad import *
import time, datetime

def tprint(message : str):
    now = datetime.datetime.now()
    print("[%2d:%2d:%2d:%3d] %s"%(now.hour,now.minute, now.second, now.microsecond/1000, message))


class Client(Component):

    def create(self):
        self.places = [
            'off',
            'waiting_server_ip',
            'configured',
            'running'
        ]

        self.transitions = {
            'configure1': ('off', 'waiting_server_ip', 'install_start', 0, self.configure1),
            'configure2': ('waiting_server_ip', 'configured', 'install_start', 0, self.configure2),
            'start': ('configured', 'running', 'install_start', 0, self.start),
            'suspend': ('configured', 'started', 'stop', 0, self.suspend)
        }

        self.dependencies = {
            'server_ip': (DepType.DATA_USE, ['configure2']),
            'service': (DepType.USE, ['start'])
        }
        
        self.initial_place = 'off'

    def __init__(self):
        self.server_ip = None
        Component.__init__(self)

    def configure1(self):
        tprint("Client: configuration (1/2)")
        time.sleep(1)
        tprint("Client: waiting for server IP")

    def configure2(self):
        self.server_ip = self.read('server_ip')
        tprint("Client: configuration (2/2) [server IP: %s]" % self.server_ip)
        time.sleep(1)
        tprint("Client: configured")

    def start(self):
        tprint("Client: starting")
        time.sleep(1)
        tprint("Client: running")

    def suspend(self):
        tprint("Client: suspending")
        time.sleep(2)
        tprint("Client: suspended")


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
        tprint("Server: allocating resources")
        time.sleep(4)
        self.my_ip = "123.124.1.2"
        tprint("Server: got IP %s" % self.my_ip)
        self.write('ip', self.my_ip)
        tprint("Server: finished allocation")

    def run(self):
        tprint("Server: preparing to run")
        time.sleep(4)
        tprint("Server: running")

    def suspend(self):
        tprint("Server: suspending")
        time.sleep(1)
        tprint("Server: suspended")

    def restart(self):
        tprint("Server: restarting")
        time.sleep(0.5)
        

if __name__ == '__main__':

    # Client
    client = Client()

    # Server
    server = Server()
    
    # Assembly
    ass = Assembly()
    ass.add_component('client', client)
    ass.add_component('server', server)
    ass.connect('client', 'server_ip',
                'server', 'ip')
    ass.connect('client', 'service',
                'server', 'service')
    ass.change_behavior('client', 'install_start')
    ass.change_behavior('server', 'deploy')
    
    tprint("Assembly: waiting client")
    ass.wait('client')
    tprint("Assembly: waiting server")
    ass.wait('server')
    exit(0)
