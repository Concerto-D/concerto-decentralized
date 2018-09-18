import time

class DryRun(object):
    def run(self):
        pass

    def testargs(self, arg1, arg2):
        print("arg1=" + str(arg1) + " and arg2=" + str(arg2))
