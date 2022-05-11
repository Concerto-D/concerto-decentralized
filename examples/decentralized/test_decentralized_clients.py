from examples.decentralized.clients_assembly import Clients

sc = Clients()
sc.set_verbosity(1)
sc.set_print_time(True)

sc.add_component('client1', sc.client)
sc.connect('client1', 'server_ip', 'server', 'ip')
sc.disconnect('client1', 'server_ip', 'server', 'ip')
sc.del_component('client1')
sc.synchronize()
sc.terminate()