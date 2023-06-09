import sys

from examples.decentralized.clients_python_assembly import ClientsPython

n = sys.argv[1] if len(sys.argv) > 1 else "1"
sc = ClientsPython(n, sleep_when_blocked=False)
sc.set_verbosity(2)
sc.set_print_time(True)

# print("-------- 1st reconf ----------------")
sc.add_component('client'+n, sc.client)
sc.add_component('python_install', sc.python_install)
sc.connect('client'+n, 'server_ip', 'server', 'ip')
sc.connect('client'+n, 'service', 'server', 'service')
sc.connect('client'+n, 'python', 'python_install', 'installation')
sc.push_b('client'+n, 'install_start')
sc.push_b('python_install', 'install')
sc.wait_all()
# sc.synchronize()

# print("-------- 2nd reconf ----------------")
sc.push_b('client'+n, 'stop')
sc.wait_all()
# sc.synchronize()

# print("-------- 3rd reconf ----------------")
sc.push_b('client'+n, 'install_start')
sc.wait_all()
# sc.synchronize()

# print("-------- Final reconf ----------------")
sc.push_b('client'+n, 'stop')
sc.push_b('client'+n, 'uninstall')
sc.push_b('python_install', 'uninstall')
sc.wait('server')
sc.wait('client_server')
sc.wait_all()
sc.disconnect('client'+n, 'server_ip', 'server', 'ip')
sc.disconnect('client'+n, 'service', 'server', 'service')
sc.disconnect('client'+n, 'python', 'python_install', 'installation')
sc.del_component('client'+n)
sc.del_component('python_install')
# sc.synchronize()
sc.execute_reconfiguration_program()
# sc.terminate()

print(f"---------------END CLIENT {n}-----------------")
