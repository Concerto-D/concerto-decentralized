#!/usr/bin/env python
import logging

from experiment_utilities.remote_host import RemoteHost
from experiment_utilities.reserve_g5k import G5kReservation

CONCERTO_GIT = 'https://gitlab.inria.fr/mchardet/madpp.git'
CONCERTO_DIR_IN_GIT = 'madpp'
EXP_DIR_IN_GIT = CONCERTO_DIR_IN_GIT + '/tests/ssh_scalability'
ROOT_DIR = '~/concertonode'
PYTHON_FILE = 'assembly.py'

CONCERTO_DIR = '%s/%s' % (ROOT_DIR, CONCERTO_DIR_IN_GIT)
EXP_DIR = '%s/%s' % (ROOT_DIR, EXP_DIR_IN_GIT)

DEFAULT_WORKING_DIRECTORY = '.'


def run_experiment(list_nb_remote_ssh, nb_repeats, conf, working_directory=DEFAULT_WORKING_DIRECTORY,
                   force_deployment=True, destroy=False):
    from json import dump

    with G5kReservation(conf, force_deployment, destroy) as g5k:
        remote_machines = g5k.get_hosts_info(role='remote')
        concerto_machine = g5k.get_hosts_info(role='concerto')[0]
        print("Remote: %s" % str(remote_machines))
        print("Concerto: %s" % str(concerto_machine))
        concerto_config = {
            "remote_hosts": remote_machines,
            "concerto_host": concerto_machine,
            "list_nb_remote_ssh": list_nb_remote_ssh,
            "nb_repeats": nb_repeats
        }
        with open(working_directory + "/concerto_config.json", "w") as concerto_config_file:
            dump(concerto_config, concerto_config_file)

        with g5k.ansible_to("concerto") as ansible_to_concerto:
            ansible_to_concerto.apt(name=["python3"], state="present")
            ansible_to_concerto.pip(name=["enoslib"], executable="pip3")

        with RemoteHost(concerto_machine["address"], remote_user="root") as concerto_host:
            run_cmd = "mkdir -p %s;" % ROOT_DIR + \
                      "cd %s;" % ROOT_DIR + \
                      "git clone %s;" % CONCERTO_GIT
            print("Executing commands: %s" % run_cmd)
            concerto_host.run(run_cmd)
            concerto_host.send_files(
                local_files=[working_directory + "/concerto_config.json"],
                remote_location=EXP_DIR
            )
            concerto_host.send_files(
                local_files=["~/.ssh/id_rsa", "~/.ssh/id_rsa.pub"],
                remote_location="~/.ssh"
            )
            run_cmd = "cd %s;" % CONCERTO_DIR + \
                      "source source_dir.sh;" + \
                      "cd %s;" % EXP_DIR + \
                      "timeout -k 10s 30m python3 %s >stdout 2>stderr" % PYTHON_FILE
            print("Executing commands: %s" % run_cmd)
            concerto_host.run(run_cmd)
            files_to_get_names = ['stdout', 'stderr', 'results.gpl', 'results.json', 'times.json']
            files_to_get = ["%s/%s" % (EXP_DIR, fn) for fn in files_to_get_names]
            concerto_host.get_files(
                remote_files=files_to_get,
                local_location=working_directory
            )


def perform_experiment(list_nb_remote_ssh, nb_repeats):
    import yaml
    from os import makedirs

    with open("conf.yaml") as f:
        conf = yaml.load(f)

    conf['g5k']['resources']['machines'][0]['nodes'] = max(list_nb_remote_ssh)

    wd = "exp"
    makedirs(wd, exist_ok=True)
    with open(wd + '/g5k_config.yaml', 'w') as g5k_config_file:
        yaml.dump(conf, g5k_config_file)

    run_experiment(list_nb_remote_ssh, nb_repeats, conf, wd)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    perform_experiment([1, 5, 10, 15, 20], 5)
