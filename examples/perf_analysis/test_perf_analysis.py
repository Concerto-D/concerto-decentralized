#!/usr/bin/python3

from concerto.all import *
from concerto.utility import Printer
import time, datetime

from examples.perf_analysis.client import Client
from examples.perf_analysis.server import Server


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
        
        dr = Reconfiguration()
        dr.add('client', Client, t_ci1=self.t_ci1, t_ci2=self.t_ci2, t_cc=self.t_cc, t_cr=self.t_cr, t_cs1=self.t_cs1, t_cs2=self.t_cs2)
        dr.add('server', Server, t_sa=self.t_sa, t_sr=self.t_sr, t_su=self.t_su, t_sc=self.t_sc)
        dr.connect('client', 'server_ip',
                    'server', 'ip')
        dr.connect('client', 'service',
                    'server', 'service')
        dr.push_behavior('client', 'install_start')
        dr.push_behavior('server', 'deploy')
        dr.wait_all()
        
        self.deploy_reconf = dr
        
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


from concerto.meta import ReconfigurationPerfAnalyzer
sc = ServerClient()
pa = ReconfigurationPerfAnalyzer(sc.deploy_reconf)
g = pa.get_graph()
g.save_as_dot("server_client.dot")
print(pa.get_exec_time_formula().to_string(lambda x: '.'.join(x)))
