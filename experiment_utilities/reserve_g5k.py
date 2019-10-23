#!/usr/bin/env python
import yaml


class G5kReservation:
    def _g5k_deploy(self, g5k_config, force_deploy=False):
        from enoslib.infra.enos_g5k.provider import G5k
        from enoslib.infra.enos_g5k.configuration import Configuration
        self._g5k_job = G5k(Configuration.from_dictionnary(g5k_config))
        self._roles, self._networks = self._g5k_job.init(force_deploy=force_deploy)
        # logging.info('Wait 30 seconds for iface to be ready...')
        # time.sleep(30)

    def _allocate(self, conf, force_deployment=False):
        if isinstance(conf, str):
            with open(conf) as f:
                config = yaml.load(f)
        elif isinstance(conf, dict):
            config = conf
        else:
            raise Exception(
                'conf is type {!r} while it should be a yaml file or a dict'.format(type(conf)))

        self._config = config

        # Claim resources on Grid'5000
        if 'g5k' not in config:
            raise Exception("'g5k' key missing in configuration!")
        self._g5k_deploy(config['g5k'], force_deploy=force_deployment)

    @staticmethod
    def _get_ip(g5k_address):
        from subprocess import run, PIPE
        ip = run("dig +short %s" % g5k_address, shell=True, stdout=PIPE).stdout.decode('utf-8').strip(' \r\n')
        return ip

    @staticmethod
    def _get_host_dict(g5k_address):
        return {"address": g5k_address, "ip": G5kReservation._get_ip(g5k_address)}

    def __init__(self, conf, force_deployment=True, destroy=False):
        self._config = None
        self._g5k_job = None
        self._roles = None
        self._networks = None
        self._destroy = destroy
        self._allocate(conf, force_deployment)
        self._alive = True

    def get_roles(self):
        if not self._alive:
            raise Exception("G5k reservation not alive!")
        return self._roles.keys()

    def get_hosts_info(self, role):
        if not self._alive:
            raise Exception("G5k reservation not alive!")
        return [G5kReservation._get_host_dict(host.address) for host in self._roles[role]]

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
