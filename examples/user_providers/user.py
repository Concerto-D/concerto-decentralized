from mad import *
from transitions import *


class User(Component):

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
        'ipprov': (DepType.DATA_USE, ['init']),
        'service': (DepType.USE, ['config', 'start'])
    }