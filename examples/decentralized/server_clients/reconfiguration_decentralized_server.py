from examples.decentralized.servers_assembly import Servers
import sys

sa = Servers()
sa.set_verbosity(2)
sa.set_print_time(True)

n = int(sys.argv[1]) if len(sys.argv) > 1 else 1

print("-------- 1st reconf ----------------")
sa.add_component('server', sa.server)
for i in range(1, n+1):
    sa.connect('server', 'ip', 'client'+str(i), 'server_ip')
    sa.connect('server', 'service', 'client'+str(i), 'service')
sa.push_b('server', 'deploy')
sa.wait_all()
sa.synchronize()

print("-------- 2nd reconf ----------------")
sa.push_b('server', 'stop')
sa.push_b('server', 'deploy')
sa.wait_all()
sa.synchronize()

print("-------- Final reconf ----------------")
sa.push_b('server', 'stop')
sa.push_b('server', 'undeploy')
sa.wait('server')
for i in range(1, n+1):
    sa.disconnect('server', 'ip', 'client'+str(i), 'server_ip')
    sa.disconnect('server', 'service', 'client'+str(i), 'service')
sa.del_component('server')
sa.synchronize()

sa.terminate()

print("---------------END SERVER-----------------")
