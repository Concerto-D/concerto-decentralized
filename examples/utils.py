import datetime


class Printer():
    def __init__(self, show : bool = True):
        self._show = show
    
    def tprint(self, message : str):
        if self._show:
            self.st_tprint(message)
    
    @staticmethod
    def st_tprint(message : str):
        now = datetime.datetime.now()
        hour = ("%d"%now.hour).rjust(2, '0')
        minute = ("%d"%now.minute).rjust(2, '0')
        second = ("%d"%now.second).rjust(2, '0')
        ms = ("%d"%(now.microsecond/1000)).rjust(3, '0')
        print("[%s:%s:%s:%s] %s"%(hour,minute,second,ms, message))
    
        

