from evaluation.assemblies.dep_assembly import DepAssembly

sc = DepAssembly(1, is_asynchrone=False)
sc.set_verbosity(2)


def deploy():
    sc.add_component("dep1", sc.dep)
    sc.connect("dep1", "ip", "server", "serviceu_ip1")
    sc.connect("dep1", "service", "server", "serviceu1")
    sc.push_b("dep1", "deploy")
    sc.wait_all()


def update():
    sc.push_b("dep1", "update")
    sc.push_b("dep1", "deploy")
    sc.wait_all()


deploy()
update()
sc.execute_reconfiguration_program()
