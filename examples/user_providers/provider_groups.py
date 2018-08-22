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
        'init': (Init(), 'waiting', 'initiated'),
        'config1': (Config(), 'initiated', 'configured1'),
        'config2': (Config(), 'configured1', 'configured2'),
        'start': (Start(), 'configured2', 'started')
    }

    dependencies = {
        'ip': (DepType.DATA_PROVIDE, ['configured1']),
        'service': (DepType.PROVIDE, ['configured1', 'configured2'])
    }