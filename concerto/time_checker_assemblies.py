import json
import time

from concerto.debug_logger import log_once

node_num_assembly_name = ["server", "dep0", "dep1", "dep2", "dep3", "dep4", "dep5", "dep6", "dep7", "dep8", "dep9", "dep10", "dep11"]


class TimeCheckerAssemblies:
    def __init__(self, uptimes_nodes_file_path):
        self.start_time = time.time()
        with open(uptimes_nodes_file_path) as f:
            self.uptime_nodes = json.load(f)

    def is_node_awake_now(self, component_name):
        log_once.debug(f"Checking if node for assembly {component_name} is up")
        uptimes_node = self.uptime_nodes[node_num_assembly_name.index(component_name)]
        seconds_elapsed = self.get_seconds_elapsed()
        for uptime, duration in uptimes_node:
            if uptime <= seconds_elapsed <= (uptime + duration):
                log_once.debug(f"Node {component_name} is up. Current time: {seconds_elapsed}. Times awakening: {uptime} - {uptime + duration}")
                return True
        log_once.debug(f"Node {component_name} is not up. Current time: {seconds_elapsed}")
        return False

    def get_seconds_elapsed(self):
        return time.time() - self.start_time
