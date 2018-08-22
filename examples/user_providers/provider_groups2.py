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
        'pinit': (Init(), 'waiting', 'initiated'),
        'pconfig': (Config(), 'initiated', 'configured'),
        'pstart': (Start(), 'configured', 'started')
    }

    dependencies = {
        'service': (DepType.PROVIDE, ['started', 'configured'])
    }