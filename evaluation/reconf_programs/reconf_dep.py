import sys

from evaluation.assemblies.dep_assembly import DepAssembly
from evaluation.config import NB_DEPS_TOT

p = int(sys.argv[1])
sc = DepAssembly(p, NB_DEPS_TOT, is_asynchrone=True)
sc.set_verbosity(2)


def deploy():
    sc.add_component(f"dep{p}", sc.dep)
    sc.connect(f"dep{p}", "ip", "server", f"serviceu_ip{p}")
    sc.connect(f"dep{p}", "service", "server", f"serviceu{p}")
    sc.push_b(f"dep{p}", "deploy")
    sc.wait_all()


def update():
    sc.push_b(f"dep{p}", "update")
    sc.push_b(f"dep{p}", "deploy")
    sc.wait_all()


deploy()
update()
sc.execute_reconfiguration_program()
