# -*- coding: utf-8 -*-
""" This component is part of the use/provide toy example which depicts
how MAD components can exchange information. This component is the HW_Server
counterpart, whose places, transitions and ports are depicted as follow:

+--------------------------------------------------------------+
|                                                              |
|                     HW_Server Component                      |
|                                                              |
|                 +-------------------------+                  |
|                 |                         |  providing_hw    |
|                 |        +-------+        |   (provide)      |
|                 |        |running| +----------->             |
|                 |        +---+---+        |                  |
|                 |            ^            |                  |
|                 |            |            |                  |
|                 |           +-+ run       |                  |
|                 |            |            |                  |
|                 |       +----+-----+      |                  |
|                 |       |configured|      |                  |
|                 |       +----+-----+      |                  |
|                 |            ^            |                  |
|                 |            |            |                  |
|                 |           +-+ configure |                  |
|                 |            |            |                  |
|                 |       +----+----+       |                  |
|                 |       |installed|       |                  |
|                 |       +----+----+       |                  |
|                 |            ^            |                  |
|                 |            |            |                  |
|                 |           +-+ install   |                  |
|                 |            |            |  hw_ref_out      |
|                 |  +---------+---------+  |   (provide)      |
|                 |  |initiated (initial)| +----->             |
|                 |  +-------------------+  |                  |
|                 |                         |                  |
|                 +-------------------------+                  |
|                                                              |
+--------------------------------------------------------------+


"""

from mad import PetriNet

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class HW_Server(object):
    """ Define a new component of type HW_Server."""

    MYCOLOR = "\x1b[33m" # YELLOW
    RESET = "\x1b[0m" # RESET
    
    # The provider contains some data that must be used by another component:
    data = {
        'provider_ip': 'localhost',
        'provider_port': '3306'
    }

    # Define the different places of the component:
    places = ['initiated', 'installed', 'configured', 'running']

    # Define the different transitions of the component:
    transitions = [
            {'name': 'install', 'source': 'initiated', 'dest': 'installed'},
            {'name': 'configure', 'source': 'installed', 'dest': 'configured'},
            {'name': 'run', 'source': 'configured', 'dest': 'running'}
    ]

    # Define the different ports - both of them are 'provide' ports, attached
    # to different places:
    ports = [
            {'name': 'hw_ref_out', 'inside_link': 'initiated'},
            {'name': 'providing_hw', 'inside_link': 'running'}
    ]

    def __init__(self, step=False):

        # Initiate our component as a PetriNet, with its places, transitions,
        # ports and its initial place:
        self.net = PetriNet(self, self.places, self.transitions, self.ports,
                initial='initiated')

    # Transition callbacks are defined here:
    def func_install(self):
        print(self.MYCOLOR+"[HW_Server] (1/3) Installlation."+self.RESET)

    def func_configure(self):
        print(self.MYCOLOR+"[HW_Server] (2/3) Configuration."+self.RESET)

    def func_run(self):
        print(self.MYCOLOR+"[HW_Server] (3/3) Running: launching thread"+self.RESET)
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()
        print(self.MYCOLOR+"[HW_Server] (3/3) Running: done"+self.RESET)

    # Two methods are defined to implement the 'provide' ports:
    def hw_ref_out(self):
        # The method 'provider_data' returns data if the related place is
        # activated:
        return self.data if self.net.get_place('initiated').state else None

    def providing_hw(self):
        # The method 'provider_serv' returns the state of its related place:
        return self.net.get_place('running').state

    #############################################
    ### HTTP SERVER

    def loop(self):
        print(self.MYCOLOR+'[HW_Server] Starting httpd...'+self.RESET)
        server_address = (self.data['provider_ip'], int(self.data['provider_port']))
        print(server_address)
        self.httpd = HTTPServer(server_address, MyHandler)
        self.httpd.serve_forever()        

    def finish(self):
        print(self.MYCOLOR+"[HW_Server] Shuting down the http server..."+self.RESET)
        self.httpd.shutdown()
        print(self.MYCOLOR+"[HW_Server] Shutdown."+self.RESET)

class MyHandler(BaseHTTPRequestHandler):
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(bytes("Hello, the world!", "utf-8"))

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write(bytes("<html><body><h1>POST!</h1></body></html>", "utf-8"))
    
