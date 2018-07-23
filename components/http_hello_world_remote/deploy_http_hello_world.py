# -*- coding: utf-8 -*-

import time
from assembly import Assembly
from components.http_hello_world_remote.hw_client import HW_Client
from components.http_hello_world_remote.hw_server import MAD_HW_Server


# Instanciate the two components:
hw_client = HW_Client()
hw_server = MAD_HW_Server()

# Instanciate the assembly:
assembly = Assembly([
    [hw_server, 'hw_server'],
    [hw_client, 'hw_client']
])

# Connect the two components which leads to finish the deployment:
assembly.connect('hw_server', 'providing_hw', 'hw_client', 'using_hw')
assembly.connect('hw_server', 'hw_ref_out', 'hw_client', 'hw_ref_in')

# Run the deployment while the two components are not connected:
assembly.auto_run()

# Wait the end of the components -- ORDER IS IMPORTANT
hw_client.finish() # WAIT THE CLIENT TO FINISH
hw_server.finish() # DESTROY THE SERVER

