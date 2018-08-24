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
        'init': ('waiting', 'initiated', Init().run),
        'config': ('initiated', 'configured', Config().run),
        'start': ('configured', 'started', Start().run)
    }

    dependencies = {
        'ip': (DepType.DATA_PROVIDE, ['configured']),
        'service': (DepType.PROVIDE, ['started'])
    }