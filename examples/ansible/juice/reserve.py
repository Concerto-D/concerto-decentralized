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
    return env, provider


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
    if not (provider == 'g5k' and 'g5k' in config):
        raise Exception(
            'The provider {!r} is not supported or it lacks a configuration'.format(provider))
    env['provider'] = 'g5k'
    updated_env, g5k_job = g5k_deploy(config['g5k'], force_deploy=force_deployment)
    env.update(updated_env)
    return env, g5k_job

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


CONCERTO_GIT = 'https://gitlab.inria.fr/mchardet/madpp.git'
CONCERTO_DIR_IN_GIT = 'madpp'
EXP_GIT = ''
EXP_DIR_IN_GIT = 'concerto'
ROOT_DIR = '~/concertonode'
PYTHON_FILE = 'galera_assembly.py'

CONCERTO_DIR = '%s/%s'%(ROOT_DIR,CONCERTO_DIR_IN_GIT)
EXP_DIR = '%s/%s'%(ROOT_DIR,EXP_DIR_IN_GIT)


DEFAULT_WORKING_DIRECTORY = '.'
def run_experiment(nb_db_entries, conf, working_directory=DEFAULT_WORKING_DIRECTORY, provider='g5k', force_deployment=True, destroy=False):
    from execo.action import Put, Get, Remote
    from execo.host import Host
    from json import dump
    
    env, g5k_job = allocate(conf, provider, force_deployment)
    database_machines = [get_host_dict(host.address) for host in env['roles']['database']]
    database_add_machines = [get_host_dict(host.address) for host in env['roles']['database_add']]
    master_machine = database_machines[0]
    workers_marchines = database_machines[1:len(database_machines)]
    registry_machine = get_host_dict(env['roles']['registry'][0].address)
    concerto_machine = get_host_dict(env['roles']['concerto'][0].address)
    ceph_use = env['config']['registry']['ceph']
    ceph_mon_host = env['config']['registry']['ceph_mon_host']
    ceph_keyring_path = env['config']['registry']['ceph_keyring']
    ceph_id = env['config']['registry']['ceph_id']
    ceph_rbd = env['config']['registry']['ceph_rbd']
    print("Databases: %s"%str(database_machines))
    print("Registry: %s"%str(registry_machine))
    print("Concerto: %s"%str(concerto_machine))
    print("Ceph: %s"%str(ceph_mon_host))
            #'ceph_id': 'discovery',
            #'ceph': True,
            #'type': 'internal',
            #'ceph_mon_host': ['ceph0.rennes.grid5000.fr', 'ceph1.rennes.grid5000.fr', 'ceph2.rennes.grid5000.fr'],
            #'ceph_keyring': '/home/discovery/.ceph/ceph.client.discovery.keyring',
            #'ceph_rbd': 'discovery_kolla_registry/datas'
    concerto_config = {
        "database_hosts": database_machines,
        "master_host" : master_machine,
        "workers_hosts": workers_marchines,
        "additional_workers_hosts": database_add_machines,
        "registry_host": registry_machine,
        "concerto_host": concerto_machine,
        "ceph": {
            "use": ceph_use,
            "mon_host": ceph_mon_host,
            "keyring_path": ceph_keyring_path,
            "id": ceph_id,
            "rbd": ceph_rbd
        },
        "nb_db_entries": nb_db_entries
    }
    concerto_config_file = open(working_directory+"/concerto_config.json", "w")
    dump(concerto_config, concerto_config_file)
    concerto_config_file.close()
    remote_host = Host(concerto_machine["address"], user="root")
    run_cmd = "mkdir -p %s;"%ROOT_DIR+\
              "cd %s;"%ROOT_DIR+\
              "git clone %s"%CONCERTO_GIT
    print("Executing commands: %s"%run_cmd)
    exp = Remote(
        cmd=run_cmd,
        hosts=[remote_host]
    ).run()
    put = Put(
        hosts=[remote_host],
        local_files=[working_directory+"/concerto_config.json"],
        remote_location= EXP_DIR
    ).run()
    put = Put(
        hosts=[remote_host],
        local_files=["~/.ssh/id_rsa","~/.ssh/id_rsa.pub"],
        remote_location= "~/.ssh"
    ).run()
    run_cmd = "cd %s;"%CONCERTO_DIR+\
              "source source_dir.sh;"+\
              "cd %s;"%ROOT_DIR+\
              "git clone %s;"%EXP_GIT+\
              "cd %s;"%EXP_DIR+\
              "python3 %s >stdout 2>stderr"%PYTHON_FILE
    print("Executing commands: %s"%run_cmd)
    exp = Remote(
        cmd=run_cmd,
        hosts=[remote_host]
    ).run()
    files_to_get_names = ['stdout', 'stderr', 'results.gpl', 'results.json', 'times.json'] # 'data.sql'
    files_to_get = ["%s/%s"%(EXP_DIR,fn) for fn in files_to_get_names]
    Get(
        hosts=[remote_host],
        remote_files=files_to_get,
        local_location=working_directory
    ).run()
    if destroy:
        g5k_job.destroy()
    
    
    
