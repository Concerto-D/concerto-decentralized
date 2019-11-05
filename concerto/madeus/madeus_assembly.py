from abc import ABCMeta, abstractmethod
from typing import Dict, Tuple, List

from concerto.assembly import Assembly
from concerto.reconfiguration import Reconfiguration
from concerto.madeus.madeus_component import MadeusComponent, _MadeusConcertoComponent


class MadeusAssembly(Assembly, metaclass=ABCMeta):
    @abstractmethod
    def create(self):
        pass

    def __init__(self, dryrun: bool = False, gantt_chart: bool = False, verbosity: int = 0, print_time: bool = False):
        super().__init__()
        self.components: Dict[str, MadeusComponent] = dict()
        self.dependencies: List[Tuple[str, str, str, str]] = []
        
        self.create()
        
        self.set_dryrun(dryrun)
        self.set_record_gantt(gantt_chart)
        self.set_verbosity(verbosity)
        self.set_print_time(print_time)

        self._reconf = Reconfiguration()
        
        for component_name, component in self.components.items():
            self._reconf.add(component_name, _MadeusConcertoComponent, component)
        for component_name, component in self.components.items():
            if len(component.transitions) > 0:
                self._reconf.push_behavior(component_name, _MadeusConcertoComponent.AUTO_BEHAVIOR)
        
        for (c1, p1, c2, p2) in self.dependencies:
            self._reconf.connect(c1, p1, c2, p2)
        self._reconf.wait_all()

    def get_concerto_reconfiguration(self):
        """
        Returns the Concerto reconfiguration object generated by the Madeus abstraction layer.
        :return: a Concerto reconfiguration.
        """
        return self._reconf

    def run(self, auto_synchronize: bool = True):
        """
        Runs the Concerto deployment.
        :param auto_synchronize: If True (default), will block until the deployment is over and return the
        deployment execution time. If False, will return the start time of the deployment and return immediately.
        :return: Deployment time if auto_synchronize is true (default), start time of the deployment (as given by
        time.perf_counter) if auto_synchronize is False.
        """
        from time import perf_counter
        reconf = self.get_concerto_reconfiguration()
        start_time = perf_counter()
        self.run_reconfiguration(reconf)
        if auto_synchronize:
            self.synchronize()
            end_time = perf_counter()
            self.terminate()
            return end_time-start_time
        else:
            return start_time

    def run_timeout(self, max_time: int):
        """
        Runs the Concerto deployment with an integer timeout.
        :param max_time: Maximum deployment time.
        :return: A tuple (finished, debug_info, running_time) where finished is true iff the timeout wasn't reached,
        debug_info contains the debug info (string) if the timeout was reached and None otherwise, and running_time
        is a float containing the running time.
        """
        from time import perf_counter
        start_time = self.run(auto_synchronize=False)
        finished, debug_info = self.synchronize_timeout(max_time)
        end_time = perf_counter()
        return finished, debug_info, end_time-start_time
