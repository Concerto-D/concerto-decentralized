from evaluation.assemblies.dep_assembly import DepAssembly

sc = DepAssembly(0, is_asynchrone=False)
sc.set_verbosity(2)


def deploy():
    sc.add_component("dep0", sc.dep)
    sc.connect("dep0", "ip", "server", "serviceu_ip0")
    sc.connect("dep0", "service", "server", "serviceu0")
    sc.push_b("dep0", "deploy")
    sc.wait_all()


def update():
    sc.push_b("dep0", "update")
    sc.push_b("dep0", "deploy")
    sc.wait_all()


deploy()
update()
sc.execute_reconfiguration_program()