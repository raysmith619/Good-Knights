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
from chess_board import ChessBoard
from chess_board_display import ChessBoardDisplay
from paths_window import PathsWindow
from paths_gen import PathsGen

loc2desc = ChessBoard.loc2desc 
loc2tuple = ChessBoard.loc2tuple 
path_desc = ChessBoard.path_desc
display_path = ChessBoardDisplay.display_path

closed_tours = True         # True => only accept closed tours
display_complete = True    # True => display each complete(cover all) path
display_move = False
move_time = .1              # Time per move (seconds)
display_path_board = False  # True => display path board each path
track_all_path = False
###track_all_path = True               # TFD
max_look_ahead = 5          # Maximum look-ahead for best move testing    
nrows = ncols = 8
###nrows = ncols = 6       # TFD
###nrows = ncols = 4       # TFD
run = False             # True - run on beginning, False - wait for arrangement
###run = True              ### TFD
start_ri = 0
###start_ri = 2        # TFD
end_ri = nrows-1
start_ci = 0
###start_ci = 3        # TFD
end_ci = ncols-1
###end_ri = 0          # TFD to limit printout
sqno = 0
all_paths = True
all_paths = False       #TFD
time_out = .5              # Time limit for path calculation
###time_out = 999              ### TFD
trace = "stack_grow,complete_paths"
trace = "stack_grow"
trace = "back_off_trace"
width = 300             # Chess board width in pixels
height = 300            # Chess board height in pixels
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
app = None
pWwm = Tk()                 # To support grid layout - MUST be done before wm
###wm = Tk()                   # To force GUI to main thread
wm = pWwm
pW = None
paths_gen = None

def arrange_cmd():
    SlTrace.lg("Arrange Paths")
    screen_width = pWwm.winfo_screenwidth()
    screen_height = pWwm.winfo_screenheight()
    start_x = 10
    start_y = 50
    dlist = paths_gen.displayed_paths
    size = pW.get_pa_var("size")
    arr = pW.get_pa_var("arr")
    arr_list, other_list = pW.select_paths(dpaths=dlist)    
                
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
    global paths_gen, display_move, time_out
    if paths_gen is not None:
        paths_gen.destroy()
        paths_gen = None
    use_prev_list = pW.get_pa_var("prev_list")
    if use_prev_list and pW.prev_arr_list is not None:
        path_starts = pW.get_prev_starts()
    else:    
        path_starts = pW.get_starts(start_ri=start_ri, end_ri=end_ri,
                                start_ci=start_ci, end_ci=end_ci,
                                nrows=nrows, ncols=ncols)
        
    time_limit = pW.get_pa_var("time_limit")
    if time_limit is None or time_limit == "":
        pass            # use setup
    else:
        time_out = time_limit

    display_move = pW.get_pa_var("display_move")
    move_time = pW.get_pa_var("move_time")
    if move_time is None or move_time == "":
        move_time = .05
    ###path_starts = [(0,0)]            # TFD - one path
    paths_gen = PathsGen(path_starts=path_starts,
        time_out=time_out,
        closed_tours=closed_tours,
        display_move=display_move,
        pW=pW,
        move_time=move_time,
        width=width,
        height=height,
        nrows = nrows,
        ncols = ncols,
        max_look_ahead=max_look_ahead)

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
    pW.set_pa_var("arr", pW.ARR_TILE)
    pW.set_pa_var("sort", pW.SORT_ORIG)
    
parser = argparse.ArgumentParser()

parser.add_argument('--closed_tours', type=str2bool, dest='closed_tours', default=closed_tours)
parser.add_argument('--display_complete', type=str2bool, dest='display_complete', default=display_complete)
parser.add_argument('--display_path_board', type=str2bool, dest='display_path_board', default=display_path_board)
parser.add_argument('--max_look_ahead=', type=int, dest='max_look_ahead', default=max_look_ahead)
parser.add_argument('--move_time=', type=float, dest='move_time', default=move_time)
parser.add_argument('--ncols=', type=int, dest='ncols', default=ncols)
parser.add_argument('--nrows=', type=int, dest='nrows', default=nrows)
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
ncols = args.ncols
nrows= args.nrows
if end_ci >= ncols:
    end_ci = ncols-1
if end_ri >= nrows:
    end_ri = nrows-1
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
