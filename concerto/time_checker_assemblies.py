import json
import time

from concerto.debug_logger import log_once

node_num_assembly_name = ["server", "dep0", "dep1", "dep2", "dep3", "dep4", "dep5", "dep6", "dep7", "dep8", "dep9", "dep10", "dep11"]


class TimeCheckerAssemblies:
    def __init__(self, uptimes_nodes_file_path):
        self.start_time = None
        self.min_uptime = None
        with open(uptimes_nodes_file_path) as f:
            self.uptime_nodes = json.load(f)

    def set_start_time(self):
        self.start_time = time.time()

    def set_min_uptime(self, min_uptime):
        self.min_uptime = min_uptime

    def is_node_awake_now(self, component_name, round_reconf):
        log_once.debug(f"Checking if node for assembly {component_name} is up")
        uptime, duration = self.uptime_nodes[node_num_assembly_name.index(component_name)][round_reconf]
        seconds_elapsed = self.get_seconds_elapsed()
        if uptime <= seconds_elapsed <= (uptime + duration):
            log_once.debug(f"Node {component_name} is up. Current time: {int(seconds_elapsed)}. Times awakening: {uptime} - {uptime + duration}")
            return True
        log_once.debug(f"Node {component_name} is not up. Current time: {int(seconds_elapsed)}. Times awakening: {uptime} - {uptime + duration}")
        return False

    def get_seconds_elapsed(self):
        return time.time() - self.start_time + self.min_uptime
