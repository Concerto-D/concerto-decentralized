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
        'init': (Init(), 'waiting', 'initiated'),
        'config': (Config(), 'initiated', 'configured'),
        'start': (Start(), 'configured', 'started')
    }

    dependencies = {
        'ipprov': (DepType.DATA_USE, ['init']),
        'service': (DepType.USE, ['config', 'start'])
    }