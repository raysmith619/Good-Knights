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
import re
from tkinter import *

from select_window import SelectWindow
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
end_ci = ncols-1
###end_ri = 0          # TFD to limit printout
sqno = 0
all_paths = True
all_paths = False       #TFD
time_out = .5              # Time limit for path calculation
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
pWwm = Tk()                 # To support grid layout - MUST be done before wm
wm = Tk()                   # To force GUI to main thread
pW = None
paths_gen = None

def arrange_cmd():
    SlTrace.lg("Arrange Paths")
    screen_width = pWwm.winfo_screenwidth()
    screen_height = pWwm.winfo_screenheight()
    first = pW.get_pa_var("first")
    start_x = 10
    start_y = 50
    wrap = pW.get_pa_var("wrap")
    last = pW.get_pa_var("last")
    square = pW.get_pa_var("square")
    lend = len(paths_gen.displayed_paths)
    if last is None or last == "":
        last = lend
    tour = pW.get_pa_var("tour")
    not_tour = pW.get_pa_var("not_tour")
    comp = pW.get_pa_var("comp") 
    not_comp = pW.get_pa_var("not_comp")  
    size = pW.get_pa_var("size")
    arr = pW.get_pa_var("arr")
    arr_list = []           # Arranged list
    other_list = []
    dlist = paths_gen.displayed_paths
    for np in range(1, lend+1):
        if first is None or first == "" or np < first:
            if wrap:
                arr_list.append(dlist[np-1])
            else:
                other_list.append(dlist[np-1])
        elif last is None or last == "" or np > last:
            other_list.append(dlist[np-1])
        else:
            arr_list.append(dlist[np-1])
    
    if square is not None and square != "":
        a_list = []
        o_list = []
        for ad in arr_list:
            start_loc = ad.path[0]
            sq = ChessBoard.loc2desc(start_loc)
            if re.search(square, sq):
                a_list.append(ad)
            else:
                o_list.append(ad)
        arr_list = a_list
        other_list += o_list        
    
    if tour or not_tour:
        a_list = []
        o_list = []
        for ad in arr_list:
            used = False
            is_tour = ad.is_closed_tour
            if tour:
                if is_tour:
                    a_list.append(ad)
                    used = True
            if not_tour:
                if not is_tour:
                    a_list.append(ad)
                    used = True
            if not used:
                o_list.append(ad)
        arr_list = a_list
        other_list += o_list        
    
    if comp or not_comp:
        a_list = []
        o_list = []
        for ad in arr_list:
            used = False
            is_comp = ad.is_complete_tour
            if comp:
                if is_comp:
                    a_list.append(ad)
                    used = True
            if not_comp:
                if not is_comp:
                    a_list.append(ad)
                    used = True
            if not used:
                o_list.append(ad)
        arr_list = a_list
        other_list += o_list        

                
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
    elif arr == PathsWindow.ARR_STACK:
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
                
def arrange_set():
    global pW            
    pW = PathsWindow(wm=pWwm, arrange_call=arrange_cmd)
    pW.set_pa_var("arr", pW.ARR_TILE)
    pW.set_pa_var("sort", pW.SORT_ORIG)
    
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
parser.add_argument('--end_ci=', type=int, dest='end_ci', default=end_ci)
parser.add_argument('--end_ri=', type=int, dest='end_ri', default=end_ri)
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
ncols = args.ncols
nrows= args.nrows
time_out = args.time_out
width = args.width
height = args.height
trace = args.trace
if trace:
    SlTrace.setFlags(trace)

SlTrace.setLogStdTs(True)
app = SelectWindow(wm,
                title="Good Knights",
                pgmExit=pgm_exit,
                )
app.add_menu_command("Run", run_cmd)
app.add_menu_command("Pause", pause_cmd)

path_starts = []
for ri in range(start_ri, end_ri+1):
    for ci in range(start_ci, end_ci+1):
        loc = (ci,ri)
        path_starts.append(loc)

arrange_set()

paths_gen = PathsGen(path_starts=path_starts,
    time_out=time_out,
    closed_tours=closed_tours,
    width=width,
    height=height,
    nrows = nrows,
    ncols = ncols,
    max_look_ahead=max_look_ahead)
paths_gen.go()        

if display_complete:
    wm.mainloop()

wm.mainloop()
