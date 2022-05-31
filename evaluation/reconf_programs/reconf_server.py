from evaluation.assemblies.server_assembly import ServerAssembly

nb_deps = 2
sc = ServerAssembly(is_asynchrone=False)
sc.set_verbosity(2)


def deploy():
    sc.add_component("server", sc.server)
    for i in range(nb_deps):
        sc.connect("server", f"serviceu_ip{i}", f"dep{i}", "ip")
        sc.connect("server", f"serviceu{i}", f"dep{i}", "service")
    sc.push_b("server", "deploy")
    sc.wait_all()


def update():
    sc.push_b("server", "suspend")
    sc.push_b("server", "deploy")
    sc.wait_all()


deploy()
update()
sc.execute_reconfiguration_program()
