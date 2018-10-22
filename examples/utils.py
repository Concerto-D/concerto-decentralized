import datetime

printing = True

def tprint_show(show : bool):
    global printing
    printing = show

def tprint(message : str):
    if printing:
        now = datetime.datetime.now()
        print("[%2d:%2d:%2d:%3d] %s"%(now.hour,now.minute, now.second, now.microsecond/1000, message))
