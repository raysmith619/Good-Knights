# chess_board_display.py    26-Oct-2019    crs Split display from chess_board.py/ChessBoard

from tkinter import *
from enum import Enum
import re

from chess_board import ChessBoard
from select_dots import SelectDots
from select_trace import SlTrace
from select_error import SelectError

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
    ncol = 8
    nrow = 8
    tracking_path = []
    track_all_path = False
    board_picts_wm = []

    @classmethod
    def display_path(cls, path,
                     desc=None, nrow=8, ncol=8,
                     width=400, height=400):
        """ Display board with path squares labeled
        :desc: text description
        :path: list of squares in order
        returns ChssBoardDisplay of displayed board
        """
        if not hasattr(cls, 'wm'):
            cls.wm = Tk()
        wm_base = cls.wm
        wm = Toplevel(wm_base)
        wm_base.withdraw() 
        wm.geometry("%dx%d" % (width, height))
        frame = Frame(wm, width=width, height=height, bg="", colormap="new")
        frame.pack(fill=BOTH, expand=True)
        wm.title(desc) 
        
        #creation of an instance
        cb = ChessBoard(nrow=nrow, ncol=ncol)
        cbd = ChessBoardDisplay(wm=wm, frame=frame, board=cb, path=path,
                                desc=desc,
                                width=width, height=height, nrow=nrow, ncol=ncol)
        if path is None:
            SlTrace.lg("No path")
            return
            
        for loc in path:
            loc = cb.loc2tuple(loc)
            cbd.label_square(loc)
        cbd.display()
        wd = 7
        if len(path) == 0:
            return
        
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
            loc = cb.loc2tuple(loc)
            if prev_loc is not None:
                cbd.display_connected_moves(loc, prev_loc)
            prev_loc = loc
        wm.lift()
        cbd.update_display()
        return cbd
        
    @classmethod
    def update_display(cls):
        wm = cls.wm
        wm.update_idletasks()
        wm.update()

    @classmethod
    def mainloop(cls):
        wm = cls.wm
        wm.mainloop()
        
    
    @classmethod
    def set_path_tracking(cls, wm=None, display_path_board=False,
                          track_all_path=False, tracking_path=[]):
        """ Set / Reset path tracking
        :wm: Tk main window default: create one
        :track_all_path: track all findings default: only growth
        :tracking_path: latest path default: empty
        """
        if wm is None:
            wm = Tk()
        cls.wm = wm
        cls.display_path_board = display_path_board
        cls.tracking_path = tracking_path
        cls.track_all_path = track_all_path
                
                
    def __init__(self,
                frame=None, wm=None,
                desc="",
                x=None, y=None,
                width=400, height=400,     # REQUIRED, if window not expanded
                board=None,
                move_time = .5,
                path=None,
                nrow=8,
                ncol=8,
                ):
        """ Set up board display
        :frame: if one
        :wm: if one
        :desc: description if one
        :x: board x position    default: tkinter default
        :y: board y position
        :width: board width default: 400 pixels
        :height: board height default: 400 pixels
        :board: ChessBoard default: created
        :path: path to display
        :nrow: number of rows default: 8
        :ncol: number of columns default: 8
        """
        self.label_number = 0               # Number for default square labeling
        self.desc = desc
        if board is None:
            board = ChessBoard(nrow=nrow, ncol=ncol)
        self.path = path                    # Path, if associated, may be placed here
        self.board = board    
        self.width = width
        self.height = height
        if board is not None:
            nrow = board.nrow
            ncol = board.ncol
        self.nrow = nrow
        self.ncol = ncol
        if wm is None:
            wm = Tk()
        self.wm = wm
        width = int(width)
        height = int(height)
        geo = f"{width}x{height}"
        if x is not None or y is not None:
            geo += f"+{x}+{y}"
        wm.geometry(geo)
        if frame is None:
            frame = Frame(master=wm, width=width, height=height, bg="", colormap="new")
            frame.pack(fill=BOTH, expand=YES)
        self.frame = frame
        select_dots = self.create_board(frame, wm, width=width, height=height,
                          nrow=nrow, ncol=ncol)
        self.select_dots = select_dots
        self.prev_loc = None                # previous move location for path viewing
        self.move_time = move_time
        self.display_move_stack = []        # (loc, line)
        self.display_move_no = 0
        
    def create_board(self, frame=None, wm=None,
                     nrow=None, ncol=None,
                     width=None, height=None):
        
        select_dots = SelectDots(frame, wm,
                        width=width, height=height,     # REQUIRED, if window not expanded
                        nrows=nrow, ncols=ncol,
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
        if self.wm is not None:
            self.wm.destroy()
            self.wm = None
            
    def resize(self, width=None, height=None):
        select_dots = self.create_board(self.frame, self.wm, width=width, height=height,
                                         nrow=self.nrow, ncol=self.ncol)
        if hasattr(self, "select_dots") and self.select_dots is not None:
            self.select_dots.destroy()    
        self.select_dots = select_dots

    def add_centered_text(self, loc, text, x=None, y=None,
                          font_name=None,
                          color=None, color_bg=None,
                          height=None, width=None, display=True):
        
        sq = self.get_square(loc)
        sq.add_centered_text(text=text, x=x, y=y,
                             font_name=font_name,
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
        :returns: list of canvas line objects
        """
        ls = []
        l1 = self.select_dots.draw_line(p1, p2, color=color, width=width)
        ls.append(l1)
        if leave:
            leave_fract = .2
            line_x = (p2[0] - p1[0])*leave_fract
            line_y = (p2[1] - p1[1])*leave_fract
            leave_p_x = p1[0] + line_x
            leave_p_y = p1[1] + line_y
            leave_p = (leave_p_x, leave_p_y)
            if leave_color is None:
                leave_color = "red"
            l2 = self.select_dots.draw_line(p1, leave_p, color=leave_color, width=2, arrow=LAST)
            ls.append(l2)
        return ls
 
    def draw_outline(self, sq, color=None, width=None):
        self.select_dots.draw_outline(sq=sq, color=color, width=width)
        
    def get_square_size(self):
        """ Return (w,h) size in pixels
            (0,0) if no squares
            ASSUMES vertical allignment
        """
        if self.ncol == 0 or self.nrow == 0:
            return (0,0)
        
        sq = self.get_square((0,0))
        points = sq.get_points()
        if len(points) != 2:
            raise SelectError(f"square(region) has {len(points)}")
        
        c1 = points[0]          # corners
        c3 = points[1]
        w = abs(c3[0]-c1[0])
        h = abs(c3[1]-c1[1])
        return (w,h)    

                   
    def get_square(self, loc):
        """ Get chess square part
        :loc: if string  - letter a-h, number 1-8  algeraic chess Notation
                if tuple - (file index (0-7 for a-h, row index 0-7 for 1-8))
        :returns: square (SelectRegion or subclass)
        """
        col_index, row_index = self.loc2tuple(loc)
        dot_row = self.select_dots.nrows - row_index
        dot_col = col_index + 1
        part = self.select_dots.get_part(type='region', row=dot_row, col=dot_col)
        return part
                
    
    def label_square(self, loc, label=None):
        """ Label board square
        :loc: location
        :label: text to place in square default: number
        """
        loc = self.loc2tuple(loc)
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
            raise SelectError(f"Piece is not a string {piece}")        
        if SlTrace.trace("set_piece"):
            SlTrace.lg(f"set_piece {piece} at {self.loc2desc(loc)}") 

        if not self.is_empty(loc):
            raise SelectError("Tried to place {} in nonempty square {}"
                             .format(piece, self.loc2desc(loc))) 
        ic,ir = loc[0],loc[1]
        self.board.squares[ir][ic] = pstr
        self.board.nempty -= 1        


    def is_empty(self, loc):
        """ Check if square is empty (unoccupied)
        """
        loc = self.loc2tuple(loc)
        ic = loc[0]
        ir = loc[1]
        if self.board.squares[ir][ic] == "":
            return True
        
        return False
    def set_empty(self, loc):
        """ Set as empty
        :loc: square on board
        """
        loc = self.loc2tuple(loc)
        ic = loc[0]
        ir = loc[1]
        self.board.squares[ir][ic] = ""
        

    def get_square_loc(self, sq=None, let=True):
        """ Return square's location
        :sq: square
        :let: True - return letters algebraic notation
                False - return (col,row) tuple
        :returns: square location
        """
        dot_row = sq.get_row()
        dot_col = sq.get_col()
        row_index = self.select_dots.nrow - dot_row
        col_index = dot_col - 1
        
        if let:
            return self.tuple2desc((col_index,row_index))
        
        return (col_index, row_index)

    def contents(self, loc):
        """ Get square contents
        :loc: location
        """
        loc = self.loc2tuple(loc)
        ic,ir = loc[0],loc[1]
        return self.board.squares[ir][ic]

    def display_connected_moves(self, loc=None, prev_loc=None, color=None,
                                width=None, leave=None, leave_color=None):
        """ Display connected move locations such as a path
        :loc: move destination
        :prev_loc: previous move destination default: None
        :color: line color
        :width: line thickness in pixels
        :leave: show leaving point
        :leave_color: color of leaving accent default same as color
        :returns: list of canvas line objects
        """
        
        if prev_loc is None:
            return []

        if leave_color is None:
            leave_color = color
        sq1 = self.get_square(prev_loc)
        p1 = sq1.get_center()
        sq2 = self.get_square(loc)
        p2 = sq2.get_center()
        return self.draw_line(p1,p2, color=color, width=width,
                              leave=leave, leave_color=leave_color)

                                
    def display(self):
        """ Display chess board current state
        """
        self.select_dots.display()

    def display_move(self, loc=None, piece=None):
        """ Display move
        :loc: destination square
        :piece: piece to move default "N"
        """
        self.display_move_no += 1
        self.update_display()
        if piece is None:
            piece = "N"
        if not self.is_empty(loc):
            sq = self.get_square(loc)
            self.draw_outline(sq, color="pink", width=4)
            return
        
        self.set_piece(piece, loc=loc)
        self.add_centered_text(loc, text=ChessPiece.desc(piece),
                          color="black")
        self.add_centered_text(loc, text=f" {self.display_move_no}", x=15, y=15)
        connect_tags = []
        if self.prev_loc is not None:
            connect_tags = self.display_connected_moves(loc=loc, prev_loc=self.prev_loc)
        self.prev_loc = loc
        self.display_move_stack.append((loc, connect_tags, self.display_move_no))
        self.wm.after(int(1000*self.move_time))
        self.update_display()

    def undisplay_move(self):
        """ Remove previous displayed move
        """
        if len(self.display_move_stack) > 0:
            loc, connect_tags, _ = self.display_move_stack.pop()
            sq = self.get_square(loc)
            sq.display_clear()
            self.clear_display_canvas(connect_tags)
            ic,ir = loc[0],loc[1]
            self.board.squares[ir][ic] = ""
            self.board.nempty += 1
            if len(self.display_move_stack) > 0 and len(self.display_move_stack[-1]) > 2:
                self.display_move_no = self.display_move_stack[-1][2]       
            self.wm.after(int(1000*self.move_time))
            self.update_display()


    def clear_display_canvas(self, tags):
        """ Remove tag from display canvas
        :tag: canvas object tag
        """
        for tag in tags:
            self.select_dots.canvas.delete(tag)
        
    def loc2desc(self, loc):
        return self.board.loc2desc(loc)

    def loc2tuple(self, loc):
        return self.board.loc2tuple(loc)

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
        
    def update_display(self):
        wm = self.wm
        if wm is None:
            return
        
        wm.update_idletasks()
        wm.update()
     
display_path = ChessBoardDisplay.display_path

#########################################################################
#          Self Test                                                    #
#########################################################################
if __name__ == "__main__":
    # root window created. Here, that would be the only window, but
    # you can later have windows within windows.
    #SlTrace.setFlags("display")
    
    wm = Tk()
    def user_exit():
        print("user_exit")
        exit()
        
    SlTrace.setProps()
    SlTrace.setFlags("")
    width = 400
    height = 400    
    
    #creation of board
    cb = ChessBoard()
    cbd = ChessBoardDisplay(wm=wm, board=cb)
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
    wm.mainloop()  

