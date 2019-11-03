# good_knights.py    crs    26-Sept-2019    Author
"""
Create a knight turing problem solver
Problem: Find the path(s) a knight can travel on a chess board to reach every square
without traversing any square more than once.  Are ther more than one such paths?
Given a specific starting square is the path unique.  What are the starting square(s)?

Develop data structures for:
    1. piece (a night for now,but may increase)
    2. move, uniquely specify a move
    3. board, uniquely specifying the board state, efficiently facilitating
     rapid and deep analysis, e.g. look ahead, backtracking

Develop board display to provide current state, lookahead moves

    Unobstructed Knight Moves

        +---+---+---+---+---+
        |   |(2)|   |(3)|   |
        +---+---+---+---+---+
        |(1)|   |   |   |(4)|
        +---+---+---+---+---+
        |   |   | N |   |   |
        +---+---+---+---+---+
        |(8)|   |   |   |(5)|
        +---+---+---+---+---+
        |   |(7)|   |(6)|   |
        +---+---+---+---+---+


   
"""
import argparse
import sys
from datetime import datetime
from tkinter import *

from select_window import SelectWindow
from select_trace import SlTrace
from select_error import SelectError
from chess_board import ChessBoard
from chess_board_display import ChessBoardDisplay
from knights_paths import KnightsPaths

loc2desc = ChessBoard.loc2desc 
loc2tuple = ChessBoard.loc2tuple 
path_desc = ChessBoard.path_desc
display_path = ChessBoardDisplay.display_path

closed_tours = True         # True => only accept closed tours
display_complete = True    # True => display each complete(cover all) path
display_path_board = False  # True => display path board each path
track_all_path = False
###track_all_path = True               # TFD
max_look_ahead = 5          # Maximum look-ahead for best move testing    
nrows = ncols = 8
###nrows = ncols = 6       # TFD
###nrows = ncols = 4       # TFD

start_ri = 0
###start_ri = 2        # TFD
end_ri = nrows-1
start_ci = 0
###start_ci = 3        # TFD
end_ci = end_ri
###end_ri = 0          # TFD to limit printout
sqno = 0
all_paths = True
all_paths = False       #TFD
time_out = .5              # Time limit for path calculation
trace = "stack_grow,complete_paths"
trace = "stack_grow"
trace = "back_off_trace"
###trace = "stack_grow,back_off_trace,no_more_moves"
trace = ""
###trace = "set_piece"

def pgm_exit():
    quit()
    SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
    SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
    sys.exit(0)

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def arrange_cmd():
    SlTrace.lg("arrange_cmd TBD")
    
def pause_cmd():
    """ Run / continue game
    """
    SlTrace.lg("pause_cmd TBD")


def run_cmd():
    """ Run / continue game
    """
    SlTrace.lg("run_cmd TBD")
    
parser = argparse.ArgumentParser()

parser.add_argument('--closed_tours', type=str2bool, dest='closed_tours', default=closed_tours)
parser.add_argument('--display_complete', type=str2bool, dest='display_complete', default=display_complete)
parser.add_argument('--display_path_board', type=str2bool, dest='display_path_board', default=display_path_board)
parser.add_argument('--max_look_ahead=', type=int, dest='max_look_ahead', default=max_look_ahead)
parser.add_argument('--ncols=', type=int, dest='ncols', default=ncols)
parser.add_argument('--nrows=', type=int, dest='nrows', default=nrows)
parser.add_argument('--time_out=', type=int, dest='time_out', default=time_out)
parser.add_argument('--trace', dest='trace', default=trace)
args = parser.parse_args()             # or die "Illegal options"
SlTrace.lg("args: %s\n" % args)
closed_tours = args.closed_tours
display_complete = args.display_complete
display_path_board = args.display_path_board
max_look_ahead = args.max_look_ahead
ncols = args.ncols
nrows= args.nrows
time_out = args.time_out
trace = args.trace
if trace:
    SlTrace.setFlags(trace)

SlTrace.setLogStdTs(True)
mw = Tk()                   # To force GUI to main thread
app = SelectWindow(mw,
                title="Good Knights",
                pgmExit=pgm_exit,
                arrange = arrange_cmd,
                )
