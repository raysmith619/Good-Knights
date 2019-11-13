# chess_board_display.py    26-Oct-2019    crs Split display from chess_board.py/ChessBoard

from tkinter import *
from enum import Enum
import re

from chess_board import ChessBoard
from select_dots import SelectDots
from select_trace import SlTrace
from select_error import SelectError

loc2desc = ChessBoard.loc2desc 
loc2tuple = ChessBoard.loc2tuple 

class Piece(Enum):
    P = 1
    N = 2
    B = 3
    R = 4
    Q = 5
    K = 6

class CHColor(Enum):    
    W = 1
    B = 2

class ChessPiece:
    uni_pieces = {'R':'♜', 'N':'♞', 'B':'♝', 'Q':'♛', 'K':'♚', 'P':'♟',
                  'r':'♖', 'n':'♘', 'b':'♗', 'q':'♕', 'k':'♔', 'p':'♙', '.':'·'}
    @classmethod
    def desc(cls, char):
        return ChessPiece.uni_pieces[char]
    
    
    def __init__(self, type=Piece.P, color=CHColor.W):
        self.type = type
        self.color = color

"""
Simple chess board display
Separated from board so board operations, can
be optimized for speed.
"""
class ChessBoardDisplay:
    ncols = 8
    nrows = 8
    tracking_path = []
    track_all_path = False
    board_picts_mw = []

    @classmethod
    def display_path(cls, path,
                     desc=None, nrows=8, ncols=8,
                     width=400, height=400):
        """ Display board with path squares labeled
        :desc: text description
        :path: list of squares in order
        returns ChssBoardDisplay of displayed board
        """
        if not hasattr(cls, 'mw'):
            cls.mw = Tk()
        mw_base = cls.mw
        mw = Toplevel(mw_base)
        mw_base.withdraw() 
        mw.geometry("%dx%d" % (width, height))
        frame = Frame(mw, width=width, height=height, bg="", colormap="new")
        frame.pack(fill=BOTH, expand=True)
        mw.title(desc) 
        
        #creation of an instance
        cb = ChessBoard(nrows=nrows, ncols=ncols)
        cbd = ChessBoardDisplay(mw=mw, frame=frame, board=cb, path=path,
                                desc=desc,
                                width=width, height=height, nrows=nrows, ncols=ncols)
        for loc in path:
            loc = loc2tuple(loc)
            cbd.label_square(loc)
        cbd.display()
        wd = 7
        loc_start = path[0]
        sq1 = cbd.get_square(loc_start)
        cbd.draw_outline(sq1, color="green", width=wd)
        loc_end = path[-1]
        sq2 = cbd.get_square(loc_end)
        cbd.draw_outline(sq2, color="red", width=wd)
        if cb.is_neighbor(loc_end, loc_start):
            p1 = sq1.get_center()
            p2 = sq2.get_center()
            cbd.draw_line(p1,p2, color="blue", width=wd)
        prev_loc = None
        for loc in path:
            loc = loc2tuple(loc)
            if prev_loc is not None:
                sq1 = cbd.get_square(prev_loc)
                p1 = sq1.get_center()
                sq2 = cbd.get_square(loc)
                p2 = sq2.get_center()
                cbd.draw_line(p1,p2, leave=True)
            prev_loc = loc
        mw.lift()
        cls.update_display()
        return cbd
        
    @classmethod
    def update_display(cls):
        mw = cls.mw
        mw.update_idletasks()
        mw.update()

    @classmethod
    def mainloop(cls):
        mw = cls.mw
        mw.mainloop()
        
    
    @classmethod
    def set_path_tracking(cls, mw=None, display_path_board=False,
                          track_all_path=False, tracking_path=[]):
        """ Set / Reset path tracking
        :mw: Tk main window default: create one
        :track_all_path: track all findings default: only growth
        :tracking_path: latest path default: empty
        """
        if mw is None:
            mw = Tk()
        cls.mw = mw
        cls.display_path_board = display_path_board
        cls.tracking_path = tracking_path
        cls.track_all_path = track_all_path
                
                
    def __init__(self,
                frame=None, mw=None,
                desc="",
                width=400, height=400,     # REQUIRED, if window not expanded
                board=None,
                path=None,
                nrows=8,
                ncols=8,
                ):
        self.label_number = 0               # Number for default square labeling
        self.desc = desc
        if board is None:
            board = ChessBoard(nrows=nrows, ncols=ncols)
            nrows = board.nrows             # Inherit from board
            ncols = board.ncols
        self.path = path                    # Path, if associated, may be placed here
        self.board = board    
        self.width = width
        self.height = height
        self.nrows = nrows
        self.ncols = ncols
        if mw is None:
            mw = Tk()
        self.mw = mw
        mw.geometry("%dx%d" % (width, height))
        if frame is None:
            frame = Frame(mw=mw, width=width, height=height, bg="", colormap="new")
            frame.pack(fill=BOTH, expand=YES)
        self.frame = frame
        select_dots = self.create_board(frame, mw, width=width, height=height,
                          nrows=nrows, ncols=ncols)
        self.select_dots = select_dots
        self.nrows = select_dots.nrows      # Local copies
        self.ncols = select_dots.ncols

    def create_board(self, frame=None, mw=None,
                     nrows=None, ncols=None,
                     width=None, height=None):
        
        select_dots = SelectDots(frame, mw,
                        width=width, height=height,     # REQUIRED, if window not expanded
                        nrows=nrows, ncols=ncols,
                        region_visible=True,
                        region_width=1,
                        do_corners=False,               # We do it here
                        do_edges=False,
                        do_regions=False,
                        edge_width=0,
                        highlighting=False
                        )
        for part in select_dots.get_parts("region"):
            row = part.get_row()
            col = part.get_col()
            part.turn_on()
            if (row+col)%2 == 1:
                part.set_color('dark gray')
        select_dots.display()
        return select_dots


    def destroy(self):
        if self.select_dots is not None:
            self.select_dots.destroy()
            self.select_dots = None
        if self.mw is not None:
            self.mw.destroy()
            self.mw = None
            
    def resize(self, width=None, height=None):
        select_dots = self.create_board(self.frame, self.mw, width=width, height=height,
                                         nrows=self.nrows, ncols=self.ncols)
        if hasattr(self, "select_dots") and self.select_dots is not None:
            self.select_dots.destroy()    
        self.select_dots = select_dots

    def add_centered_text(self, text, x=None, y=None,
                          color=None, color_bg=None,
                          height=None, width=None, display=True):
        self.select_dots.add_centered_text(text=text, x=x, y=y,
                          color=color, color_bg=color_bg,
                          height=height, width=width, display=display)
    


    def draw_line(self, p1, p2, color=None, width=None, leave=False, leave_color=None):
        """ Draw line between two points on canvas
        :p1: point x,y canvas coordinates
        :p2: point x,y canvas coordinates
        :color: line color default: red
        :width: line width in pixels default:1
        :leave: Visually indicate from where we are going
        :leave_color: Use this color for leaving
        """
        self.select_dots.draw_line(p1, p2, color=color, width=width)
        if leave:
            leave_fract = .2
            line_x = (p2[0] - p1[0])*leave_fract
            line_y = (p2[1] - p1[1])*leave_fract
            leave_p_x = p1[0] + line_x
            leave_p_y = p1[1] + line_y
            leave_p = (leave_p_x, leave_p_y)
            if leave_color is None:
                leave_color = "red"
            self.select_dots.draw_line(p1, leave_p, color=leave_color, width=2, arrow=LAST)
 
    def draw_outline(self, sq, color=None, width=None):
        self.select_dots.draw_outline(sq=sq, color=color, width=width)
        
           
    def get_square(self, loc):
        """ Get chess square part
        :loc: if string  - letter a-h, number 1-8  algeraic chess Notation
                if tuple - (file index (0-7 for a-h, row index 0-7 for 1-8))
        :returns: square (SelectRegion or subclass)
        """
        col_index, row_index = loc2tuple(loc)
        dot_row = self.select_dots.nrows - row_index
        dot_col = col_index + 1
        part = self.select_dots.get_part(type='region', row=dot_row, col=dot_col)
        return part
                
    
    def label_square(self, loc, label=None):
        """ Label board square
        :loc: location
        :label: text to place in square default: number
        """
        loc = loc2tuple(loc)
        ci, ri = loc[0], loc[1]
        sq = self.get_square((ci,ri))
        if label is None:
            self.label_number += 1
            label = f"{self.label_number:2d}"
        sq.add_centered_text(text=label)
        

    def set_piece(self, piece, loc=None):
        """ Set piece on board
        :piece: str - [PpNnBbRrQqKk][algebraic location]?
        :loc: str - algebraic location
        """
        pstr = ''
        if isinstance(piece, str):
            m = re.match(r'(^[PpNnBbRrQqKk])([a-h][1-8])?$', piece)
            if m is not None:
                pstr = m.group(1)
                locstr = m.group(2)
                if locstr is not None:
                    loc = self.loc2tuple(locstr)
                else:
                    loc = self.loc2tuple(loc)
            else:
                raise SelectError("Unrecognized piece string:'{}'".format(piece))
            
        else:
            raise SelectError("Piece is not a string {}".format(piece))        
        if SlTrace.trace("set_piece"):
            SlTrace.lg(f"set_piece {piece} at {self.loc2desc(loc)}") 

        if not self.is_empty(loc):
            raise SelectError("Tried to place {} in nonempty square {}"
                             .format(piece, self.loc2desc(loc))) 
           
        self.squares[loc[0]][loc[1]] = pstr
        self.nempty -= 1        


    def is_empty(self, loc):
        """ Check if square is empty (unoccupied)
        """
        loc = self.loc2tuple(loc)
        if self.squares[loc[0]][loc[1]] == "":
            return True
        
        return False
        

    def get_square_loc(self, sq=None, let=True):
        """ Return square's location
        :sq: square
        :let: True - return letters algebraic notation
                False - return (col,row) tuple
        :returns: square location
        """
        dot_row = sq.get_row()
        dot_col = sq.get_col()
        row_index = self.select_dots.nrows - dot_row
        col_index = dot_col - 1
        
        if let:
            return self.tuple2desc((col_index,row_index))
        
        return (col_index, row_index)

    def contents(self, loc):
        """ Get square contents
        :loc: location
        """
        loc = self.loc2tuple(loc)
        return self.squares[loc[0]][loc[1]]
                            
                                
    def display(self):
        """ Display chess board current state
        """
        self.select_dots.display()
        

    def path_desc(self, path):
        """ Generate string with path description
        :path: list of loc descriptions
        :returns: string of path
        """
        path_str = ""
        for loc in path:
            if path_str != "":
                path_str += " "
            desc = self.loc2desc(loc)
            path_str += desc 
        return path_str

