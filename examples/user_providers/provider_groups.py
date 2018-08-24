from mad import *
from transitions import *


class ProviderGroups(Component):

    places = [
        'waiting',
        'initiated',
        'configured1',
        'configured2',
        'started'
    ]

    transitions = {
        'init': ('waiting', 'initiated', Init().run),
        'config1': ('initiated', 'configured1', Config().run),
        'config2': ('configured1', 'configured2', Config().run),
        'start': ('configured2', 'started', Start().run)
    }

    dependencies = {
        'ip': (DepType.DATA_PROVIDE, ['configured1']),
        'service': (DepType.PROVIDE, ['configured1', 'configured2'])
    }