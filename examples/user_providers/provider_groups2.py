from mad import *
from transitions import *


class ProviderGroups2(Component):

    places = [
        'waiting',
        'initiated',
        'configured',
        'started'
    ]

    transitions = {
        'pinit': ('waiting', 'initiated', Init().run),
        'pconfig': ('initiated', 'configured', Config().run),
        'pstart': ('configured', 'started', Start().run)
    }

    dependencies = {
        'service': (DepType.PROVIDE, ['started', 'configured'])
    }