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
        self.client = Client()
        self.server = Server()
        self.add_component('client', self.client)
        self.add_component('server', self.server)
    
    def deploy(self):
        print("### DEPLOYING ####")
        self.connect('client', 'server_ip',
                    'server', 'ip')
        self.connect('client', 'service',
                    'server', 'service')
        self.change_behavior('client', 'install_start')
        self.change_behavior('server', 'deploy')
        tprint("Assembly: waiting client")
        self.wait('client')
        tprint("Assembly: waiting server")
        self.wait('server')
        
        #DEBUGGING
        print("Server active places: %s"%','.join([p.get_name() for p in self.server.act_places]))
        print("Client active places: %s"%','.join([p.get_name() for p in self.client.act_places]))
        
    def suspend(self):
        print("### SUSPENDING ###")
        self.change_behavior('client', 'stop')
        self.wait('client')
        self.change_behavior('server', 'stop')
        self.wait('server')
        
        #DEBUGGING
        print("Server active places: %s"%','.join([p.get_name() for p in self.server.act_places]))
        print("Client active places: %s"%','.join([p.get_name() for p in self.client.act_places]))
        
    def restart(self):
        print("### RESTARTING ###")
        
        #DEBUGGING
        print("Server active places: %s"%','.join([p.get_name() for p in self.server.act_places]))
        print("Client active places: %s"%','.join([p.get_name() for p in self.client.act_places]))
        
        self.change_behavior('client', 'install_start')
        self.change_behavior('server', 'deploy')
        tprint("Assembly: waiting client")
        self.wait('client')
        tprint("Assembly: waiting server")
        self.wait('server')
        
        
        

if __name__ == '__main__':
    sca = ServerClient()
    sca.deploy()
    
    tprint("Main: waiting a little before reconfiguring")
    time.sleep(3)
    
    sca.suspend()
    tprint("Main: server maintenance")
    time.sleep(5)
    
    tprint("Main: maintenance over")
    sca.restart()
    
    sca.terminate()
    exit(0)