PREFIX_EXPERIMENT = "concerto"
DEFAULT_SWEEPER_NAME = "galera-concerto-sweeper"
DEFAULT_NBS_NODES = [(3,1),(3,5),(3,10),(3,20),(5,0),(10,0),(20,0)]
DEFAULT_NBS_ENTRIES = [1000]
DEFAULT_START_ATTEMPT = 1
DEFAULT_NB_ATTEMPTS = 10
DEFAULT_SWEEPER_DIR = os.path.join(os.getenv('HOME'), DEFAULT_SWEEPER_NAME)
def perform_experiments(start_attempt = DEFAULT_START_ATTEMPT, nb_attempts = DEFAULT_NB_ATTEMPTS, nbs_nodes = DEFAULT_NBS_NODES, nbs_entries = DEFAULT_NBS_ENTRIES, sweeper_dir = DEFAULT_SWEEPER_DIR):
    import copy, yaml, traceback
    from os import makedirs
    from execo_engine.sweep import (ParamSweeper, sweep)
    from pprint import pformat
    
    #CONF = [] #TO GET SOMEHOW
    with open("conf.yaml") as f:
        CONF = yaml.load(f)
    
    sweeper = ParamSweeper(
        sweeper_dir,
        sweeps=sweep({
            'nb_db_nodes': list(nbs_nodes), #, 5, 10],
            'nb_db_entries': list(nbs_entries), #, 0, 10000, 100000],
            'attempt': list(range(start_attempt, start_attempt+nb_attempts))
        }))
    
    logging.info("Using Execo sweeper in directory: %s"%sweeper_dir)
    done_tasks = sweeper.get_done()
    if len(done_tasks) > 0:
        logging.info("Tasks already done:\n%s"%"\n".join("- " + pformat(task) for task in done_tasks))
    
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
            conf['g5k']['resources']['machines'][0]['nodes'] = nb_db_nodes
            xp_name = "%s-nb_db_%d-nb_ent_%d-%d" % (PREFIX_EXPERIMENT, nb_db_nodes, nb_db_entries, attempt)

            # Let's get it started!
            wd = "exp/%s"%xp_name
            makedirs(wd, exist_ok=True)
            with open(wd+'/g5k_config.yaml', 'w') as g5k_config_file:
                yaml.dump(conf, g5k_config_file)
            run_experiment(nb_db_entries, conf, wd, destroy=False)

            # Everything works well, mark combination as done
            sweeper.done(combination)
            logging.info("End of combination %s" % pformat(combination))

        except Exception as e:
          # Oh no, something goes wrong! Mark combination as cancel for
          # a later retry
            logging.error("Combination %s Failed with message \"%s\". Full exception message:\n%s" % (pformat(combination), e, traceback.format_exc()))
            sweeper.cancel(combination)

        finally:
            pass
        
        

if __name__ == '__main__':
    #Testing
    logging.basicConfig(level=logging.DEBUG)
    perform_experiments()
    #run_experiment(0, "conf.yaml", '.')