display_path = ChessBoardDisplay.display_path

#########################################################################
#          Self Test                                                    #
#########################################################################
if __name__ == "__main__":
    # root window created. Here, that would be the only window, but
    # you can later have windows within windows.
    #SlTrace.setFlags("display")
    
    mw = Tk()
    def user_exit():
        print("user_exit")
        exit()
        
    SlTrace.setProps()
    SlTrace.setFlags("")
    width = 400
    height = 400    
    
    #creation of board
    cb = ChessBoard()
    cbd = ChessBoardDisplay(mw=mw, board=cb)
    cbd.display()
    
    sq = cbd.get_square('a1')
    sq.set_color('pink')
    sq.display()
    
    
    
    sq = cbd.get_square('b2')
    sq.set_color('blue')
    sq.display()
    
    
    sq = cbd.get_square('e5')
    sq.set_color('green')
    sq.display()
    
        
    sq = cbd.get_square('h7')
    sq.set_color('yellow')
    sq.display()
    
    pieces = ['R','N','B', 'Q', 'K', 'r','n','b', 'q', 'k']
    ip = 0
    for ri in range(8):
        for ci in range(8):
            sq = cbd.get_square((ci,ri))
            c1=chr(ci+ord('a'))
            c2=chr(ri+ord('1'))
            sq.add_centered_text(text=c1+c2)
            if (ci+ri)%2 == 1:
                if ip >= len(pieces):
                    ip = 0
                sq.add_centered_text(ChessPiece.desc(pieces[ip]))
                ip += 1
            sq.display()
    mw.mainloop()  