app.add_menu_command("Run", run_cmd)
app.add_menu_command("Pause", pause_cmd)

###cB = ChessBoard(mw=mw, nrows=nrows, ncols=ncols, is_displayed=False)

n_complete_paths = 0
n_having_complete_path = 0
n_with_no_complete_path = 0
n_with_multiple_complete_paths = 0
longest_path = []
longest_path_start = None
n_closed_tour = 0
max_success_time = None     # Maximum successful duration
total_success_time = 0      # Total successful times        

class CompStats:
    def __init__(self):
        self.ncount = 0          # Number of instances
        self.time_dur = None
        self.npath = None      # Number of paths found
        self.nbackup = None    # Number of backups (excluding complete tour path backups)
        self.track_level = None # minimum stack tracking
        self.ntrack_ntie = None
        self.ntie = None
    
    def report_heading(self, desc):
        SlTrace.lg(f"{desc:14s} {'count':5s} {'time':>5s} {'paths':5s} {'backup':6s} {'level':5s} {'nttrk':>6s} {'ntie':>6s}")

    def report_line(self, desc=""):
        SlTrace.lg(f"{desc:14s} {self.ncount:5d} {self.time_dur:5.3f} {self.npath:5d} {self.nbackup:6d} {self.track_level:5d} {self.ntrack_ntie:6d} {self.ntie:6d}")
               
    def add(self, time_dur=None, npath=None, nbackup=None, track_level=None, count=True):
        self.time_dur = time_dur
        self.npath = npath
        self.nbackup = nbackup
        self.track_level = track_level
        if count:
            self.ncount += 1

class AvgCompStats(CompStats):
    def add(self, time_dur=None, npath=None, nbackup=None, track_level=None, ntrack_ntie=None, ntie=None, count=True):
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
        nbackup = self.nbackup/self.ncount
        track_level = self.track_level/self.ncount
        ntrack_ntie = self.ntrack_ntie/self.ncount
        SlTrace.lg(f"{desc:14s} {self.ncount:5d} {time_dur:5.3f} {npath:5.0f} {nbackup:6.0f} {track_level:5.0f} {ntrack_ntie:6.1f} {ntie:6.1f} ")
            
class MaxCompStats(CompStats):
    def add(self, time_dur=None, npath=None, nbackup=None, track_level=None, ntrack_ntie=None, ntie=None, count=True):
        if self.time_dur is None or time_dur > self.time_dur:
            self.time_dur = time_dur
        if self.npath is None or npath > self.npath:
            self.npath = npath
        if self.nbackup is None or nbackup > self.nbackup:  
            self.nbackup = nbackup
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
    def add(self, time_dur=None, npath=None, nbackup=None, track_level=None, ntrack_ntie=None, ntie=None, count=True):
        if self.time_dur is None or time_dur < self.time_dur:
            self.time_dur = time_dur
        if self.npath is None or npath < self.npath:
            self.npath = npath
        if self.nbackup is None or nbackup < self.nbackup:  
            self.nbackup = nbackup
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

class DisplayedPath:
    """ Displayed path info to facilitate display arrangement/access/manipulation
    """
    org_no = None       # Original order
    def __init__(self, path=None, disp_board=None, org_no=None, desc=None):
        """ Setup
        :path: path (list of locs in order)
        :disp_board: ChessBoardDisplay instance
        :org_no: original order(starting at one) default: numbered as called
        :description: description of display default: None
        """
        if disp_board is None:
            raise SelectError("Required disp_board is missing")
        disp_board = disp_board
        if path is None:
            path = disp_board.path
        self.path = path
        if org_no is None:
            if DisplayedPath.org_no is None:
                DisplayedPath.org_no = 0
            org_no = DisplayedPath.org_no + 1
        self.org_no = org_no
        self.desc = desc
        
displayed_paths = []        # List of displayed paths

