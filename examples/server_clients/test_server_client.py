#!/usr/bin/python3
import queue

from concerto.all import *
from concerto.utility import Printer
import time, datetime

from server_client_assembly import ServerClient

# Creating an instance of the ServerClient assembly and setting some parameters
sca = ServerClient()
sca.set_record_gantt(True)
sca.set_verbosity(1)
sca.set_print_time(True)

Printer.st_tprint("Main: deploying the assembly")
sca.deploy() # First reconfiguration

Printer.st_tprint("Main: waiting a little before reconfiguring")
time.sleep(3)

sca.suspend() # Second reconfiguration

Printer.st_tprint("Main: waiting a little before restarting")
time.sleep(5)

sca.restart() # Third reconfiguration

sca.terminate() # Terminating the assembly (shutting down the execution thread)

# Exporting the Gantt chart in Gnuplot and JSON formats
Printer.st_tprint("Main: exporting Gantt chart in Gnuplot and JSON formats")
gc : GanttRecord = sca.get_gantt_record()
gc.export_gnuplot("results.gpl")
gc.export_json("results.json")
