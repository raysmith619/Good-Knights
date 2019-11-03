# timeout.py    23-Oct-2019
""" Timeout from stackoverflow.com
"""
from threading import Thread
import functools
from matplotlib.dates import seconds

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

if __name__ == "__main__":
    import time
    
    def long_fun(timein=None):
        """ test function that takes timein sec
        :timein: int number of seconds
        """
        if timein is None:
            timein = 8
        print("timein({:d}) start".format(timein))
        for _ in range(timein):
            print("timein sleep({:d})".format(_))
            time.sleep(1)
        print("timein end")
        
    time_limit = 3    
    timed_long_fun = timeout(timeout=time_limit)(long_fun(8))
    
    try:
        timed_long_fun()
    except:
        print("Timeout")
        