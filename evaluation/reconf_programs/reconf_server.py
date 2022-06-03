from evaluation.assemblies.server_assembly import ServerAssembly
from evaluation.config import NB_DEPS_TOT

sc = ServerAssembly(NB_DEPS_TOT, is_asynchrone=True)
sc.set_verbosity(2)


def deploy():
    sc.add_component("server", sc.server)
    for i in range(NB_DEPS_TOT):
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
