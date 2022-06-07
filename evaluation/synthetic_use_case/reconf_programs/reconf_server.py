import sys

from evaluation.synthetic_use_case.assemblies.server_assembly import ServerAssembly
import yaml

config_file_path = sys.argv[1]
with open(config_file_path, "r") as f:
    config_dict = yaml.safe_load(f)

sc = ServerAssembly(config_dict, is_asynchrone=False)
sc.set_verbosity(2)


def deploy():
    sc.add_component("server", sc.server)
    for i in range(config_dict['nb_deps_tot']):
        sc.connect("server", f"serviceu_ip{i}", f"dep{i}", "ip")
        sc.connect("server", f"serviceu{i}", f"dep{i}", "service")
    sc.push_b("server", "deploy")
    sc.wait_all()


def update():
    sc.push_b("server", "suspend")
    sc.wait_all(wait_for_refusing_provide=True)
    sc.push_b("server", "deploy")
    sc.wait_all()


deploy()
update()
sc.execute_reconfiguration_program()
