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
        'uinit': ('waiting', 'initiated', InitShort().run),
        'uconfig': ('initiated', 'configured', ConfigLong().run),
        'ustart': ('configured', 'started', Start().run)
    }

    dependencies = {
        'service': (DepType.USE, ['uconfig', 'ustart'])
    }