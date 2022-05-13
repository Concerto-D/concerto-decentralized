import sys

from examples.decentralized.servers_mysql_assembly import ServerMysql, ServerMysqlAssembly

sa = ServerMysqlAssembly()
sa.set_verbosity(2)
sa.set_print_time(True)

n = int(sys.argv[1]) if len(sys.argv) > 1 else 1

print("-------- 1st reconf ----------------")
sa.add_component('server', sa.server)
sa.add_component('client_server', sa.client_server)
sa.connect('server', 'bdd', 'mysql', 'service')
sa.connect('server', 'ip', 'client_server', 'server_ip')
sa.connect('server', 'service', 'client_server', 'service')
for i in range(1, n+1):
    sa.connect('server', 'ip', 'client'+str(i), 'server_ip')
    sa.connect('server', 'service', 'client'+str(i), 'service')
sa.push_b('server', 'deploy')
sa.push_b('client_server', 'install_start')
sa.wait_all()
sa.synchronize()

print("-------- 2nd reconf ----------------")
sa.push_b('server', 'stop')
sa.push_b('client_server', 'stop')
sa.wait_all()
sa.synchronize()

print("-------- 3rd reconf ----------------")
sa.push_b('server', 'deploy')
sa.push_b('client_server', 'install_start')
sa.wait_all()
sa.synchronize()

print("-------- Final reconf ----------------")
sa.push_b('server', 'stop')
sa.push_b('server', 'undeploy')
sa.push_b('client_server', 'stop')
sa.push_b('client_server', 'uninstall')
sa.wait('server')
sa.wait('client_server')
for i in range(1, n+1):
    sa.disconnect('server', 'ip', 'client'+str(i), 'server_ip')
    sa.disconnect('server', 'service', 'client'+str(i), 'service')
sa.disconnect('server', 'ip', 'client_server', 'server_ip')
sa.disconnect('server', 'service', 'client_server', 'service')
sa.del_component('server')
sa.del_component('client')
sa.synchronize()

sa.terminate()

print("---------------END SERVER-----------------")
