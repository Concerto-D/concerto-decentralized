#!/usr/bin/python3

from concerto.all import *
from concerto.meta import ReconfigurationPerfAnalyzer
import time, datetime

from examples.perf_analysis.client import Client
from examples.perf_analysis.server import Server


class ServerClient(Assembly):
    def __init__(self, times_dict):
        self.t_sa = times_dict[('server', 'allocate')]
        self.t_sr = times_dict[('server', 'run')]
        self.t_su = times_dict[('server', 'update')]
        self.t_sc = times_dict[('server', 'cleanup')]
        self.t_ci1 = times_dict[('client', 'install1')]
        self.t_ci2 = times_dict[('client', 'install2')]
        self.t_cc = times_dict[('client', 'configure')]
        self.t_cr = times_dict[('client', 'start')]
        self.t_cs1 = times_dict[('client', 'suspend1')]
        self.t_cs2 = times_dict[('client', 'suspend2')]
        
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
        self.run_reconfiguration(self.deploy_reconf)
        self.synchronize()


times = {
    ('server', 'allocate'): 4,
    ('server', 'run'): 4,
    ('server', 'update'): 1,
    ('server', 'cleanup'): 0.5,
    ('client', 'install1'): 1,
    ('client', 'install2'): 1,
    ('client', 'configure'): 1,
    ('client', 'start'): 1,
    ('client', 'suspend1'): 1,
    ('client', 'suspend2'): 1,
}

sc = ServerClient(times)

sc.set_record_gantt(True)

pa = ReconfigurationPerfAnalyzer(sc.deploy_reconf)
g = pa.get_graph()
g.save_as_dot("server_client.dot")
formula = pa.get_exec_time_formula()
print(formula.to_string(lambda x: '.'.join(x)))
print("Time predicted by graph traversal:\n%f" % pa.get_exec_time(times))
print("Time predicted by formula evaluation:\n%f" % formula.evaluate(times))

print("Running reconf...")
start_time: float = time.perf_counter()
sc.deploy()
end_time: float = time.perf_counter()
sc.terminate()
print("Time actually measured:\n%f" % (end_time-start_time))

sc.set_record_gantt(True)
# ...
gr = sc.get_gantt_record()
gc = gr.get_gantt_chart()
gc.export_json("gantt_chart.json")
