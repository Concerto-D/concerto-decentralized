import sys

from evaluation.synthetic_use_case.assemblies.dep_assembly import DepAssembly
import yaml

config_file_path = sys.argv[2]
with open(config_file_path, "r") as f:
    config_dict = yaml.safe_load(f)

p = int(sys.argv[1])
sc = DepAssembly(p, config_dict, is_asynchrone=True)
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
