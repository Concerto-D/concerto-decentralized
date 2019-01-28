#!/usr/bin/env python
import os, yaml, logging, time

from enoslib.task import enostask, _save_env

def g5k_deploy(g5k_config, force_deploy=False, **kwargs):
    from enoslib.infra.enos_g5k.provider import G5k
    provider = G5k(g5k_config)
    roles, networks = provider.init(force_deploy=force_deploy)
    env = {}
    env['roles'] = roles
    env['networks'] = networks
    logging.info('Wait 30 seconds for iface to be ready...')
    time.sleep(30)
    return env


def allocate(conf, provider='g5k', force_deployment=False):
    config = {}
    env = {}

    if isinstance(conf, str):
        # Get the config object from a yaml file
        with open(conf) as f:
            config = yaml.load(f)
    elif isinstance(conf, dict):
        # Get the config object from a dict
        config = conf
    else:
        # Data format error
        raise Exception(
            'conf is type {!r} while it should be a yaml file or a dict'.format(type(conf)))

    env['db'] = config.get('database', 'mariadb')
    env['monitoring'] = config.get('monitoring', False)
    env['config'] = config

    # Claim resources on Grid'5000
    if provider == 'g5k' and 'g5k' in config:
        env['provider'] = 'g5k'
        updated_env = g5k_deploy(config['g5k'], force_deploy=force_deployment)
        env.update(updated_env)
    else:
        raise Exception(
            'The provider {!r} is not supported or it lacks a configuration'.format(provider))
    return env

#{
    #'roles': {
        #'database': [Host(ecotype - 47. nantes.grid5000.fr, address = ecotype - 47. nantes.grid5000.fr), Host(ecotype - 45. nantes.grid5000.fr, address = ecotype - 45. nantes.grid5000.fr), Host(ecotype - 19. nantes.grid5000.fr, address = ecotype - 19. nantes.grid5000.fr)],
        #'registry': [Host(ecotype - 48. nantes.grid5000.fr, address = ecotype - 48. nantes.grid5000.fr)]
    #},
    #'config': {
        #'database': 'mariadb',
        #'registry': {
            #'ceph_id': 'discovery',
            #'ceph': True,
            #'type': 'internal',
            #'ceph_mon_host': ['ceph0.rennes.grid5000.fr', 'ceph1.rennes.grid5000.fr', 'ceph2.rennes.grid5000.fr'],
            #'ceph_keyring': '/home/discovery/.ceph/ceph.client.discovery.keyring',
            #'ceph_rbd': 'discovery_kolla_registry/datas'
        #},
        #'monitoring': False,
        #'g5k': {
            #'dhcp': True,
            #'job_name': 'juice-tests',
            #'env_name': 'debian9-x64-nfs',
            #'walltime': '02:00:00',
            #'resources': {
                #'machines': [{
                    #'roles': ['database'],
                    #'nodes': 3,
                    #'primary_network': 'n1',
                    #'cluster': 'ecotype',
                    #'secondary_networks': []
                #}, {
                    #'roles': ['registry'],
                    #'nodes': 1,
                    #'primary_network': 'n1',
                    #'cluster': 'ecotype',
                    #'secondary_networks': []
                #}],
                #'networks': [{
                    #'roles': ['control_network', 'database_network'],
                    #'id': 'n1',
                    #'site': 'nantes',
                    #'type': 'prod'
                #}]
            #}
        #}
    #},
    #'db': 'mariadb',
    #'provider': 'g5k',
    #'networks': [{
        #'roles': ['control_network', 'database_network'],
        #'gateway': '172.16.207.254',
        #'cidr': '172.16.192.0/20',
        #'dns': '131.254.203.235'
    #}],
    #'monitoring': False
#}


def get_ip(g5k_address):
    from subprocess import run, PIPE
    ip = run("dig +short %s"%g5k_address, shell=True, stdout=PIPE).stdout.decode('utf-8').strip(' \r\n')
    
    return ip

def get_host_dict(g5k_address):
    return {"address": g5k_address, "ip": get_ip(g5k_address)}


