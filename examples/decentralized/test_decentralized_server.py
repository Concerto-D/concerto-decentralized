from examples.decentralized.servers_assembly import Servers

sa = Servers()
sa.set_verbosity(2)
sa.set_print_time(True)

sa.add_component('server', sa.server)
sa.connect('client1', 'server_ip', 'server', 'ip')
sa.synchronize()
sa.terminate()