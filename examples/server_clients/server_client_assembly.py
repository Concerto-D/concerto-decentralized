#!/usr/bin/python3

from concerto.all import *
from examples.server_clients.client import Client
from examples.server_clients.server import Server


class ServerClient(Assembly):
    def __init__(self):
        self.server = Server()
        self.client = Client()
        Assembly.__init__(self)
    
    def deploy(self):
        self.print("### DEPLOYING ####")
        self.add_component('client', self.client)
        self.add_component('server', self.server)
        self.connect('client', 'server_ip',
                    'server', 'ip')
        self.connect('client', 'service',
                    'server', 'service')
        self.push_b('client', 'install_start')
        self.push_b('server', 'deploy')
        self.wait_all()
        self.synchronize()

    def suspend_restart(self):
        self.print("### SUSPENDING ###")
        self.push_b('client', 'stop')
        self.push_b('client', 'install_start')
        self.push_b('server', 'stop')
        self.push_b('server', 'deploy')
        self.wait_all()
        self.synchronize()
        
    def suspend(self):
        self.print("### SUSPENDING ###")
        self.push_b('client', 'stop')
        self.push_b('server', 'stop')
        self.wait_all()
        self.synchronize()
        
    def restart(self):
        self.print("### RESTARTING ###")
        self.push_b('client', 'install_start')
        self.push_b('server', 'deploy')
        self.wait_all()
        self.synchronize()
        
    def maintain(self):
        self.print("### MAINTAINING ###")
        self.push_b('client', 'stop')
        self.push_b('server', 'stop')
        self.push_b('client', 'install_start')
        self.push_b('server', 'deploy')
        self.wait_all()
        self.synchronize()
