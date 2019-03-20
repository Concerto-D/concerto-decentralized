#!/usr/bin/python3

from concerto.all import *

from client import Client
from server import Server


class ServerClient(Assembly):
    def __init__(self, t_sa=4., t_sr=4., t_su=1., t_sc=0.5, t_ci1=1., t_ci2=1., t_cc=1., t_cr=1., t_cs1=2., t_cs2=0.):
        self.t_sa = t_sa
        self.t_sr = t_sr
        self.t_su = t_su
        self.t_sc = t_sc
        self.t_ci1 = t_ci1
        self.t_ci2 = t_ci2
        self.t_cc = t_cc
        self.t_cr = t_cr
        self.t_cs1 = t_cs1
        self.t_cs2 = t_cs2
        self.server = Server(t_sa=self.t_sa, t_sr=self.t_sr, t_su=self.t_su, t_sc=self.t_sc)
        self.client = Client(t_ci1=self.t_ci1, t_ci2=self.t_ci2, t_cc=self.t_cc, t_cr=self.t_cr, t_cs1=self.t_cs1, t_cs2=self.t_cs2)
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
        self.wait('client')
        self.synchronize()
        
    def suspend(self):
        self.print("### SUSPENDING ###")
        self.push_b('client', 'stop')
        self.push_b('server', 'stop')
        self.wait('server')
        self.synchronize()
        
    def restart(self):
        self.print("### RESTARTING ###")
        self.push_b('client', 'install_start')
        self.push_b('server', 'deploy')
        self.wait('client')
        self.synchronize()
        
    def maintain(self):
        self.print("### MAINTAINING ###")
        self.push_b('client', 'stop')
        self.push_b('server', 'stop')
        self.push_b('client', 'install_start')
        self.push_b('server', 'deploy')
        self.wait('client')
        self.synchronize()
