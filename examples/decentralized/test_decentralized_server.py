from examples.decentralized.servers_assembly import Servers

sa = Servers()
sa.set_verbosity(2)
sa.set_print_time(True)

sa.add_component('server', sa.server)
sa.connect('server', 'ip', 'client1', 'server_ip')
sa.disconnect('server', 'ip', 'client1', 'server_ip')
sa.del_component('server')
sa.synchronize()
sa.terminate()