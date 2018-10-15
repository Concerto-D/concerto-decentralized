from mad import *
import time


class UserRead(Component):

    def create(self):
        self.places = [
            'waiting',
            'initiated',
            'configured',
            'started'
        ]

        self.transitions = {
            'init': ('waiting', 'initiated', 'install', self.init),
            'config': ('initiated', 'configured', 'install', self.config),
            'start': ('configured', 'started', 'install', self.start)
        }

        self.dependencies = {
            'ipprov': (DepType.DATA_USE, ['init']),
            'service': (DepType.USE, ['config', 'start'])
        }
        
        self.initial_place = 'waiting'

    def init(self):
        time.sleep(10)

    def config(self):
        time.sleep(5)
        ip = self.read('ipprov')
        print("get IP : " + ip)

    def start(self):
        time.sleep(5)
