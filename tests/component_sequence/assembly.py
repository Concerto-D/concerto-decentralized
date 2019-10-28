import time
from typing import List
from concerto.all import Component, Assembly, DepType
from concerto.utility import empty_transition


class ParallelTransitionsComponent(Component):
    def __init__(self, nb_parallel_transitions: int, sleep_time: float, first: bool = False):
        self._nb_parallel_transitions = nb_parallel_transitions
        assert(nb_parallel_transitions >= 1)
        self._sleep_time = sleep_time
        self._first = first
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
            self.transitions["trans%d" % i] = ('ready', 'end', 'run', 0, self.run_function),

        self.dependencies = {
            "finished": (DepType.PROVIDE, ['end'])
        }
        if not self._first:
            self.dependencies["previous"] = (DepType.USE, ['wait_dep'])

    def run_function(self):
        self.print_color("Waiting for %f seconds" % self._sleep_time)
        time.sleep(self._sleep_time)


class SequenceAssembly(Assembly):
    def __init__(self):
        super().__init__()
        self._current_nb = 0
        self._last_chain_length = 0

    def prepare(self, max_chain_length: int, nb_parallel_transitions: int, sleep_time: float):
        self._current_nb = max_chain_length
        for i in range(max_chain_length):
            self.add_component("comp%d" % i, ParallelTransitionsComponent(nb_parallel_transitions, sleep_time,
                                                                          first=(i == 0)))
        self.synchronize()

    def run(self, chain_length: int):
        self._last_chain_length = chain_length
        if chain_length > self._current_nb:
            raise Exception("Chain length larger than the number of components!")
        beginning_time = time.perf_counter()
        for i in range(chain_length):
            self.push_b("comp%d" % i, "run")
        self.wait("comp%d" % (chain_length-1))
        self.synchronize()
        end_time = time.perf_counter()
        return end_time-beginning_time

    def reset(self):
        for i in range(self._last_chain_length):
            self.push_b("comp%d" % i, "reset")
        self.synchronize()


def run_experiments(list_chain_length: List[int], list_nb_parallel_transitions: List[int], nb_repeats: int,
                    sleep_time: float = 0,
                    verbosity: int = -1, printing: bool = False, print_time: bool = False, dryrun: bool = False):
    import json
    from statistics import mean, stdev
    from typing import Dict, Any
    from concerto.utility import Printer
    assembly = SequenceAssembly()
    assembly.set_verbosity(verbosity)
    assembly.set_print_time(print_time)
    assembly.set_record_gantt(True)
    assembly.set_dryrun(dryrun)

    running_times: Dict[int, Dict[int, Dict[str, Any]]] = dict()

    for nb_trans in list_nb_parallel_transitions:
        running_times[nb_trans] = dict()
        if printing:
            Printer.st_tprint("Preparing the assembly with %d parallel transitions per component" % nb_trans)
        assembly.prepare(max(list_chain_length), nb_trans, sleep_time)
        time.sleep(5)

        for chain_length in list_chain_length:
            if printing:
                Printer.st_tprint("Testing for a chain of length %d..." % chain_length)
            running_times[nb_trans][chain_length] = {
                "runs": []
            }
            for i in range(nb_repeats):
                running_time = assembly.run(chain_length)
                time.sleep(5)
                assembly.reset()
                running_times[nb_trans][chain_length]["runs"].append(running_time)
                if printing:
                    Printer.st_tprint("- attempt %d: %f" % (i, running_time))
            running_times[nb_trans][chain_length]["average"] = mean(running_times[nb_trans][chain_length]["runs"])
            if printing:
                Printer.st_tprint("- average: %f" % running_times[nb_trans][chain_length]["average"])
            if nb_repeats >= 2:
                running_times[nb_trans][chain_length]["std"] = stdev(running_times[nb_trans][chain_length]["runs"])
                if printing:
                    Printer.st_tprint("- std: %f" % running_times[nb_trans][chain_length]["std"])
    with open("times.json", "w") as f:
        json.dump(running_times, f, indent='\t')

    if printing:
        Printer.st_tprint("Terminating assembly")
    assembly.terminate()

    gc = assembly.get_gantt_record()
    gc.export_gnuplot("results.gpl")
    gc.get_gantt_chart().export_json("results.json")


def load_config(conf_file_location):
    from json import load
    with open(conf_file_location, "r") as file:
        conf = load(file)
    return conf


def main():
    config = load_config("concerto_config.json")
    list_chain_length = config['list_chain_length']
    list_nb_parallel_transitions = config['list_nb_parallel_transitions']
    nb_repeats = config['nb_repeats']

    run_experiments(
        list_chain_length, list_nb_parallel_transitions, nb_repeats,
        sleep_time=0,
        verbosity=-1,
        printing=True,
        print_time=True,
    )


if __name__ == '__main__':
    main()
