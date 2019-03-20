#!/usr/bin/python3

from concerto.all import *

from client import Client
from server import Server


class ServerClients(Assembly):
    def __init__(self, nb_clients):
        self.nb_clients = nb_clients
        Assembly.__init__(self)
        
        self.clients = []
        for i in range(self.nb_clients):
            self.clients.append(Client())
            self.add_component(self.client_name(i), self.clients[i])
        
        self.server = Server()
        self.add_component('server', self.server)
        self.synchronize()
    
    @staticmethod
    def client_name(id : int):
        return 'client%d'%id
    
    def deploy(self):
        self.print("### DEPLOYING ####")
        for i in range(self.nb_clients):
            self.connect(self.client_name(i), 'server_ip',
                    'server', 'ip')
            self.connect(self.client_name(i), 'service',
                    'server', 'service')
            self.push_b(self.client_name(i), 'install_start')
        self.push_b('server', 'deploy')
        self.wait_all()
        self.synchronize()
        
    def suspend(self):
        self.print("### SUSPENDING ###")
        for i in range(self.nb_clients):
            self.push_b(self.client_name(i), 'stop')
        self.push_b('server', 'stop')
        self.wait_all()
        self.synchronize()
        
    def restart(self):
        self.print("### RESTARTING ###")
        for i in range(self.nb_clients):
            self.push_b(self.client_name(i), 'install_start')
        self.push_b('server', 'deploy')
        self.wait_all()
        self.synchronize()
