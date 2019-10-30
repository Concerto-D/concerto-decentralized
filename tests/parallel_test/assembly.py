import time
from typing import List, Optional
from concerto.all import Component, Assembly, DepType
from concerto.utility import empty_transition


class ParallelTransitionsComponent(Component):
    def __init__(self,  nb_parallel_transitions: int,
                 sleep_time: float = 0, remote_address: Optional[str] = None):
        self._nb_parallel_transitions = nb_parallel_transitions
        assert(nb_parallel_transitions >= 1)
        self._sleep_time = sleep_time
        self._remote_host = None
        if remote_address:
            from experiment_utilities.remote_host import RemoteHost
            self._remote_host = RemoteHost(remote_address)
        super().__init__()

    def create(self):
        self.places = [
            'beginning',
            'ready',
            'end'
        ]

        self.initial_place = "beginning"

        self.transitions = {
            'wait_dep': ('beginning', 'ready', 'run', 0, empty_transition),
            'reset': ('end', 'beginning', 'reset', 0, empty_transition)
        }
        for i in range(self._nb_parallel_transitions):
            self.transitions["trans%d" % i] = 'ready', 'end', 'run', 0, self.run_function,

        self.dependencies = {
            "service": (DepType.PROVIDE, ['end']),
            "use_service": (DepType.USE, ['wait_dep'])
        }

    def run_function(self):
        if self._remote_host:
            self._remote_host.run("sleep %f" % self._sleep_time)
        elif self._sleep_time > 0:
            time.sleep(self._sleep_time)


class ProviderComponent(Component):
    def create(self):
        self.places = [
            'beginning',
            'end'
        ]

        self.initial_place = "beginning"

        self.transitions = {
            'provide': ('beginning', 'end', 'provide', 0, empty_transition),
            'reset': ('end', 'beginning', 'reset', 0, empty_transition),
        }

        self.dependencies = {
            "service": (DepType.PROVIDE, ['end'])
        }


class ParallelAssembly(Assembly):
    def __init__(self):
        super().__init__()
        self._current_nb_active_components = 0
        self._last_nb_active_components = 0

    def prepare(self, nb_components: int, nb_parallel_transitions: int,
                remote_addresses: Optional[List[str]] = None, sleep_time: float = 0):
        if remote_addresses:
            assert(len(remote_addresses) == nb_components)
        self._current_nb_active_components = nb_components

        self.add_component("provider", ProviderComponent())
        for i in range(nb_components):
            remote_address = remote_addresses[i] if remote_addresses else None
            self.add_component("user%d" % i, ParallelTransitionsComponent(nb_parallel_transitions,
                                                                          sleep_time,
                                                                          remote_address))
            self.connect("provider", "service", "user%d" % i, "use_service")
        self.synchronize()

    def run(self, nb_active_components):
        self._last_nb_active_components = nb_active_components
        if nb_active_components > self._current_nb_active_components:
            raise Exception("Number of calls larger than the number of components!")
        beginning_time = time.perf_counter()
        for i in range(nb_active_components):
            self.push_b("user%d" % i, "run")
        self.push_b("provider", "provide")
        self.wait_all()
        self.synchronize()
        end_time = time.perf_counter()
        return end_time-beginning_time

    def reset(self):
        for i in range(self._last_nb_active_components):
            self.push_b("user%d" % i, "reset")
        self.push_b("provider", "reset")
        self.wait_all()
        self.synchronize()


def run_experiments(list_nb_components: List[int], list_nb_parallel_transitions: List[int], nb_repeats: int,
                    remote_hosts: List[str] = (), sleep_time: float = 0,
                    verbosity: int = -1, printing: bool = False, print_time: bool = False, dryrun: bool = False):
    import json
    from statistics import mean, stdev
    from typing import Dict, Any
    from concerto.utility import Printer

    running_times: Dict[int, Dict[int, Dict[str, Any]]] = dict()

    for nb_trans in list_nb_parallel_transitions:
        assembly = ParallelAssembly()
        assembly.set_verbosity(verbosity)
        assembly.set_print_time(print_time)
        assembly.set_record_gantt(True)
        assembly.set_dryrun(dryrun)

        running_times[nb_trans] = dict()
        if printing:
            Printer.st_tprint("Preparing the assembly with %d parallel transitions per component" % nb_trans)
        assembly.prepare(max(list_nb_components), nb_trans, remote_hosts, sleep_time)
        time.sleep(1)

        for nb_components in list_nb_components:
            if printing:
                Printer.st_tprint("Testing for %d components..." % nb_components)
            running_times[nb_trans][nb_components] = {
                "runs": []
            }
            for i in range(nb_repeats):
                running_time = assembly.run(nb_components)
                time.sleep(2)
                assembly.reset()
                running_times[nb_trans][nb_components]["runs"].append(running_time)
                if printing:
                    Printer.st_tprint("- attempt %d: %f" % (i, running_time))
            running_times[nb_trans][nb_components]["average"] = mean(running_times[nb_trans][nb_components]["runs"])
            if printing:
                Printer.st_tprint("- average: %f" % running_times[nb_trans][nb_components]["average"])
            if nb_repeats >= 2:
                running_times[nb_trans][nb_components]["std"] = stdev(running_times[nb_trans][nb_components]["runs"])
                if printing:
                    Printer.st_tprint("- std: %f" % running_times[nb_trans][nb_components]["std"])

        if printing:
            Printer.st_tprint("Terminating assembly")
        assembly.terminate()

        gc = assembly.get_gantt_record()
        gc.export_gnuplot("results_%d_transitions.gpl" % nb_trans)
        gc.get_gantt_chart().export_json("results_%d_transitions.json" % nb_trans)

    with open("times.json", "w") as f:
        json.dump(running_times, f, indent='\t')


def load_config(conf_file_location):
    from json import load
    with open(conf_file_location, "r") as file:
        conf = load(file)
    return conf


def main():
    config = load_config("concerto_config.json")
    list_nb_components = config['list_nb_components']
    list_nb_parallel_transitions = config['list_nb_parallel_transitions']
    nb_repeats = config['nb_repeats']
    remote_hosts = config['remote_hosts']
    sleep_time = config['sleep_time']

    run_experiments(
        list_nb_components,
        list_nb_parallel_transitions,
        nb_repeats,
        remote_hosts,
        verbosity=-1,
        printing=True,
        print_time=True,
        sleep_time=sleep_time
    )


if __name__ == '__main__':
    main()
