# comp_stats.py
"""
An attempt to organize statistics gathering / reporting 
"""
from select_trace import SlTrace
from select_error import SelectError

class CompStats:
    def __init__(self):
        self.ncount = 0          # Number of instances
        self.time_dur = None
        self.npath = None       # Number of paths found
        self.nmove = None       # Number of moves, including retries
        self.nbackup = None     # Number of backups (excluding complete tour path backups)
        self.track_level = None # minimum stack tracking
        self.ntrack_ntie = None
        self.ntie = None
    
    def report_heading(self, desc):
        SlTrace.lg(f"{desc:14s} {'count':5s} {'time':>6s} {'paths':5s}"
                   f" {'moves':6s} {'level':5s} {'nttrk':>6s} {'ntie':>6s}")

    def report_line(self, desc=""):
        if self.ncount < 1:
            return                          # Suppress line if no entries
        
        SlTrace.lg(f"{desc:14s} {self.ncount:5d} {self.time_dur:6.3f} {self.npath:5d}"
                    f" {self.nmove:6.0f} {self.track_level:5d}"
                    f" {self.ntrack_ntie:6d} {self.ntie:6d}")
               
    def add(self, time_dur=None, npath=None, nbackup=None, nmove=None, track_level=None, count=True):
        self.time_dur = time_dur
        self.npath = npath
        self.nbackup = nbackup
        self.nmove = nmove
        self.track_level = track_level
        if count:
            self.ncount += 1

class AvgCompStats(CompStats):
    def add(self, time_dur=None, npath=None, nbackup=None, nmove=None, track_level=None, ntrack_ntie=None, ntie=None, count=True):
        if self.time_dur is None:
            self.time_dur = time_dur
        else:
            self.time_dur += time_dur
        if self.npath is None:
            self.npath = npath
        else:
            self.npath += npath
        if self.nbackup is None:  
            self.nbackup = nbackup
        else:
            self.nbackup += nbackup
        if self.nmove is None:  
            self.nmove = nmove
        else:
            self.nmove += nmove
        if self.track_level is None:
            self.track_level = track_level
        else:
            self.track_level += track_level
        if self.ntrack_ntie is None:
            self.ntrack_ntie = ntrack_ntie
        else:
            self.ntrack_ntie += ntrack_ntie
        if self.ntie is None:
            self.ntie = ntie
        else:
            self.ntie += ntie
            
        if count:
            self.ncount += 1


    def report_line(self, desc=""):
        if self.ncount < 1:
            return                          # Suppress line if no entries
        
        time_dur = self.time_dur/self.ncount
        npath = self.npath/self.ncount
        nmove = self.nmove/self.ncount
        track_level = self.track_level/self.ncount
        ntrack_ntie = self.ntrack_ntie/self.ncount
        ntie = self.ntie/self.ncount
        SlTrace.lg(f"{desc:14s} {self.ncount:5d} {time_dur:6.3f}"
                   f" {npath:5.0f} {nmove:6.0f} {track_level:5.0f}"
                   f" {ntrack_ntie:6.1f} {ntie:6.1f} ")
            
class MaxCompStats(CompStats):
    def add(self, time_dur=None, npath=None, nbackup=None, nmove=None, track_level=None, ntrack_ntie=None, ntie=None, count=True):
        if self.time_dur is None or time_dur > self.time_dur:
            self.time_dur = time_dur
        if self.npath is None or npath > self.npath:
            self.npath = npath
        if self.nbackup is None or nbackup > self.nbackup:  
            self.nbackup = nbackup
        if self.nmove is None or nmove > self.nmove:  
            self.nmove = nmove
        if self.track_level is None or track_level > self.track_level:
            self.track_level = track_level
        if self.track_level is None or track_level > self.track_level:
            self.track_level = track_level
        if self.ntrack_ntie is None or ntrack_ntie > self.ntrack_ntie:
            self.ntrack_ntie = ntrack_ntie
        if self.ntie is None or ntie > self.ntie:
            self.ntie = ntie
            
        if count:
            self.ncount += 1

class MinCompStats(CompStats):
    def add(self, time_dur=None, npath=None, nbackup=None, nmove=None, track_level=None, ntrack_ntie=None, ntie=None, count=True):
        if self.time_dur is None or time_dur < self.time_dur:
            self.time_dur = time_dur
        if self.npath is None or npath < self.npath:
            self.npath = npath
        if self.nbackup is None or nbackup < self.nbackup:  
            self.nbackup = nbackup
        if self.nmove is None or nmove < self.nmove:  
            self.nmove = nmove
        if self.track_level is None or track_level < self.track_level:
            self.track_level = track_level
        if self.ntrack_ntie is None or ntrack_ntie < self.ntrack_ntie:
            self.ntrack_ntie = ntrack_ntie
        if self.ntie is None or ntie < self.ntie:
            self.ntie = ntie
            
        if count:
            self.ncount += 1

class ResultCompStats(CompStats):
    """ Comp stats for result class
    """
    def __init__(self):
        self.avg = AvgCompStats()
        self.min = MinCompStats()
        self.max = MaxCompStats()
        
    def add(self, *args, **kwargs):
        self.avg.add(*args, **kwargs)
        self.min.add(*args, **kwargs)
        self.max.add(*args, **kwargs)
