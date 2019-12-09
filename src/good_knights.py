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
import os
import argparse
import re
from tkinter import *

from grid_window import GridWindow
from select_trace import SlTrace
from select_control import SelectControl

from chess_board import ChessBoard
from chess_board_display import ChessBoardDisplay
display_path = ChessBoardDisplay.display_path
from paths_window import PathsWindow
from paths_gen import PathsGen

pWwm = Tk()                 # To support grid layout - MUST be done before wm
###wm = Tk()                   # To force GUI to main thread
wm = pWwm
pW = None
cF = SelectControl(control_prefix="path_control")
ncol = cF.make_val("ncol", 4)     # default, override from properties

closed_tours = cF.make_val("find_closed", True)         # True => only accept closed tours
display_complete = cF.make_val("display_complete", True)    # True => display each complete(cover all) path
display_move = display_complete = cF.make_val("display_move", False)
move_time = cF.make_val("move_time", .1)              # Time per move (seconds)
display_path_board = cF.make_val("display_path_board", False)  # True => display path board each path
track_all_path = cF.make_val("track_all_path", False)
###track_all_path = True               # TFD
max_look_ahead = cF.make_val("max_look_ahead", 5)          # Maximum look-ahead for best move testing    
nrow = cF.make_val("nrow", 8, repeat=True)
ncol = cF.make_val("ncol", 8, repeat=True)
###nrow = ncol = 6       # TFD
###nrow = ncol = 4       # TFD
run = cF.make_val("run", False)             # True - run on beginning, False - wait for arrangement
###run = True              ### TFD
start_ri = cF.make_val("start_ri", 0)
###start_ri = 2        # TFD
end_ri = cF.make_val("end_ri", nrow-1)
start_ci = cF.make_val("start_ci", 0)
###start_ci = 3        # TFD
end_ci = cF.make_val("end_ci", ncol-1)
###end_ri = 0          # TFD to limit printout
sqno = 0
all_paths = cF.make_val("all_paths", False)
time_out = cF.make_val("time_out", 2)              # Time limit for path calculation
###time_out = 999              ### TFD
trace = "stack_grow,complete_paths"
trace = "stack_grow"
trace = "back_off_trace"
trace = ""
trace = cF.make_val("trace", trace)
width = cF.make_val("width", 300)             # Chess board width in pixels
height = cF.make_val("height", width)            # Chess board height in pixels
###trace = "stack_grow,back_off_trace,no_more_moves"
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
app = None
paths_gen = None

def arrange_cmd():
    cb = ChessBoard(nrow=nrow, ncol=ncol)
    SlTrace.lg("Arrange Paths")
    screen_width = pWwm.winfo_screenwidth()
    screen_height = pWwm.winfo_screenheight()
    start_x = 10
    start_y = 50
    if paths_gen is None:
        SlTrace.lg("No paths to arrange yet")
        return
    
    dlist = paths_gen.displayed_paths
    size = pW.get_val("size")
    arr = pW.get_val("arr")
    arr_list, other_list = pW.select_paths(dpaths=dlist)
    arr_locs = []
    for dpath in arr_list:
        arr_locs.append(dpath.path[0])    
    other_locs = []
    for dpath in other_list:
        other_locs.append(dpath.path[0])    
    SlTrace.lg(f"Arranged: {cb.path_desc(arr_locs)}")
    SlTrace.lg(f"Hidden: {cb.path_desc(other_locs)}")            
    if arr == PathsWindow.ARR_TILE:
        cur_x, cur_y = start_x, start_y
        for arr_disp in arr_list:
            SlTrace.lg(f"arrange {arr_disp.disp_board.desc}")
            arr_disp.resize(width=size, height=size, x=cur_x, y=cur_y)
            arr_disp.show()         # Insure visible
            cur_x += size
            if cur_x > screen_width-size:
                cur_x = start_x
                cur_y += size
        for other_disp in other_list:
            other_disp.hide()
    elif arr == PathsWindow.ARR_STACK or arr == PathsWindow.ARR_LAYER:
        cur_x, cur_y = start_x, start_y
        for arr_disp in arr_list:
            SlTrace.lg(f"arrange {arr_disp.disp_board.desc}")
            arr_disp.resize(width=size, height=size, x=cur_x, y=cur_y)
            arr_disp.show()         # Insure visible
            cur_y += size*.1
            if cur_y > screen_height-2*size:
                cur_y = start_y
                cur_x += size
    for other_disp in other_list:
        other_disp.hide()

