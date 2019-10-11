from abc import ABCMeta, abstractmethod
from typing import Dict, Tuple, List, Set

from concerto.assembly import Assembly
from concerto.reconfiguration import Reconfiguration
from concerto.madeus.madeus_component import MadeusComponent, _MadeusConcertoComponent


class MadeusAssembly(Assembly):
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
        return self._reconf

    def run(self, auto_synchronize=True):
        self.run_reconfiguration(self.get_concerto_reconfiguration())
        if auto_synchronize:
            self.synchronize()
            self.terminate()
