from concerto.component import Component
from concerto.dependency import DepType
from concerto.assembly import Assembly
from concerto.reconfiguration import Reconfiguration
from concerto.meta import ReconfigurationPerfAnalyzer


class HAProxy(Component):
    def create(self):
        self.places = [
            'initiated',
            'deployed'
        ]

        self.transitions = {
            'deploy': ('initiated', 'deployed', 'deploy', 0, self.deploy)
        }

        self.dependencies = {
            'haproxy': (DepType.PROVIDE, ['deployed']),
            'facts': (DepType.USE, ['deploy'])
        }

        self.initial_place = 'initiated'

    def deploy(self):
        pass


a = Assembly()
deploy = Reconfiguration()
deploy.add("proxy", HAProxy)
deploy.push_behavior("proxy", "deploy")
deploy.wait_all()

pa = ReconfigurationPerfAnalyzer(deploy)
g = pa.get_graph()
g.save_as_dot("haproxy.dot")
formula = pa.get_exec_time_formula()
print(formula.to_string(lambda x: '.'.join(x)))