def deploy(conf, working_directory='.', provider='g5k', force_deployment=False):
    from execo.action import Put, Get, Remote
    from execo.host import Host
    from json import dump
    
    env = allocate(conf, provider, force_deployment)
    database_machines = [get_host_dict(host.address) for host in env['roles']['database']]
    master_machine = database_machines[0]
    workers_marchines = database_machines[1:len(database_machines)]
    registry_machine = get_host_dict(env['roles']['registry'][0].address)
    madpp_machine = get_host_dict(env['roles']['madpp'][0].address)
    ceph_use = env['config']['registry']['ceph']
    ceph_mon_host = env['config']['registry']['ceph_mon_host']
    ceph_keyring_path = env['config']['registry']['ceph_keyring']
    ceph_id = env['config']['registry']['ceph_id']
    ceph_rbd = env['config']['registry']['ceph_rbd']
    print("Databases: %s"%str(database_machines))
    print("Registry: %s"%str(registry_machine))
    print("Madpp: %s"%str(madpp_machine))
    print("Ceph: %s"%str(ceph_mon_host))
            #'ceph_id': 'discovery',
            #'ceph': True,
            #'type': 'internal',
            #'ceph_mon_host': ['ceph0.rennes.grid5000.fr', 'ceph1.rennes.grid5000.fr', 'ceph2.rennes.grid5000.fr'],
            #'ceph_keyring': '/home/discovery/.ceph/ceph.client.discovery.keyring',
            #'ceph_rbd': 'discovery_kolla_registry/datas'
    madpp_config = {
        "database_hosts": database_machines,
        "master_host" : master_machine,
        "workers_hosts": workers_marchines,
        "registry_host": registry_machine,
        "madpp_host": madpp_machine,
        "ceph": {
            "use": ceph_use,
            "mon_host": ceph_mon_host,
            "keyring_path": ceph_keyring_path,
            "id": ceph_id,
            "rbd": ceph_rbd
        }
    }
    madpp_config_file = open(working_directory+"/madpp_config.json", "w")
    dump(madpp_config, madpp_config_file)
    madpp_config_file.close()
    remote_host = Host(madpp_machine["address"], user="root")
    run_cmd = "mkdir -p madppnode;"+\
              "cd madppnode;"+\
              "rm -r madpp;"+\
              "git clone https://gitlab.inria.fr/mchardet/madpp.git"
    print("Executing commands: %s"%run_cmd)
    exp = Remote(
        cmd=run_cmd,
        hosts=[remote_host]
    ).run()
    put = Put(
        hosts=[remote_host],
        local_files=[working_directory+"/madpp_config.json"],
        remote_location= "madppnode/madpp/examples/ansible/juice"
    ).run()
    put = Put(
        hosts=[remote_host],
        local_files=["~/.ssh/id_rsa","~/.ssh/id_rsa.pub"],
        remote_location= "~/.ssh"
    ).run()
    run_cmd = "cd madppnode/madpp;"+\
              "source source_dir.sh;"+\
              "cd examples/ansible/juice/;"+\
              "python3 galera_assembly.py >stdout 2>stderr"
    print("Executing commands: %s"%run_cmd)
    exp = Remote(
        cmd=run_cmd,
        hosts=[remote_host]
    ).run()
    Get(
        hosts=[remote_host],
        remote_files=['madppnode/madpp/examples/ansible/juice/stdout', 'madppnode/madpp/examples/ansible/juice/stderr', 'madppnode/madpp/examples/ansible/juice/results.gpl', 'madppnode/madpp/examples/ansible/juice/results.json'],
        local_location=working_directory
    ).run()
    
    
    

SWEEPER_DIR = os.path.join(os.getenv('HOME'), 'juice-sweeper')
def experiments():
    import copy, yaml
    from os import makedirs
    from execo_engine.sweep import (ParamSweeper, sweep)
    from pprint import pformat
    
    #CONF = [] #TO GET SOMEHOW
    CONF = yaml.load("conf.yaml")
    
    sweeper = ParamSweeper(
        SWEEPER_DIR,
        sweeps=sweep({
            'nb_db_nodes': [3, 5, 10],
            'nb_db_entries': [0, 1000, 10000, 100000],
            'attempt': [1]
        }))

    while sweeper.get_remaining():
        combination = sweeper.get_next()
        logging.info("Treating combination %s" % pformat(combination))

        try:
            # Setup parameters
            conf = copy.deepcopy(CONF)  # Make a deepcopy so we can run
                                        # multiple sweeps in parallels
            nb_db_nodes = combination['nb_db_nodes']
            nb_db_entries = combination['nb_db_entries']
            attempt = combination['attempt']
            print("Test")
            print(conf)
            print("Test")
            conf['g5k']['resources']['machines'][0]['nodes'] = nb_db_nodes
            xp_name = "nb_db_%d-nb_ent_%d-%d" % (nb_db_nodes, nb_db_entries, attempt)

            # Let's get it started hun!
            wd = "exp/%s"%xp_name
            makedirs(wd)
            with open(wd+'/g5k_config.yaml', 'w') as g5k_config_file:
                yaml.dump(conf, g5k_config_file)
            deploy(conf,wd)

            # Everything works well, mark combination as done
            sweeper.done(combination)
            logging.info("End of combination %s" % pformat(combination))

        except Exception as e:
          # Oh no, something goes wrong! Mark combination as cancel for
          # a later retry
            logging.error("Combination %s Failed with message %s" % (pformat(combination), e))
            sweeper.cancel(combination)
            raise e

        finally:
            pass
        
        

if __name__ == '__main__':
    #Testing
    logging.basicConfig(level=logging.DEBUG)
    experiments()
    #deploy("conf.yaml", '.')
