from mad import *
from transitions import *


class UserGroups(Component):

    places = [
        'waiting',
        'initiated',
        'configured',
        'started'
    ]

    transitions = {
        'uinit': (InitShort(), 'waiting', 'initiated'),
        'uconfig': (ConfigLong(), 'initiated', 'configured'),
        'ustart': (Start(), 'configured', 'started')
    }

    dependencies = {
        'service': (DepType.USE, ['uconfig', 'ustart'])
    }