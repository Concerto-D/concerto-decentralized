#!/usr/bin/env python
import logging
import time
import yaml


class G5kReservation:
    @staticmethod
    def _g5k_deploy(g5k_config, force_deploy=False, **kwargs):
        from enoslib.infra.enos_g5k.provider import G5k
        from enoslib.infra.enos_g5k.configuration import Configuration
        provider = G5k(Configuration.from_dictionnary(g5k_config))
        roles, networks = provider.init(force_deploy=force_deploy)
        env = {'roles': roles, 'networks': networks}
        logging.info('Wait 30 seconds for iface to be ready...')
        time.sleep(30)
        return env, provider

    @staticmethod
    def _allocate(conf, provider='g5k', force_deployment=False):
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
        updated_env, g5k_job = G5kReservation._g5k_deploy(config['g5k'], force_deploy=force_deployment)
        env.update(updated_env)
        return env, g5k_job

    @staticmethod
    def _get_ip(g5k_address):
        from subprocess import run, PIPE
        ip = run("dig +short %s" % g5k_address, shell=True, stdout=PIPE).stdout.decode('utf-8').strip(' \r\n')

        return ip

    @staticmethod
    def _get_host_dict(g5k_address):
        return {"address": g5k_address, "ip": G5kReservation._get_ip(g5k_address)}

    def __init__(self, conf, force_deployment=True, destroy=False):
        from execo.action import Put, Get, Remote
        from execo.host import Host
        from json import dump

        self._env, self._g5k_job = G5kReservation._allocate(conf, 'g5k', force_deployment)
        self._destroy = destroy
        self._alive = True

    def get_roles(self):
        if not self._alive:
            raise Exception("G5k reservation not alive!")
        return self._env['roles'].keys()

    def get_hosts_info(self, role):
        if not self._alive:
            raise Exception("G5k reservation not alive!")
        return [G5kReservation._get_host_dict(host.address) for host in self._env['roles'][role]]

    def terminate(self):
        if not self._alive:
            raise Exception("G5k reservation not alive!")
        if self._destroy:
            self._g5k_job.destroy()
        self._alive = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._alive:
            self.terminate()
