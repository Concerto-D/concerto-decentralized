from examples.decentralized.clients_assembly import Clients

import sys

n = sys.argv[1] if len(sys.argv) > 1 else "1"
sc = Clients(n)
sc.set_verbosity(1)
sc.set_print_time(True)

print("-------- 1st reconf ----------------")
sc.add_component('client'+n, sc.client)
sc.connect('client'+n, 'server_ip', 'server', 'ip')
sc.connect('client'+n, 'service', 'server', 'service')
sc.push_b('client'+n, 'install_start')
sc.wait_all()
sc.synchronize()

print("-------- 2nd reconf ----------------")
sc.push_b('client'+n, 'stop')
sc.push_b('client'+n, 'install_start')
sc.wait_all()
sc.synchronize()

print("-------- Final reconf ----------------")
sc.push_b('client'+n, 'stop')
sc.push_b('client'+n, 'uninstall')
sc.wait('client'+n)
sc.disconnect('client'+n, 'server_ip', 'server', 'ip')
sc.disconnect('client'+n, 'service', 'server', 'service')
sc.del_component('client'+n)
sc.synchronize()

sc.terminate()

print(f"---------------END CLIENT {n}-----------------")
