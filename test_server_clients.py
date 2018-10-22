from mad import *
import time, datetime


printing = True
def tprint(message : str):
    if printing:
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
            'suspend': ('running', 'configured', 'stop', 0, self.suspend)
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


class ServerClient(Assembly):
    def __init__(self):
        Assembly.__init__(self)
        self.nb_clients = 2000
        self.clients = []
        for i in range(self.nb_clients):
            new_client = Client()
            self.clients.append(new_client)
            self.add_component('client%d'%i, new_client)
        self.server = Server()
        self.add_component('server', self.server)
    
    def deploy(self):
        tprint("### DEPLOYING ####")
        for i in range(self.nb_clients):
            self.connect('client%d'%i, 'server_ip',
                        'server', 'ip')
            self.connect('client%d'%i, 'service',
                        'server', 'service')
            self.change_behavior('client%d'%i, 'install_start')
        self.change_behavior('server', 'deploy')
        tprint("Assembly: waiting clients")
        for i in range(self.nb_clients):
            self.wait('client%d'%i)
        tprint("Assembly: waiting server")
        self.wait('server')
        
    def suspend(self):
        tprint("### SUSPENDING ###")
        for i in range(self.nb_clients):
            self.change_behavior('client%d'%i, 'stop')
        for i in range(self.nb_clients):
            self.wait('client%d'%i)
        self.change_behavior('server', 'stop')
        self.wait('server')
        
    def restart(self):
        tprint("### RESTARTING ###")
        
        for i in range(self.nb_clients):
            self.change_behavior('client%d'%i, 'install_start')
        self.change_behavior('server', 'deploy')
        tprint("Assembly: waiting clients")
        for i in range(self.nb_clients):
            self.wait('client%d'%i)
        tprint("Assembly: waiting server")
        self.wait('server')
        
        
        

if __name__ == '__main__':
    printing = False
    
    sca = ServerClient()
    
    start_time : float = time.clock()
    sca.deploy()
    
    tprint("Main: waiting a little before reconfiguring")
    time.sleep(3)
    
    sca.suspend()
    tprint("Main: server maintenance")
    time.sleep(5)
    
    tprint("Main: maintenance over")
    sca.restart()
    
    end_time : float = time.clock()
    print("Total time in seconds: %f"%(end_time-start_time))
    
    sca.terminate()
    exit(0)
