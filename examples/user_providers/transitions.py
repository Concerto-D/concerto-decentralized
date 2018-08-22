import time

class Init(object):
    def run(self):
        time.sleep(10)

class InitShort(object):
    def run(self):
        time.sleep(2)

class Config(object):
    def run(self):
        time.sleep(5)

class ConfigLong(object):
    def run(self):
        time.sleep(12)

class Start(object):
    def run(self):
        time.sleep(5)
