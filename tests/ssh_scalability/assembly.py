import time
from concerto.all import Component, Assembly
from concerto.utility import empty_transition


class SSHCaller(Component):
    def __init__(self, remote_address, sleep_time):
        from experiment_utilities.remote_host import RemoteHost
        self._remote_host = RemoteHost(remote_address)
        self._sleep_time = sleep_time
        super().__init__()

    def create(self):
        self.places = [
            'beginning',
            'end'
        ]

        self.transitions = {
            'call': ('beginning', 'end', 'call', 0, self.call_function),
            'reset': ('end', 'beginning', 'reset', 0, empty_transition)
        }

        self.initial_place = "beginning"

    def call_function(self):
        self.print_color("Waiting for %f seconds" % self._sleep_time)
        self.print_color(str(self._remote_host))
        self._remote_host.run("sleep %f" % self._sleep_time)


class SSHAssembly(Assembly):
    def __init__(self):
        super().__init__()
        self._current_nb = 0
        self._last_nb_calls = 0

    def prepare(self, remote_addresses, sleep_time):
        self._current_nb = len(remote_addresses)
        for i, address in enumerate(remote_addresses):
            self.add_component("caller%d" % i, SSHCaller(address["ip"], sleep_time))
        self.synchronize()

    def call(self, nb_calls):
        self._last_nb_calls = nb_calls
        if nb_calls > self._current_nb:
            raise Exception("Number of calls larger than the number of components!")
        beginning_time = time.perf_counter()
        for i in range(nb_calls):
            self.push_b("caller%d" % i, "call")
        self.wait_all()
        self.synchronize()
        end_time = time.perf_counter()
        return end_time-beginning_time

    def reset(self):
        for i in range(self._last_nb_calls):
            self.push_b("caller%d" % i, "reset")
        self.synchronize()


def run_experiments(remote_hosts, list_nb_remote_ssh, nb_repeats,
                    verbosity: int = 0, printing: bool = False, print_time: bool = False, dryrun: bool = False):
    import json
    from statistics import mean, stdev
    from typing import Dict, Any
    from concerto.utility import Printer
    assembly = SSHAssembly()
    assembly.set_verbosity(verbosity)
    assembly.set_print_time(print_time)
    assembly.set_record_gantt(True)
    assembly.set_dryrun(dryrun)

    if printing:
        Printer.st_tprint("Preparing the assembly")
    assembly.prepare(remote_hosts, 10)
    time.sleep(5)

    running_times: Dict[int, Dict[str, Any]] = dict()

    for nb_remote_ssh in list_nb_remote_ssh:
        if printing:
            Printer.st_tprint("Testing for %d remote SSH connections..." % nb_remote_ssh)
        running_times[nb_remote_ssh] = {
            "runs": []
        }
        for i in range(nb_repeats):
            running_time = assembly.call(nb_remote_ssh)
            time.sleep(5)
            assembly.reset()
            running_times[nb_remote_ssh]["runs"].append(running_time)
            if printing:
                Printer.st_tprint("- attempt %d: %f" % (i, running_time))
        running_times[nb_remote_ssh]["average"] = mean(running_times[nb_remote_ssh]["runs"])
        if printing:
            Printer.st_tprint("- average: %f" % running_times[nb_remote_ssh]["average"])
        if nb_repeats >= 2:
            running_times[nb_remote_ssh]["std"] = stdev(running_times[nb_remote_ssh]["runs"])
            if printing:
                Printer.st_tprint("- std: %f" % running_times[nb_remote_ssh]["std"])
    with open("times.json", "w") as f:
        json.dump(running_times, f)

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
    remote_hosts = config['remote_hosts']
    list_nb_remote_ssh = config['list_nb_remote_ssh']
    nb_repeats = config['nb_repeats']

    run_experiments(
        remote_hosts, list_nb_remote_ssh, nb_repeats,
        verbosity=1,
        printing=True,
        print_time=True,
    )


if __name__ == '__main__':
    main()
