from examples.decentralized.servers_assembly import Servers
import sys

sa = Servers()
sa.set_verbosity(2)
sa.set_print_time(True)

n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
sa.add_component('server', sa.server)
for i in range(1, n+1):
    sa.connect('server', 'ip', 'client'+str(i), 'server_ip')

for i in range(1, n+1):
    sa.disconnect('server', 'ip', 'client'+str(i), 'server_ip')

sa.del_component('server')
sa.synchronize()
sa.terminate()

print("---------------END SERVER-----------------")
