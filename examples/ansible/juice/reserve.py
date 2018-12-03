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


def deploy(conf, provider='g5k', force_deployment=False):
    from execo.action import Put, Get, Remote
    from execo.host import Host
    from json import dump
    
    env = allocate(conf, provider, force_deployment)
    database_machines = [host.address for host in env['roles']['database']]
    master_machine = database_machines[0]
    workers_marchines = database_machines[1..len(database_machines)]
    registry_machine = env['roles']['registry'][0]
    madpp_machine = env['roles']['madpp'][0]
    ceph_mon_host = env['config']['registry']['ceph_mon_host']
    madpp_config = {
        "database_hosts": database_machines,
        "master_host" : master_machine,
        "workers_hosts": workers_marchines,
        "registry_host": registry_machine,
        "madpp_host": madpp_machine,
        "ceph_mon_host": ceph_mon_host
    }
    madpp_config_file = open("madpp_config.json", "w")
    dump(madpp_config, madpp_config_file)
    madpp_config_file.close()
    remote_host = Host(madpp_machine, user="root")
    put = Put(
        hosts=[remote_host],
        local_file="madpp_config.json",
        remote_location= "."
    ).run()
    run_cmd = "git clone https://gitlab.inria.fr/mchardet/madpp.git" +\
              "cd madpp;"+\
              "source source_dir.sh;"+\
              "cd examples/ansible/juice/;python3.6 galera_assembly.py >stdout 2>stderr"
    exp = Remote(
        cmd=run_cmd,
        hosts=[remote_host]
    ).run()
    Get(
        hosts=[remote_host],
        remote_files=['stdout', 'stderr'],
        local_location='.'
    ).run()
    
    
    

SWEEPER_DIR = os.path.join(os.getenv('HOME'), 'juice-sweeper')
def experiments():
    import copy
    from execo_engine.sweep import (ParamSweeper, sweep)
    from pprint import pformat
    
    CONF = [] #TO GET SOMEHOW
    
    sweeper = ParamSweeper(
        SWEEPER_DIR,
        sweeps=sweep({
              'param1': []
            , 'param2': []
            , 'param3': []
        }))

    while sweeper.get_remaining():
        combination = sweeper.get_next()
        logging.info("Treating combination %s" % pformat(combination))

        try:
            # Setup parameters
            conf = copy.deepcopy(CONF)  # Make a deepcopy so we can run
                                        # multiple sweeps in parallels
            conf['g5k']['resources']['machines'][0]['nodes'] = combination['db-nodes']
            conf['tc']['constraints'][0]['delay'] = "%sms" % combination['delay']
            db = combination['db']
            xp_name = "%s-%s-%s" % (db, combination['db-nodes'], combination['delay'])

            # Let's get it started hun!
            allocate(conf, db, xp_name)

            # Everything works well, mark combination as done
            sweeper.done(combination)
            logging.info("End of combination %s" % pformat(combination))

        except Exception as e:
          # Oh no, something goes wrong! Mark combination as cancel for
          # a later retry
            logging.error("Combination %s Failed with message %s" % (pformat(combination), e))
            sweeper.cancel(combination)

        finally:
            pass
        
        

if __name__ == '__main__':
    #Testing
    deploy("conf.yaml")