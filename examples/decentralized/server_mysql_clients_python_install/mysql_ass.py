from examples.decentralized.mysql_assembly import MysqlAssembly
import sys

sa = MysqlAssembly(is_asynchrone=False)
sa.set_verbosity(2)
sa.set_print_time(True)

n = int(sys.argv[1]) if len(sys.argv) > 1 else 1

# print("-------- 1st reconf ----------------")
sa.add_component('mysql', sa.mysql)
sa.connect('mysql', 'service', 'server', 'bdd')
sa.push_b('mysql', 'install_start')
sa.wait_all()
# sa.synchronize()

# print("-------- 2nd reconf ----------------")
sa.push_b('mysql', 'uninstall')
sa.wait_all()
# sa.synchronize()

# print("-------- 3rd reconf")
sa.push_b('mysql', 'install_start')
sa.wait_all()
# sa.synchronize()

# print("-------- Final reconf ----------------")
sa.push_b('mysql', 'uninstall')
sa.wait('server')
sa.wait('client_server')
sa.wait_all()
sa.disconnect('mysql', 'service', 'server', 'bdd')
sa.del_component('mysql')
# sa.synchronize()
# sa.wait_all()
sa.execute_reconfiguration_program()
# sa.terminate()

print("---------------END MYSQL-----------------")
