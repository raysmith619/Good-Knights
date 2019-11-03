# alarm_windows.py    21Oct2019  crs
"""
Alarm for windows from Stackoverflow.com
Because signal.alarm is not available for windows
"""
import os
import time
import threading

class Alarm (threading.Thread):
    def __init__ (self, timeout, handler=None):
        threading.Thread.__init__ (self)
        self.timeout = timeout
        self.handler = handler
        self.setDaemon (True)

    def run (self):
        time.sleep (self.timeout)
        if self.handler is not None:
            self.handler()
        else:
            self.self_handler()
            time.sleep(10)
            os._exit (1)
        os._exit(2)
        
    def self_handler(self):
        print("Timeout")


if __name__ == "__main__":
    def handler():
        print("Our timeout")
        raise Exception
    
    task_time = 8
    alarm_time = 3
    try:
        alarm = Alarm(alarm_time, handler)
        alarm.start()
        time.sleep(task_time)
        del alarm
        print('yup')
    except Exception as exc:
        print("exception {}".format(exc))
        del alarm
    try:
        alarm = Alarm()
        print("alarm_time: {:d} seconds".format(alarm_time))
        print("longer wait {:d} sec".format(task_time))    
        alarm = Alarm(alarm_time)
        alarm.start ()
        for _ in range(task_time):
            print("sleep 1 second")
            time.sleep(1)
    except exception as exec:
        print("timeout via except {}".format(exc))
    del alarm
    print("End of test")