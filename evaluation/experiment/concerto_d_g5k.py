from typing import List

import enoslib as en
from enoslib.infra.enos_g5k.g5k_api_utils import get_cluster_site


provider = None


def reserve_nodes_for_concerto_d(nb_concerto_d_nodes: int, nb_zenoh_routers: int, cluster: str):
    """
    TODO: voir pour les restriction des ressources (pour approcher des ressources d'une OU (raspberry ou autre))
    TODO: Etre attentif au walltime lors du lancement des expériences
    """
    _ = en.init_logging()
    site = get_cluster_site(cluster)
    concerto_d_network = en.G5kNetworkConf(type="prod", roles=["base_network"], site=site)
    conf = (
        en.G5kConf.from_settings(job_type="allow_classic_ssh", walltime="03:00:00", job_name="concerto-d")
                  .add_network_conf(concerto_d_network)
    )
    conf = conf.add_machine(
        roles=["concerto_d", "server"],
        cluster=cluster,
        nodes=1,
        primary_network=concerto_d_network,
    )
    for i in range(nb_concerto_d_nodes - 1):
        conf = conf.add_machine(
            roles=["concerto_d", f"dep{i}"],
            cluster=cluster,
            nodes=1,
            primary_network=concerto_d_network,
        )
    conf = conf.add_machine(
        roles=["zenoh_routers"],
        cluster=cluster,
        nodes=nb_zenoh_routers,
        primary_network=concerto_d_network,
    )
    conf = conf.finalize()

    global provider
    provider = en.G5k(conf)
    roles, networks = provider.init()
    return roles, networks


def install_apt_deps(roles_concerto_d: List):
    with en.actions(roles=roles_concerto_d) as a:
        a.apt(name=["python3", "git"], state="present")
        print(a.results)


def deploy_concerto_d(roles_concerto_d: List, configuration_file: str):
    """
    Homedir is shared between site frontend and nodes, so this can be done only once per site
    """
    with en.actions(roles=roles_concerto_d) as a:
        home_dir = "/home/anomond"
        a.copy(src="~/.ssh/gitlab_concerto_d_deploy_key", dest=f"{home_dir}/.ssh/gitlab_concerto_d_deploy_key")
        a.git(dest=f"{home_dir}/concertonode",
              repo="git@gitlab.inria.fr:aomond-imt/concerto-d/concerto-decentralized.git",
              key_file=f"{home_dir}/.ssh/gitlab_concerto_d_deploy_key",
              accept_hostkey=True)
        a.pip(chdir=f"{home_dir}/concertonode",
              requirements=f"{home_dir}/concertonode/requirements.txt",
              virtualenv=f"{home_dir}/concertonode/venv")
        a.file(path=f"{home_dir}/concertonode/evaluation/experiment/generated_configurations", state="directory")
        # Reset reprise_configs dir
        a.file(path=f"{home_dir}/concertonode/reprise_configs", state="absent")
        a.file(path=f"{home_dir}/concertonode/reprise_configs", state="directory")
        # Reset logs dir
        a.file(path=f"{home_dir}/concertonode/logs", state="absent")
        a.file(path=f"{home_dir}/concertonode/logs", state="directory")
        a.file(path=f"{home_dir}/concertonode/archives_reprises", state="directory")
        a.copy(src=configuration_file, dest=f"{home_dir}/concertonode/{configuration_file}")
        print(a.results)


def deploy_zenoh_routers(roles_zenoh_router: List):
    with en.actions(roles=roles_zenoh_router) as a:
        a.apt_repository(repo="deb [trusted=yes] https://download.eclipse.org/zenoh/debian-repo/ /", state="present")
        a.apt(name="zenoh", update_cache="yes")
        print(a.results)


def execute_reconf(role_node, config_file_path: str, duration, dep_num):
    command_args = []
    command_args.append("PYTHONPATH=$PYTHONPATH:$(pwd)")  # Set PYTHONPATH (equivalent of source source_dir.sh)
    command_args.append("venv/bin/python3")               # Execute inside the python virtualenv
    assembly_name = "server" if dep_num is None else "dep"
    command_args.append(f"evaluation/synthetic_use_case/reconf_programs/reconf_{assembly_name}.py")  # The reconf program to execute
    if dep_num is not None:
        command_args.append(str(dep_num))  # If it's a dependency
    command_args.append(config_file_path)  # The path of the config file that the remote process will search to
    command_args.append(str(duration))     # The awakening time of the program, it goes to sleep afterwards (it exits)

    command_str = " ".join(command_args)
    home_dir = "/home/anomond"
    with en.actions(roles=role_node) as a:
        a.shell(chdir=f"{home_dir}/concertonode", command=command_str)


def execute_zenoh_routers(roles_zenoh_router, timeout):
    print(f"launch zenoh routers with {timeout} timeout")
    en.run_command(" ".join(["RUST_LOG=debug", "timeout", str(timeout), "zenohd", "--mem-storage='/**'"]), roles=roles_zenoh_router, background=True)


def get_logs_from_concerto_d_node(roles_sites, logs_assembly_names: List[str]):
    """
    Need one role per site to gather the logs
    """
    home_dir = "/home/anomond"
    with en.actions(roles=roles_sites) as a:
        for assembly_name in logs_assembly_names:
            a.fetch(src=f"{home_dir}/concertonode/logs/logs_{assembly_name}.txt", dest=f"remote_logs/logs_{assembly_name}.txt")