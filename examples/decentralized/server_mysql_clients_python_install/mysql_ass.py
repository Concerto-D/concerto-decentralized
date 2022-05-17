from examples.decentralized.mysql_assembly import MysqlAssembly
from examples.decentralized.servers_assembly import Servers
import sys

sa = MysqlAssembly()
sa.set_verbosity(2)
sa.set_print_time(True)
sa.id_sync = 0

n = int(sys.argv[1]) if len(sys.argv) > 1 else 1

print("-------- 1st reconf ----------------")
sa.add_component('mysql', sa.mysql)
sa.connect('mysql', 'service', 'server', 'bdd')
sa.push_b('mysql', 'install_start')
sa.wait_all()
sa.synchronize()
sa.id_sync += 1

print("-------- 2nd reconf ----------------")
sa.push_b('mysql', 'uninstall')
sa.wait_all()
sa.synchronize()
sa.id_sync += 1

print("-------- 3rd reconf")
sa.push_b('mysql', 'install_start')
sa.wait_all()
sa.synchronize()
sa.id_sync += 1

print("-------- Final reconf ----------------")
sa.push_b('mysql', 'uninstall')
sa.wait('server')
sa.wait('client_server')
sa.disconnect('mysql', 'service', 'server', 'bdd')
sa.del_component('mysql')
sa.synchronize()

sa.terminate()

print("---------------END MYSQL-----------------")
