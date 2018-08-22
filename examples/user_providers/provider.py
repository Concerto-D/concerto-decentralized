from mad import *
from transitions import *


class Provider(Component):

    places = [
        'waiting',
        'initiated',
        'configured',
        'started'
    ]

    transitions = {
        'init': (Init(), 'waiting', 'initiated'),
        'config': (Config(), 'initiated', 'configured'),
        'start': (Start(), 'configured', 'started')
    }

    dependencies = {
        'ip': (DepType.DATA_PROVIDE, ['configured']),
        'service': (DepType.PROVIDE, ['started'])
    }