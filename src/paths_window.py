# paths_window.py
"""
Path Display and Arrangement window
"""
from tkinter import *

from select_error import SelectError
from select_trace import SlTrace
from select_control import SelectControl

from chess_board import ChessBoard

class PathsWindow(Frame):
    ARR_TILE = 1
    ARR_LAYER = 2
    ARR_STACK = 3
    
    SORT_ORIG = 1
    SORT_ROW = 2
    SORT_COL = 3
    SORT_TIME = 4
    
    def __init__(self, wm=None, arrange_call=None,
                  run_call=None, pause_call=None, continue_call=None,
                  step_call=None, back_call=None, stop_call=None):
        global cF
        
        if wm is None:
            wm = Tk()
        self.wm = wm
        height = 450
        width = 400
        xpos = 600
        ypos = 50
        self.wm.bind ( "<Return>", self.enter_cmd)
        geo = f"{width}x{height}+{xpos}+{ypos}"     # NO SPACES PERMITTED
        wm.geometry(geo)
        self.arrange_call = arrange_call
        self.run_call = run_call
        self.pause_call = pause_call
        self.continue_call = continue_call
        self.step_call = step_call
        self.back_call = back_call
        self.stop_call = stop_call
        self.prev_arr_list = None
        self.run = False                    # True iff running path generation
        self.is_pause = False               # Paused
        self.is_step = False                # Step pressed
        self.is_action = False              # True ==> pending action
        self.paths_gen = None               # Set to control link
        cF = SelectControl()
        
        ROW_TITLE = 0
        
        Label(wm, text="Path Arrangement").grid(row=ROW_TITLE, column=2)
        
        ROW_UNDO_REDO = ROW_TITLE+1
        Label(wm, text="").grid(row=ROW_UNDO_REDO)
        ROW_UNDO_BUTTON = ROW_UNDO_REDO+1
        COL_UNDO_BUTTON = 0
        ROW_REDO_BUTTON = ROW_UNDO_BUTTON        
        COL_REDO_BUTTON = COL_UNDO_BUTTON+1
        Button(wm, text="UNDO\nsettings", command=self.undo_settings).grid(
                row=ROW_UNDO_BUTTON, column=COL_UNDO_BUTTON)
        Button(wm, text="REDO\nsettings", command=self.redo_settings).grid(
                row=ROW_REDO_BUTTON, column=COL_REDO_BUTTON)
        
        ROW_ARR = ROW_UNDO_BUTTON+1
        ROW_ARR_SELECT = ROW_ARR-1
        
        COL_ARR = 0
        COL_SORT = COL_ARR+1
        COL_SELECT = COL_SORT+1  # Centered
        COL_FIRST = COL_SORT+1
        COL_WRAP = COL_FIRST+1
        COL_LAST = COL_WRAP+1
        
        COL_SIZE_LABEL = 0
        COL_SIZE = COL_SIZE_LABEL+1
    
        
        
        
        Label(wm, text="Arrangement").grid(row=ROW_ARR, column=COL_ARR)
        Label(wm, text="sorted by").grid(row=ROW_ARR, column=COL_SORT)
        Label(wm, text="Select").grid(row=ROW_ARR_SELECT, column=COL_SELECT, columnspan=3, sticky=S)
        Label(wm, text="first").grid(row=ROW_ARR,column=COL_FIRST)
        Label(wm, text="wrap").grid(row=ROW_ARR, column=COL_WRAP)
        Label(wm, text="last").grid(row=ROW_ARR, column=COL_LAST)

        cF.make_val("arr", self.ARR_TILE)
        Radiobutton(wm, text="tile", variable=cF.get_var("arr"), value=self.ARR_TILE).grid(row=11, column=COL_ARR)
        Radiobutton(wm, text="layer", variable=cF.get_var("arr"), value=self.ARR_LAYER).grid(row=12, column=COL_ARR)
        Radiobutton(wm, text="stack", variable=cF.get_var("arr"), value=self.ARR_STACK).grid(row=13, column=COL_ARR)
       
        cF.make_val("sort", self.SORT_ORIG)
        Radiobutton(wm, text="orig", variable=cF.get_var("sort"), value=self.SORT_ORIG).grid(row=11, column=COL_SORT)
        Radiobutton(wm, text="row", variable=cF.get_var("sort"), value=self.SORT_ROW).grid(row=12, column=COL_SORT)
        Radiobutton(wm, text="col", variable=cF.get_var("sort"), value=self.SORT_COL).grid(row=13, column=COL_SORT)
        Radiobutton(wm, text="time", variable=cF.get_var("sort"), value=self.SORT_TIME).grid(row=14, column=COL_SORT)
        
        cF.make_val("first", 0, textvar=True)
        self.wj_first = Entry(wm, width=3, textvariable=cF.get_textvar("first"), validate=ALL)
        self.wj_first.grid(row=11, column=COL_FIRST)
        cF.add_widget("first", self.wj_first)
        
        cF.make_val("wrap", False)
        self.wj_wrap = Checkbutton(wm, variable=cF.get_var("wrap"))
        self.wj_wrap.grid(row=11, column=COL_WRAP)

        cF.make_val("last", 0, textvar=True)
        self.wj_last = Entry(wm, width=3, textvariable=cF.get_textvar("last"))
        self.wj_last.grid(row=11, column=COL_LAST)
        cF.add_widget("last", self.wj_last)

        cF.make_val("size", 300, textvar=True)
        ROW_SIZE =  21
        Label(wm, text="Size").grid(row=ROW_SIZE, column=COL_SIZE_LABEL)
        self.wj_size = Entry(wm, width=4, textvariable=cF.get_textvar("size"))
        self.wj_size.grid(row=21, column=COL_SIZE, sticky=W)
        cF.add_widget("size", self.wj_size)

        # Selection options
        ROW_SQ = 12
        cF.make_val("square", ".*", repeat=True, textvar=True)
        Label(wm, text="square").grid(row=ROW_SQ, column=COL_SELECT, sticky=E)
        self.wj_square = Entry(wm, width=18, textvariable=cF.get_textvar("square"))
        self.wj_square.grid(row=ROW_SQ, column=COL_SELECT+1, columnspan=3, sticky=W)
        cF.add_widget("square", self.wj_square)
        
        cF.make_val("closed_tour", False, repeat=True)
        Label(wm, text="closed tour").grid(row=ROW_SQ+1, column=COL_SELECT, sticky=E)
        self.wj_tour = Checkbutton(wm, variable=cF.get_var("closed_tour"), onvalue=True, offvalue=False)
        self.wj_tour.grid(row=ROW_SQ+1, column=COL_SELECT+1, sticky=W)
        
        cF.make_val("not_tour", False)
        Label(wm, text="NOT tour").grid(row=ROW_SQ+1, column=COL_SELECT+2, sticky=E)
        self.wj_not_tour = Checkbutton(wm, variable=cF.get_var("not_tour"))
        self.wj_not_tour.grid(row=ROW_SQ+1, column=COL_SELECT+3, sticky=W)
        
        cF.make_val("comp", False)
        Label(wm, text="complete").grid(row=ROW_SQ+2, column=COL_SELECT, sticky=E)
        self.wj_comp = Checkbutton(wm, variable=cF.get_var("comp"))
        self.wj_comp.grid(row=ROW_SQ+2, column=COL_SELECT+1, sticky=W)
        
        cF.make_val("not_comp", False)
        Label(wm, text="NOT comp").grid(row=ROW_SQ+2, column=COL_SELECT+2, sticky=E)
        self.wj_not_comp = Checkbutton(wm, variable=cF.get_var("not_comp"))
        self.wj_not_comp.grid(row=ROW_SQ+2, column=COL_SELECT+3, sticky=W)
        
        Label(wm, text="run prev list").grid(row=ROW_SQ+3, column=COL_SELECT, sticky=E)
        cF.make_val("prev_list", False)
        self.wj_prev_list = Checkbutton(wm, variable=cF.get_var("prev_list"))
        self.wj_prev_list.grid(row=ROW_SQ+3, column=COL_SELECT+1, sticky=W)

        Label(wm, text="").grid(row=ROW_SIZE+1)
        ROW_ARRANGE_BUTTON = ROW_SIZE+1
        COL_ARRANGE_BUTTON = 0             
        Button(wm, text="Arrange", command=self.arrange_button).grid(row=ROW_ARRANGE_BUTTON, column=COL_ARRANGE_BUTTON)


        Label(wm, text="Running Control").grid(row=ROW_ARRANGE_BUTTON+1, columnspan=5)
        ROW_NROW_COL = ROW_ARRANGE_BUTTON+2
        COL_NROW_COL = 0             
         
        Label(wm, text="Rows").grid(row=ROW_NROW_COL, column=COL_NROW_COL, sticky=E)
        cF.make_val("nrow", 8, repeat=True, textvar=True)
        self.wj_nrow = Entry(wm, width=3, textvariable=cF.get_textvar("nrow"))
        self.wj_nrow.grid(row=ROW_NROW_COL, column=COL_NROW_COL+1, sticky=W)
        cF.add_widget("nrow", self.wj_nrow)
         
        Label(wm, text="Cols").grid(row=ROW_NROW_COL, column=COL_NROW_COL+2, sticky=E)
        cF.make_val("ncol", 8, repeat=True, textvar=True)
        self.wj_ncol = Entry(wm, width=3, textvariable=cF.get_textvar("ncol"))
        self.wj_ncol.grid(row=ROW_NROW_COL, column=COL_NROW_COL+3, sticky=W)
        cF.add_widget("ncol", self.wj_ncol)
        
        ROW_FIND_CLOSED = ROW_NROW_COL
        COL_FIND_CLOSED = COL_NROW_COL+4
        cF.make_val("find_closed", True, repeat=True, textvar=True)
        Label(wm, text="find\nclosed tours").grid(row=ROW_FIND_CLOSED, column=COL_FIND_CLOSED, sticky=E)
        self.wj_tour = Checkbutton(wm, variable=cF.get_var("find_closed"), onvalue=True, offvalue=False)
        self.wj_tour.grid(row=ROW_NROW_COL, column=COL_FIND_CLOSED+1, sticky=W)

        
        ROW_RUN_CONTROL = ROW_NROW_COL + 1
        ###Label(wm, text="").grid(row=ROW_RUN_CONTROL)
        ROW_DISPLAY = ROW_RUN_CONTROL+1
        Label(wm, text="display\nmove").grid(row=ROW_DISPLAY, column=0, sticky=E)
        cF.make_val("display_move", False, repeat=True)
        self.wj_display_move = Checkbutton(wm, variable=cF.get_var("display_move"))
        self.wj_display_move.grid(row=ROW_DISPLAY, column=1, sticky=W)
         
        Label(wm, text="move\ntime").grid(row=ROW_DISPLAY, column=2, sticky=E)
        cF.make_val("move_time", 2., repeat=True, textvar=True)
        self.wj_move_time = Entry(wm, width=4, textvariable=cF.get_textvar("move_time"))
        self.wj_move_time.grid(row=ROW_DISPLAY, column=3, sticky=W)
        cF.add_widget("move_time", self.wj_move_time)
         
        Label(wm, text="time\nlimit").grid(row=ROW_DISPLAY, column=4, sticky=E)
        cF.make_val("time_limit", 2.0, repeat=True, textvar=True)
        self.wj_time_limit = Entry(wm, width=5, textvariable=cF.get_textvar("time_limit"))
        self.wj_time_limit.grid(row=ROW_DISPLAY, column=5, sticky=W)
        cF.add_widget("time_limit", self.wj_time_limit)
        
        ###Label(wm, text="").grid(row=ROW_DISPLAY+1)
        ROW_RUN_BUTTON = ROW_DISPLAY+2
        COL_RUN_BUTTON = 0
        Button(wm, text="Run", command=self.run_button).grid(row=ROW_RUN_BUTTON, column=COL_RUN_BUTTON)
        Button(wm, text="Pause", command=self.pause_button).grid(row=ROW_RUN_BUTTON, column=COL_RUN_BUTTON+1)
        Button(wm, text="Continue", command=self.continue_button).grid(row=ROW_RUN_BUTTON, column=COL_RUN_BUTTON+2)
        Button(wm, text="Step", command=self.step_button).grid(row=ROW_RUN_BUTTON, column=COL_RUN_BUTTON+3)
        Button(wm, text="Back", command=self.back_button).grid(row=ROW_RUN_BUTTON, column=COL_RUN_BUTTON+4)
        Button(wm, text="Stop", command=self.stop_button).grid(row=ROW_RUN_BUTTON, column=COL_RUN_BUTTON+5)
        
        NEXT_TOUR_BUTTON = ROW_RUN_BUTTON+1
        COL_NEXT_TOUR_BUTTON = 1
        Button(wm, text="Next Tour", command=self.next_tour_button).grid(row=NEXT_TOUR_BUTTON, column=COL_NEXT_TOUR_BUTTON)
        Button(wm, text="Prev Tour", command=self.prev_tour_button).grid(row=NEXT_TOUR_BUTTON, column=COL_NEXT_TOUR_BUTTON+1)

        size_check = self.get_val("size", 123)
        if type(size_check) != int:
            raise SelectError("size should be int")

    def enter_cmd(self, event):
        self.update_settings()

    def get_prev_starts(self):
        """ Get starting squares corresponding to previous arranged paths
        """
        path_starts = []
        if self.prev_arr_list is None:
            return []
        
        for dpath in self.prev_arr_list:
            path_starts.append(dpath.path[0])
        return path_starts
    
    def get_starts(self, locs=None, nrow=None, ncol=None, start_ri=None, end_ri=None,
                   start_ci=None, end_ci=None):
        """ Get list of starting squares
        :locs: base list of squares(loc or algebraic notation) default: nrowxncol squares
        :nrow: number of rows default: from gen_paths
        :ncol: number of cols default: from gen_paths
        :start_ri: beginning row index default: 0
        :end_ri: ending row index default: nrow-1
        :start_ci: beginning col index default: 0
        :end_ci: ending column index default: ncol-1
        :returns: pair: list of starting squares
        """
        if ncol is None:
            ncol = self.paths_gen.ncol
        if nrow is None:
            nrow = self.paths_gen.nrow
            
        cb = ChessBoard(nrow=nrow, ncol=ncol)
        if locs is None:
            path_starts = []
            if start_ri is None:
                start_ri = 0
            if end_ri is None:
                end_ri = nrow-1
            if start_ci is None:
                start_ci = 0
            if end_ci is None:
                end_ci = ncol-1
            for ri in range(start_ri, end_ri+1):
                for ci in range(start_ci, end_ci+1):
                    loc = (ci,ri)
                    path_starts.append(loc)
            locs = path_starts

        first = self.get_val("first", 0)
        lend = len(locs)
        if first == 0:
            first = 1
        wrap = self.get_val("wrap")
        last = self.get_val("last", 0)
        if last == 0:
            last = lend + 1
        square = self.get_val("square")
        if last == 0:
            last = lend
        loc_list = []
        for np in range(1, lend+1):
            if first == 0 or np < first:
                if wrap:
                    loc_list.append(locs[np-1])
            else:
                loc_list.append(locs[np-1])
        
        if square is not None and square != "":
            if "," in square:       # comma separates patterns
                pats = square.split(",")
                square = ""
                for pat in pats:
                    if square != "":
                        square += "|"
                    square += "("  + pat + ")"
            a_list = []
            for loc in loc_list:
                sq = cb.loc2desc(loc)
                if re.search(square, sq):
                    a_list.append(loc)
            loc_list = a_list
        
        return loc_list

    def select_paths(self, dpaths=None):
        """ Select list of displayed paths
        Uses get_starts to get basic list
        Refines this list based on run results
        Resulting list is saved in self.prev_arr_list
        
        :paths: initial list
        :returns: list of selected paths, list of unselected paths
        """
        
        locs = []                   # Find list of starting locs
        if len(dpaths) == 0:
            return [], []
        
        for dpath in dpaths:
            locs.append(dpath.path[0])    # Get starting loc
            
        start_locs = self.get_starts(locs=locs)
        start_paths = []            # Get paths with these starting locs
        other_paths = []
        for dpath in dpaths:
            if dpath.path[0] in start_locs:
                start_paths.append(dpath)
            else:
                other_paths.append(dpath)
        last = self.get_val("last")
        if last is 0 or last == "":
            last = len(dpaths)
        closed_tour = self.get_val("closed_tour")
        not_tour = self.get_val("not_tour")
        comp = self.get_val("comp") 
        not_comp = self.get_val("not_comp")  

        arr_list = start_paths
        other_list = other_paths
        if closed_tour or not_tour:
            a_list = []
            o_list = []
            for ad in arr_list:
                used = False
                is_tour = ad.is_closed_tour
                if closed_tour:
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
        self.prev_arr_list = arr_list        
        return arr_list, other_list
 
    def set_in_step(self):
        self.is_action = True
        self.is_step = True
        self.is_pause = True
 
    def clear_in_step(self):
        self.is_action = False
        self.is_step = False
        self.is_pause = False
               
    def update_display(self):
        wm = self.wm
        wm.update_idletasks()
        wm.update()
            
    def update_settings(self):
        cF.update_settings()
        
    def arrange_button(self):
        """ Called when button pressed
            Updates variables
        """
        self.update_settings()
        if self.arrange_call is not None:
            self.arrange_call()
        
    def run_button(self):
        """ Called when button pressed directly
        :adj_tour: if present, adjust tour number before run
        """
        self.step = False           # Clear step command
        self.is_pause = False
        self.run_command()
        
    def next_tour_button(self):
        """ Called when next_tour pressed
        """
        if self.paths_gen is None:
            SlTrace.lg("paths_gen connection has NOT been setup")
            return
        
        self.paths_gen.next_tour()
        
    def prev_tour_button(self):
        """ Called when prev_tour pressed
        """
        if self.paths_gen is None:
            SlTrace.lg("paths_gen connection has NOT been setup")
            return
        
        self.paths_gen.prev_tour()
        
    def run_command(self):
        """ Called when running program
            Updates variables
            :adj_tour: if present adjuest tour number before running
        """
        self.update_settings()
        self.run = True
        self.pause = False
        if self.run_call is not None:
            self.wm.after(1, self.run_call)
        
    def pause_button(self):
        """ Called when button pressed
            Updates variables
        """
        self.is_action = True
        self.update_settings()
        self.is_pause = True
        if self.pause_call is not None:
            self.wm.after(1, self.pause_call)
        
    def continue_button(self):
        """ Called when button pressed
            Updates variables
        """
        self.update_settings()
        self.is_pause = False
        self.is_step = False
        if self.continue_call is not None:
            self.wm.after(1, self.continue_call)
        
    def step_button(self):
        """ Called when button pressed
            Updates variables
        """
        self.update_settings()
        self.set_val("display_move")
        if self.step_call is not None:
            self.step_call()

    def back_button(self):
        """ Called when button pressed
            Updates variables
        """
        self.update_settings()
        self.is_action = True
        if self.back_call is not None:
            self.back_call()
    
    def set_paths_gen(self, paths_gen):     #w:
        """ connect paths_gen to control window
        :paths_gen: PathsGen control 
        """
        self.paths_gen = paths_gen
        
    def stop_button(self):             
        """ Called when button pressed
            Updates variables
        """
        self.set_val("display_move")     # Force action
        self.update_settings()
        self.is_action = True
        self.is_pause = True
        if self.paths_gen is None:
            raise SelectError("paths_gen connection has NOT been setup")
        self.paths_gen.stop_gen()
            
    def get_val(self, name, default=None):
        """ Returns current variable setting
        :name: variable name 
        :default: value used if val is not set
        """
        val = cF.get_val(name, default=default)
        if name == "first":
            if val == "":
                val == 0
        elif name == "last":
            if val == "" or val == 0:
                val = 0
        return val
            
    def set_val(self, name, val=None):
        """ Sets variable setting
        :var_name: variable name 
        :val: value default: None
        """
        if val is None:
            cur_val = cF.get_val(name)
            tcur_val = type(cur_val)
            if tcur_val == bool:
                val = True
            elif tcur_val == str:
                val = ""
            elif tcur_val == int:
                val = 0
            elif tcur_val == float:
                val = 0.
        cF.set_val(name, val)

    def undo_settings(self):
        """ Recover previous saved window settings
        """
        cF.undo_settings()
    
    def redo_settings(self):
        """ Recover settings replaced by last undo
        """
        cF.redo_settings()
    
if __name__ == "__main__":
    
    def arrange():
        print("arrange test call")
        
    wm = Tk()
    
    pW = PathsWindow(wm, arrange_call=arrange)
    ###pW.set_val("arr", PathsWindow.ARR_STACK)
    mainloop()