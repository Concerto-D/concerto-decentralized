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


def deploy(conf, provider='g5k', force_deployment=False, env=None, **kwargs):
    config = {}

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
        
    print("  Roles:")
    print(env['roles'])
    print("  Networks:")
    print(env['networks'])
    print("  Config:")
    print(env)
    

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
            deploy(conf, db, xp_name)

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