success_comp_stats = ResultCompStats()
fail_comp_stats = ResultCompStats()    
for ri in range(start_ri, end_ri+1):
    for ci in range(start_ci, end_ci+1):
        ###ChessBoard.set_path_tracking(mw=mw, display_path_board=display_path_board,
        ###                             track_all_path=track_all_path)
        sqno += 1
        loc = (ci,ri)
        SlTrace.lg(f"{sqno:2d}: {loc2desc(loc)}", dp=3)
        kpths = KnightsPaths(loc=(ci,ri), closed_tours=closed_tours, time_limit=time_out,
                             max_look_ahead=max_look_ahead)
        time_beg = datetime.now()
        path = kpths.next_path()
        nbackup = kpths.get_nbackup()
        track_level = kpths.get_track_level()
        time_end = datetime.now()
        time_dur = (time_end-time_beg).total_seconds()
        npath = kpths.get_ncomplete_path()
        ntrack_ntie = kpths.ntrack_ntie
        ntie = kpths.ntie
        comp_stats = (f"Comp Stats: time={time_dur:.3f} paths={npath}"
                    f" backup={nbackup} track_level={track_level} tie_track={ntrack_ntie} ntie={ntie}")
        if path is None:
            what = "tours" if closed_tours else "paths"
            SlTrace.lg(f"No {what} found - {npath} complete paths found")
            SlTrace.lg(f"    {comp_stats}")
            fail_comp_stats.add(time_dur=time_dur, npath=npath, nbackup=nbackup,
                            track_level=track_level, ntrack_ntie=ntrack_ntie,
                            ntie=ntie)
            continue
        
        if len(path) == ncols*nrows:
            success_comp_stats.add(time_dur=time_dur, npath=npath, nbackup=nbackup,
                            track_level=track_level, ntrack_ntie=ntrack_ntie,
                            ntie=ntie)
            ct_desc = ""        # Closed tour description, if one
            if kpths.is_neighbor(path[0], path[-1]):
                n_closed_tour += 1
                ndesc = "th"
                if n_closed_tour%10 == 1:
                    ndesc = "st"
                if n_closed_tour%10 == 2 or n_closed_tour%10 == 3:
                    ndesc = "nd"
                ct_desc = (f" {n_closed_tour:d}{ndesc} closed tour"
                        + f" paths={npath}")
            SlTrace.lg(f"{ct_desc} (in {time_dur:.3f} sec)"
                       + f" from {loc2desc(path[0])}"
                       + f" to {loc2desc(path[-1])}"
                       + f" path: {path_desc(path)}")
            n_complete_paths += 1
            n_having_complete_path += 1
            total_success_time += time_dur
            if max_success_time is None or time_dur > max_success_time:
                max_success_time = time_dur
            SlTrace.lg()
            dp = display_path(f" {sqno}: {loc2desc(loc)} {ct_desc} {time_dur:.3f} sec: ", path)
            displayed_paths.append(DisplayedPath(disp_board=dp, desc="success"))
        else:
            dp = display_path("Short Path", path)
            displayed_paths.append(DisplayedPath(disp_board=dp, desc="Short Path"))
        SlTrace.lg(f"    {comp_stats}")
                
SlTrace.lg(f"{n_complete_paths:4d} complete paths")
SlTrace.lg(f"{n_closed_tour:4d} closed tours")

SlTrace.lg(f"{n_having_complete_path:4d} starting squares having complete path")
SlTrace.lg(f"{n_with_no_complete_path:4d} starting squares with no complete path")
SlTrace.lg(f"{n_with_multiple_complete_paths:4d} starting squares with multiple complete paths")
if n_complete_paths > 0:
    SlTrace.lg(f"  Average success time: {total_success_time/n_complete_paths:.3f}")
    SlTrace.lg(f"  Maximum success time: {max_success_time:.3f}")
SlTrace.lg()
SlTrace.lg("    Computational Statistics")
success_comp_stats.report_heading("  Successful")
success_comp_stats.min.report_line("    minimum")
success_comp_stats.max.report_line("    maximum")
success_comp_stats.avg.report_line("    average")
fail_comp_stats.report_heading("  Failed")
fail_comp_stats.min.report_line("    minimum")
fail_comp_stats.max.report_line("    maximum")
fail_comp_stats.avg.report_line("    average")
if longest_path_start is not None:
    SlTrace.lg(f"  {loc2desc(longest_path_start)} starts the longest path({len(longest_path):d})"
               + f"  {path_desc(longest_path)}"
               )
if display_complete:
    mw.mainloop()

mw.mainloop()