def run_set():
    global paths_gen, display_move, time_out, nrow, ncol
    global start_ri, end_ri, start_ci, end_ci
    global closed_tours
    global width, height
    if paths_gen is not None:
        paths_gen.destroy()
        paths_gen = None
    use_prev_list = pW.get_val("prev_list")
    
    nrow_prev = nrow
    ncol_prev = ncol
    nrow = pW.get_val("nrow")
    ncol = pW.get_val("ncol")
    if nrow != nrow_prev or ncol != ncol_prev:
        use_prev_list = False
        start_ri = start_ci = 0
        end_ri = start_ri + nrow-1
        end_ci = start_ci + ncol-1
    if use_prev_list and pW.prev_arr_list is not None:
        path_starts = pW.get_prev_starts()
    else:    
        path_starts = pW.get_starts(start_ri=start_ri, end_ri=end_ri,
                                start_ci=start_ci, end_ci=end_ci,
                                nrow=nrow, ncol=ncol)
    closed_tours = pW.get_val("find_closed")    
    time_limit = pW.get_val("time_limit")
    if time_limit is None or time_limit == "":
        pass            # use setup
    else:
        time_out = time_limit

    display_move = pW.get_val("display_move")
    move_time = pW.get_val("move_time")
    if move_time is None or move_time == "":
        move_time = .05
    ###path_starts = [(0,0)]            # TFD - one path
    width = pW.get_val("size", width)
    height = pW.get_val("size", height)
    paths_gen = PathsGen(path_starts=path_starts,
        time_out=time_out,
        closed_tours=closed_tours,
        display_move=display_move,
        pW=pW,
        move_time=move_time,
        width=width,
        height=height,
        nrow = nrow,
        ncol = ncol,
        max_look_ahead=max_look_ahead)
    pW.set_paths_gen(paths_gen)     #connect paths_gen to control window

def run_cmd():
    run_set()
    paths_gen.go()        

def pause_cmd():
    ###SlTrace.lg("TBD")
    pass

def continue_cmd():
    ###SlTrace.lg("TBD")
    pass

def step_cmd():
    if paths_gen is None:
        run_set()
        paths_gen.go(in_step=True)
    else:
        paths_gen.next_move()
        pW.set_in_step()

def back_cmd():
    paths_gen.backup_move(keep_move=True)

def stop_cmd():
    SlTrace.lg("User stop")

    
        
    
                    
def arrange_set():
    global pW            
    pW = PathsWindow(wm=pWwm, arrange_call=arrange_cmd,
         run_call=run_cmd, pause_call=pause_cmd, continue_call=continue_cmd,
         step_call=step_cmd, back_call=back_cmd, stop_call=stop_cmd)
    ### pW.set_val("arr", pW.ARR_TILE)
    ### pW.set_val("sort", pW.SORT_ORIG)
    
parser = argparse.ArgumentParser()

parser.add_argument('--closed_tours', type=str2bool, dest='closed_tours', default=closed_tours)
parser.add_argument('--display_complete', type=str2bool, dest='display_complete', default=display_complete)
parser.add_argument('--display_path_board', type=str2bool, dest='display_path_board', default=display_path_board)
parser.add_argument('--max_look_ahead=', type=int, dest='max_look_ahead', default=max_look_ahead)
parser.add_argument('--move_time=', type=float, dest='move_time', default=move_time)
parser.add_argument('--ncol=', type=int, dest='ncol', default=ncol)
parser.add_argument('--nrow=', type=int, dest='nrow', default=nrow)
parser.add_argument('--end_ci=', type=int, dest='end_ci', default=end_ci)
parser.add_argument('--end_ri=', type=int, dest='end_ri', default=end_ri)
parser.add_argument('--run', type=str2bool, dest='run', default=run)
parser.add_argument('--time_out=', type=int, dest='time_out', default=time_out)
parser.add_argument('--width=', type=int, dest='width', default=width)
parser.add_argument('--height=', type=int, dest='height', default=height)
parser.add_argument('--trace', dest='trace', default=trace)
args = parser.parse_args()             # or die "Illegal options"
SlTrace.lg("args: %s\n" % args)
closed_tours = args.closed_tours
display_complete = args.display_complete
display_path_board = args.display_path_board
end_ci = args.end_ci
end_ri = args.end_ri
max_look_ahead = args.max_look_ahead
move_time = args.move_time
ncol = args.ncol
nrow= args.nrow
if end_ci >= ncol:
    end_ci = ncol-1
if end_ri >= nrow:
    end_ri = nrow-1
run = args.run    
time_out = args.time_out
width = args.width
height = args.height
trace = args.trace
pgm_info = "%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:]))
SlTrace.lg(pgm_info)
if trace:
    SlTrace.setFlags(trace)

SlTrace.setLogStdTs(True)
app = GridWindow(wm,
                title="Good Knights",
                arrange_selection=False,
                pgmExit=pgm_exit,
                )
arrange_set()
if run:
    run_cmd()

wm.mainloop()
