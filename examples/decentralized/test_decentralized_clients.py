from examples.decentralized.clients_assembly import Clients

import sys

n = sys.argv[1] if len(sys.argv) > 1 else "1"
sc = Clients(n)
sc.set_verbosity(1)
sc.set_print_time(True)

sc.add_component('client'+n, sc.client)
sc.connect('client'+n, 'server_ip', 'server', 'ip')
sc.disconnect('client'+n, 'server_ip', 'server', 'ip')
sc.del_component('client'+n)
sc.synchronize()
sc.terminate()

print(f"---------------END CLIENT {n}-----------------")
