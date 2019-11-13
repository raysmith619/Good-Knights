# paths_window.py
"""
Path Display and Arrangement window
"""
from tkinter import *

from select_error import SelectError


class PathsWindow(Toplevel):
    COL_SEP = 0
    COL_ARR = COL_SEP+1
    COL_SORT = COL_ARR+1
    COL_SELECT = COL_SORT+1  # Centered
    COL_FIRST = COL_SORT+1
    COL_WRAP = COL_FIRST+1
    COL_LAST = COL_WRAP+1
    
    COL_SIZE_LABEL = 0
    COL_SIZE = COL_SIZE_LABEL+1
    
    ARR_TILE = 1
    ARR_LAYER = 2
    ARR_STACK = 3
    
    SORT_ORIG = 1
    SORT_ROW = 2
    SORT_COL = 3
    SORT_TIME = 4
    
    def __init__(self, wm=None, arrange_call=None):
        if wm is None:
            wm = Tk()
        self.wm = wm
        height = 250
        width = 400
        xpos = 600
        ypos = 50
        geo = f"{width}x{height}+{xpos}+{ypos}"     # NO SPACES PERMITTED
        wm.geometry(geo)
        self. arrange_call = arrange_call
        Label(wm, text="Path Arrangement").grid(row=0, column=2)
        Label(wm, text="Arrangement").grid(row=3, column=self.COL_ARR)
        Label(wm, text="sorted by").grid(row=3, column=self.COL_SORT)
        Label(wm, text="Select").grid(row=2, column=self.COL_SELECT, columnspan=3)
        Label(wm, text="first").grid(row=3,column=self.COL_FIRST)
        Label(wm, text="wrap").grid(row=3, column=self.COL_WRAP)
        Label(wm, text="last").grid(row=3, column=self.COL_LAST)

        self.iv_arr = IntVar()
        Radiobutton(wm, text="tile", variable=self.iv_arr, value=self.ARR_TILE).grid(row=11, column=self.COL_ARR)
        Radiobutton(wm, text="layer", variable=self.iv_arr, value=self.ARR_LAYER).grid(row=12, column=self.COL_ARR)
        Radiobutton(wm, text="stack", variable=self.iv_arr, value=self.ARR_STACK).grid(row=13, column=self.COL_ARR)
        self.iv_arr.set(self.ARR_TILE)
       
        self.iv_sort = IntVar()
        self.iv_sort.set(self.SORT_ORIG)
        Radiobutton(wm, text="orig", variable=self.iv_sort, value=self.SORT_ORIG).grid(row=11, column=self.COL_SORT)
        Radiobutton(wm, text="row", variable=self.iv_sort, value=self.SORT_ROW).grid(row=12, column=self.COL_SORT)
        Radiobutton(wm, text="col", variable=self.iv_sort, value=self.SORT_COL).grid(row=13, column=self.COL_SORT)
        Radiobutton(wm, text="time", variable=self.iv_sort, value=self.SORT_TIME).grid(row=14, column=self.COL_SORT)
        
        self.tv_first = StringVar()
        self.tv_first.set("1")
        self.wj_first = Entry(wm, width=3, textvariable=self.tv_first, validate=ALL)
        self.wj_first.grid(row=11, column=self.COL_FIRST)
        
        self.bv_wrap = BooleanVar()
        self.bv_wrap.set(False)
        self.wj_wrap = Checkbutton(wm, variable=self.bv_wrap)
        self.wj_wrap.grid(row=11, column=self.COL_WRAP)

        self.tv_last = StringVar()
        self.tv_last.set("")
        self.wj_last = Entry(wm, width=3, textvariable=self.tv_last)
        self.wj_last.grid(row=11, column=self.COL_LAST)

        size_default = "300"
        self.tv_size = StringVar()
        self.tv_size.set(size_default)
         
        Label(wm, text="Size").grid(row=21, column=self.COL_SIZE_LABEL)
        
        self.tv_size = StringVar()
        self.tv_size.set("300")
        self.wj_size = Entry(wm, width=4, textvariable=self.tv_size)
        self.wj_size.grid(row=21, column=self.COL_SIZE)
        ###self.wj_size.delete(0,END)
        ###self.wj_size.insert(0,size_default)

        # Selection options
        ROW_SQ = 12
        Label(wm, text="square").grid(row=ROW_SQ, column=self.COL_SELECT)
        self.tv_square = StringVar()
        self.tv_square.set(".*")
        self.wj_square = Entry(wm, width=10, textvariable=self.tv_square)
        self.wj_square.grid(row=ROW_SQ, column=self.COL_SELECT+1)
        
        Label(wm, text="tour").grid(row=ROW_SQ+1, column=self.COL_SELECT)
        self.bv_tour = BooleanVar()
        self.bv_tour.set(False)
        self.wj_tour = Checkbutton(wm, variable=self.bv_tour)
        self.wj_tour.grid(row=ROW_SQ+1, column=self.COL_SELECT+1, sticky=W)
        
        Label(wm, text="NOT tour").grid(row=ROW_SQ+1, column=self.COL_SELECT+2)
        self.bv_not_tour = BooleanVar()
        self.bv_not_tour.set(False)
        self.wj_not_tour = Checkbutton(wm, variable=self.bv_not_tour)
        self.wj_not_tour.grid(row=ROW_SQ+1, column=self.COL_SELECT+3, sticky=W)
        
        Label(wm, text="comp").grid(row=ROW_SQ+2, column=self.COL_SELECT)
        self.bv_comp = BooleanVar()
        self.bv_comp.set(False)
        self.wj_comp = Checkbutton(wm, variable=self.bv_comp)
        self.wj_comp.grid(row=ROW_SQ+2, column=self.COL_SELECT+1, sticky=W)
        
        Label(wm, text="NOT comp").grid(row=ROW_SQ+2, column=self.COL_SELECT+2)
        self.bv_not_comp = BooleanVar()
        self.bv_not_comp.set(False)
        self.wj_not_comp = Checkbutton(wm, variable=self.bv_not_comp)
        self.wj_not_comp.grid(row=ROW_SQ+2, column=self.COL_SELECT+3, sticky=W)
        
        Label(wm, text="prev run").grid(row=ROW_SQ+3, column=self.COL_SELECT)
        self.bv_prev_run = BooleanVar()
        self.bv_prev_run.set(False)
        self.wj_prev_run = Checkbutton(wm, variable=self.bv_prev_run)
        self.wj_prev_run.grid(row=ROW_SQ+3, column=self.COL_SELECT+1, sticky=W)

                         
        Button(wm, text="Arrange", command=self.arrange_button).grid(row=31, column=int((self.COL_SELECT+2)/2))

    def arrange_button(self):
        """ Called when button pressed
            Updates variables
        """
        self.tv_size.set(self.wj_size.get())
        self.tv_first.set(self.wj_first.get())
        self.tv_last.set(self.wj_last.get())
        if self.arrange_call is not None:
            self.arrange_call()
            
    def get_pa_var(self, var_name):
        """ Returns current variable setting
        :var_name: variable name 
                    arr: arrangemengt values:
        """
        if var_name == "arr":
            return self.iv_arr.get()
        
        if var_name == "sort":
            return self.iv_sort.get()
        
        if var_name == "first":
            first = self.tv_first.get()
            if first == "":
                return 1
            try:
                return int(first)
            
            except:
                return 1
        
        if var_name == "last":
            last = self.tv_last.get()
            if last == "":
                return None
            try:
                return int(last)
            
            except:
                return None
        
        if var_name == "size":
            size = self.tv_size.get()
            if size == "":
                return 200
            try:
                return int(size)
            
            except:
                return 200
        
        if var_name == "wrap":
            return self.bv_wrap.get()

        if var_name == "square":
            return self.tv_square.get()
        
        if var_name == "tour":
            return self.bv_tour.get()
        
        if var_name == "not_tour":
            return self.bv_not_tour.get()
        
        if var_name == "comp":
            return self.bv_comp.get()
        
        if var_name == "not_comp":
            return self.bv_not_comp.get()
                    
        raise SelectError(f"Unrecognized pa_var: '{var_name}'")
            
    def set_pa_var(self, var_name, val):
        """ Sets variable setting
        :var_name: variable name 
                    arr: arrangemengt values:
        """
        if var_name == "arr":
            self.iv_arr.set(val)
        elif var_name == "sort":
            self.iv_sort.set(val)
        elif var_name == "first":
            self.tv_first.set(str(val))
        elif var_name == "last":
            self.tv_last.set(str(val))
        elif var_name == "size":
            self.tv_size.set(str(val))
        elif var_name == "wrap":
            self.bv_wrap.set(val)
        elif var_name == "square":
            self.tv_square.set(val)
        elif var_name == "tour":
            self.bv_tour.set(val)
        elif var_name == "not_tour":
            self.bv_not_tour.set(val)
        elif var_name == "comp":
            self.bv_comp.set(val)
        elif var_name == "not_comp":
            self.bv_not_comp.set(val)
        else:    
            raise SelectError(f"Unrecognized pa_var: '{var_name}'")
    
if __name__ == "__main__":
    
    def arrange():
        print("arrange test call")
        
    wm = Tk()
    pW = PathsWindow(wm, arrange_call=arrange)
    ###'''
    pW.set_pa_var("arr", PathsWindow.ARR_STACK)
    pW.set_pa_var("last", 64)
    pW.set_pa_var("size", 250)
    ###'''
    mainloop()