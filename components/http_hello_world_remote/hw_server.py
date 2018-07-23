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

import sys, time, os
from subprocess import Popen
from http.server import BaseHTTPRequestHandler, HTTPServer

#############################################
### HTTP SERVER
#############################################

class HW_Server(object):
    MYCOLOR = "\x1b[43m" # YELLOW
    RESET = "\x1b[0m" # RESET
    def __init__(self, ip, port, wait_file):
        self.ip = ip
        self.port = port
        self.wait_file = wait_file

    def run(self):
        print(self.MYCOLOR+'[HW_Server] Starting httpd...'+self.RESET)
        server_address = (self.ip, int(self.port))
        self.httpd = HTTPServer(server_address, MyHandler)
        print(self.MYCOLOR+'[HW_Server] Creating wait file: '+self.wait_file+self.RESET)
        open(self.wait_file, 'a').close() # CREATE FILE TO SAY I'M READY
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

#############################################
# MAD WRAPPER
#############################################

class MAD_HW_Server(object):
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
        print(self.MYCOLOR+"[MAD_HW_Server] (1/3) Installlation."+self.RESET)

    def func_configure(self):
        print(self.MYCOLOR+"[MAD_HW_Server] (2/3) Configuration."+self.RESET)

    def func_run(self):
        print(self.MYCOLOR+"[MAD_HW_Server] (3/3) Launching process..."+self.RESET)
        self.wait_file = "/tmp/MAD_HW_SERVER_"+str(os.getpid())
        try:
            self.p = Popen(["python3", "./components/http_hello_world_remote/hw_server.py","localhost", "3306", self.wait_file])
        except:
            print(self.MYCOLOR+"[MAD+HW_Server] (3/3) Error -- was not able to launch the process"+self.RESET)
            os.abort()
        print(self.MYCOLOR+"[MAD_HW_Server] (3/3) Launching process ... waiting (wait_file: "+self.wait_file+")"+self.RESET)
        while not os.path.exists(self.wait_file):
            print(self.MYCOLOR+"[MAD_HW_Server] (3/3) Launching process ... waiting...looping"+self.RESET)
            time.sleep(0.1)
        print(self.MYCOLOR+"[MAD_HW_Server] (3/3) Running..."+self.RESET)

    # Two methods are defined to implement the 'provide' ports:
    def hw_ref_out(self):
        # The method 'provider_data' returns data if the related place is
        # activated:
        return self.data if self.net.get_place('initiated').state else None

    def providing_hw(self):
        # The method 'provider_serv' returns the state of its related place:
        return self.net.get_place('running').state

    def finish(self):
        print(self.MYCOLOR+"[MAD_HW_Server] finish..."+self.RESET)
        self.p.terminate()
        os.remove(self.wait_file)
        print(self.MYCOLOR+"[MAD_HW_Server] finish...done"+self.RESET)

if __name__ == "__main__":
    # execute only if run as a script
    if len(sys.argv)==4:
           hw = HW_Server(sys.argv[1], sys.argv[2], sys.argv[3])
           hw.run()
