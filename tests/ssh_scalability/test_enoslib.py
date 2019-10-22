import yaml

from enoslib.infra.enos_g5k.provider import G5k
from enoslib.infra.enos_g5k.configuration import Configuration


with open("conf.yaml") as f:
    conf = yaml.load(f)
conf_g5k = conf['g5k']
provider = G5k(Configuration.from_dictionnary(conf_g5k))
roles, networks = provider.init()
print(roles)
