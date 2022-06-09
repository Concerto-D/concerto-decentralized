from typing import List

import enoslib as en
import subprocess


def reserve_nodes_for_concerto_d(nb_deps_tot: int, nb_zenoh_routers: int):
    _ = en.init_logging()
    concerto_d_network = en.G5kNetworkConf(type="prod", roles=["base_network"], site="nantes")
    conf = (
        en.G5kConf.from_settings(job_type="allow_classic_ssh", walltime="01:00:00", job_name="concerto-d")
                  .add_network_conf(concerto_d_network)
    )
    conf = conf.add_machine(
        roles=["concerto_d", "server"],
        cluster="econome",
        nodes=1,
        primary_network=concerto_d_network,
    )
    for i in range(nb_deps_tot):
        conf = conf.add_machine(
            roles=["concerto_d", f"dep{i}"],
            cluster="econome",
            nodes=1,
            primary_network=concerto_d_network,
        )
    conf = conf.add_machine(
        roles=["zenoh_routers"],
        cluster="econome",
        nodes=nb_zenoh_routers,
        primary_network=concerto_d_network,
    )
    conf = conf.finalize()

    provider = en.G5k(conf)
    # provider.destroy()
    roles, networks = provider.init()
    return roles, networks
    # return None, None


def deploy_concerto_d(roles_concerto_d: List, configuration_file_path: str):
    # TODO: remove enoslib from requirements when deployed
    with en.actions(roles=roles_concerto_d) as a:
        home_dir = "/home/anomond"
        a.apt(name=["python3", "git"], state="present")
        # a.git(dest=f"{home_dir}/concertonode",
        #       repo="git@gitlab.inria.fr:aomond-imt/concerto-d/concerto-decentralized.git",
        #       key_file=f"{home_dir}/.ssh/gitlab_concerto_d_deploy_key",
        #       accept_hostkey=True)
        a.pip(chdir=f"{home_dir}/concertonode",
              requirements=f"{home_dir}/concertonode/requirements.txt",
              virtualenv=f"{home_dir}/concertonode/venv")
        # a.file(path=f"{home_dir}/concertonode/evaluation/experiment/generated_configurations", state="directory")
        a.copy(src=configuration_file_path, dest=f"{home_dir}/concertonode/{configuration_file_path}")
        print(a.results)


def deploy_zenoh_routers(roles_zenoh_router: List):
    with en.actions(roles=roles_zenoh_router) as a:
        a.apt_repository(repo="deb [trusted=yes] https://download.eclipse.org/zenoh/debian-repo/ /", state="present")
        a.apt(name="zenoh", update_cache="yes")
        print(a.results)


def execute_reconf(role_node, config_file_path: str, duration, dep_num):
    command_args = []
    command_args.append("PYTHONPATH=$PYTHONPATH:$(pwd)")  # What's executed in source_dir.sh
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

    # TODO: temporary until finding a solution to run script on individual hosts


def execute_zenoh_routers(roles_zenoh_router):
    # Command zenohd doesn't give the hand back, but ansible cannot run script in the background
    # TODO: try run_command(background=True)
    for role in roles_zenoh_router:
        subprocess.Popen(["ssh", role.address, "RUST_LOG=debug", "timeout", "500", "zenohd", "--mem-storage='/**'"])

