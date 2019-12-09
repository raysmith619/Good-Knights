# chess_board_display.py    26-Oct-2019    crs Split display from chess_board.py/ChessBoard

from tkinter import *
from enum import Enum
import re


from select_dots import SelectDots
from select_trace import SlTrace
from select_error import SelectError

from numpy import rank


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


class ChessMove:
    def __init__(self, piece=None, dest=None, orig=None):
        """ Chess move
        :piece: chess piece
        :dest: move destination loc
        :orig: origin default: determined by piece & dest
        """
        self.piece = piece
        self.dest = dest 
        self.orig = orig

"""
Simple chess board
display is not present so operations can
be optimized for speed.
"""
class ChessBoard:
    ncol = 8
    nrow = 8
    tracking_path = []
    track_all_path = False
    board_picts_mw = []
                    
    @classmethod
    def tuple2desc(cls, tp):
        """ Convert ic,ir tuple to description string
        return 
        :tp: (ic,ir) tuple
        :returns: algebraic description string
        """
        col_index,row_index = tp[0],tp[1]
        c1=chr(col_index + ord('a'))
        c2=chr(row_index + ord('1'))
        loc_str = c1+c2
        return loc_str
    
    @classmethod
    def CBloc2tuple(cls, loc):
        return cls.board.loc2tuple(loc)


    @classmethod
    def CBpath_desc(cls, path):
        """ Generate string with path description
        :path: list of loc descriptions
        :returns: string of path
        """
        return cls.board.path_desc(path)


    @classmethod
    def CBsquares_list(cls, locs):
        """ Generate string with compressed
        square listing a1,a2,...a8 => a1-8
        :locs: list of loc descriptions
        :returns: string of squares
        """
        return cls.board.squares_list(locs)

    @classmethod
    def CBpath_dups(cls, path, logit=True):
        """ Log path duplications(counts)
        :path: path list
        :logit: if True list path with dup count, in two lines
        :returns: True if dups
        """
        counts = {}
        dup_count = 0
        for move in path:
            move_desc = cls.loc2desc(move)
            if move_desc not in counts:
                counts[move_desc] = 1
            else:
                counts[move_desc] += 1
                dup_count += 1
        if dup_count == 0:
            return False
        
        if logit:
            pth1 = ""   # first line (dup counts)
            pth2 = ""   # second line (path desc)
            SlTrace.lg("path duplication count: {:d}".format(dup_count))
            for move in path:
                move_desc = cls.loc2desc(move)
                ncount = counts[move_desc]
                if pth1 != "":
                    pth1 += " "
                    pth2 += " "
                if ncount > 1:
                    pth1 += "{:2d}".format(ncount)
                else:
                    pth1 += "{:2s}".format("")
                pth2 += "{:2s}".format(move_desc)
            SlTrace.lg(" {}".format(pth1))
            SlTrace.lg(" {}".format(pth2))
            pass
        return True            
                
                
    def __init__(self,
                base_board=None,
                nrow=8,
                ncol=8,
                 ):
        self.label_number = 0               # Number for default square labeling
        if base_board is not None:
            self.nrow = base_board.nrow
            self.ncol = base_board.ncol
            self.nempty = base_board.nempty
            self.copy_squares(self, base_board)
        else:
            self.nrow = nrow
            self.ncol = ncol
            self.squares = self.create_squares()
            self.nempty = nrow*ncol
        ChessBoard.board = self             # Set current board in class


    def get_legal_moves(self, piece=None, loc=None):
        """ Get legal moves for given piece, from loc
        :piece: piece to move default: Knight
        :loc: location str or tuple
        :returns: list of tuples for legal moves
        """
        loc = self.loc2tuple(loc)
        return self.get_knight_moves(loc)


    def get_knight_moves(self, loc=None, only_empty=False):
        """ Get legal moves for given piece, from loc
        :piece: piece to move default: Knight
        :loc: location str or tuple
        :only_empty: True-> only consider empty squares
        :returns: list of tuples for legal moves
        """

        nrow = self.nrow
        ncol = self.ncol
        col_index, row_index = self.loc2tuple(loc)
        if col_index < 0 or col_index >= ncol:
            raise SelectError("get_knight_moves: col_index {:d} is out of bounds".format(col_index))
        
        if row_index < 0 or row_index >= nrow:
            raise SelectError("get_knight_moves: row_index {:d} is out of bounds".format(row_index))
        
        pbs = []
        ic,ir = col_index-2,row_index+1         # (1)
        if ic >= 0 and ir < nrow:
            pbs.append((ic,ir))
        ic,ir = col_index-1,row_index+2         # (2)
        if ic >= 0 and ir < nrow:
            pbs.append((ic,ir))
        ic,ir = col_index+1,row_index+2         # (3)
        if ic < ncol and ir < nrow:
            pbs.append((ic,ir))
        ic,ir = col_index+2,row_index+1         # (4)
        if ic < ncol and ir < nrow:
            pbs.append((ic,ir))
        ic,ir = col_index+2,row_index-1         # (5)
        if ic < ncol and ir >= 0:
            pbs.append((ic,ir))
        ic,ir = col_index+1,row_index-2         # (6)
        if ic < ncol and ir >= 0:
            pbs.append((ic,ir))
        ic,ir = col_index-1,row_index-2         # (7)
        if ic >= 0 and ir >=0:
            pbs.append((ic,ir))
        ic,ir = col_index-2, row_index-1        # (8)
        if ic >= 0 and ir >= 0:
            pbs.append((ic,ir))
        if only_empty:
            epbs = []
            for loc in pbs:
                if self.is_empty(loc):
                    epbs.append(loc)
            return epbs
        
        return pbs


    def is_neighbor(self, loc, loc2):
        """ Check if one move away
        :loc: location of us
        :loc2: location of candidate neighbor
        :returns: True if is neighbor
        """
        moves = self.get_knight_moves(loc)
        if self.loc2tuple(loc2) in moves:
            return True
        
        return False


    def clear_loc(self, loc=None):
        """ Clear square to empty
        """
        loc = self.loc2tuple(loc)
        ic,ir = loc[0],loc[1]
        self.squares[ir][ic] = ""
        self.nempty += 1        
                    
    def loc2desc(self, loc):
        """ Convert loc (string or loc) to description string
        :loc: Location specifier tuple (ir, ic) or str (file
        :returns: algebraic description string
        """
        tup = self.loc2tuple(loc)
        ic,ir = tup[0], tup[1]
        if self.ncol > 8 or self.nrow > 8:
            desc = f"C{ic}R{ir}"
        else:
            c1=chr(ic + ord('a'))
            c2=chr(ir + ord('1'))
            desc =  c1+c2
        return desc
    
    def loc2tuple(self, loc):
        """ Convert location(string specification or loc tuple) to tuple(loc specification)
        :loc: if string:
                1. if first character is "C" form is C(\d+)R(\d+) for column number, row number
                2. if letter a-h, number 1-8  algeraic chess Notation
              if tuple - (column index, row index) if ncol AND nrow <= 8 (0-7 for a-h, row index 0-7 for 1-8))
                      else column index = "C" column number - 1 row index = "R" row number - 1
        """
        if isinstance(loc, str):
            if self.ncol > 8 or self.nrow > 8:
                if len(str) < 4:
                    raise SelectError(f"loc2tp: loc{loc} to short for form CnRn")
                m = re.match(r"C(\d+)R(\d+)", loc)
                if not m:
                    raise SelectError(f"loc2tp: loc{loc} to not of the form CnRn")
                ic = int(m.group(1))
                ir = int(m.group(2))
            else:
                if len(loc) != 2:
                    raise SelectError(f"Unrecognized notation: '{loc}' not 2 chars")
                col_let = loc[0].lower()
                ic = ord(col_let) - ord('a')
                row_let = loc[1]
                ir = int(row_let) - 1
        else:
            ic = loc[0]
            ir = loc[1]
        if ic < 0 or ic >= self.ncol:
            raise SelectError(f"{loc} col index {ic} is out of range[0,{self.ncol})")
        if ir < 0 or ir >= self.nrow:
            raise SelectError(f"{loc} row index {ir} is out of range[0,{self.nrow})")

        return (ic,ir)

    def path_desc(self, path):
        """ Generate string with path description
        :path: list of locs loc descriptors
        :returns: string of path
        """
        path_str = ""
        for loc in path:
            if path_str != "":
                path_str += " "
            desc = self.loc2desc(loc)
            path_str += desc 
        return path_str

    def squares_list(self, locs):
        """ Generate string with compressed
        square listing a1,a2,...a8 => a1-8
        :locs: list of loc descriptions
        :returns: string of squares
        TBD - only nrow,ncol <= 8 supported currently
        """
        path_str = self.path_desc(locs)
        path_squares = path_str.split()
        squares = sorted(path_squares)
        
        cpl = ""
        cur_file = None
        cur_rank = None
        cur_first_rank = None
        cur_last_rank = None
        for sq in squares:
            file = sq[0]
            rank = int(sq[1])
            if cur_file is None or file != cur_file:
                if cur_last_rank is not None and cur_last_rank != cur_first_rank:
                    cpl += f"-{cur_last_rank}"
                    cur_last_rank = None
                if cpl != "":
                    cpl += " "
                cur_file = file
                cur_rank = rank
                cur_first_rank = rank
                cur_last_rank = rank
                cpl +=  f"{cur_file}{cur_rank}"
                continue
            if cur_last_rank is not None and rank == cur_last_rank+1:
                cur_last_rank += 1
                continue
                
            if cur_last_rank is not None and cur_last_rank != cur_first_rank:
                cpl += f"-{cur_last_rank}"
            cur_file = file
            cur_rank = cur_last_rank = rank
            if cpl != "":
                cpl += " "
            cpl +=   f"{cur_file}{cur_rank}"
        if cur_last_rank is not None and cur_last_rank != cur_first_rank:
            cpl += f"-{cur_last_rank}"
        return cpl
        

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
                raise SelectError(f"Unrecognized piece string:'{piece}'")
            
        else:
            raise SelectError(f"Piece({piece}) is not a string")        
        if SlTrace.trace("set_piece"):
            SlTrace.lg(f"set_piece {piece} at {self.loc2desc(loc)}") 

        loc = self.loc2tuple(loc)      # Support str or tuple
        if not self.is_empty(loc):
            raise SelectError(f"Tried to place {piece} in nonempty square {self.loc2desc(loc)}") 
        ic = loc[0]
        ir = loc[1]   
        self.squares[ir][ic] = pstr
        self.nempty -= 1        


    def is_empty(self, loc):
        """ Check if square is empty (unoccupied)
        """
        loc = self.loc2tuple(loc)
        if len(loc) < 2:
            SlTrace.lg(f"loc{loc} to short")
            return False
        ic = loc[0]
        ir = loc[1]
        if ic >= self.ncol:
            SlTrace.lg(f"is_empty: ic({ic}) >= ncol({self.ncol}) out of range")
            return False
        
        if ir >= self.nrow:
            SlTrace.lg(f"is_empty: ir({ir}) >= nrow({self.nrow}) out of range")
            return False
        
        if self.squares[ir][ic] == "":
            return True
        
        return False


    def is_board_full(self):
        if self.nempty <= 0:
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
        return self.squares[ir][ic]


    def create_squares(self):
        """ Initialize set of squares
        :returns: set of empty squares
        """
        squares = [['' for ic in range(self.ncol)] for ir in range(self.nrow)]
        return squares


    def copy_squares(self, dest=None, src=None):
        """ Copy squares contents
        :dest: destination board
        :src: source board
        """
        if not hasattr(dest, "squares"):
            dest.squares = src.create_squares()
            
        if dest.nrow != src.nrow:
            raise SelectError(f"copy_squares: dest: nrow:{dest.nrow} != src: nrow:{src.nrow})")
        
        if dest.ncol != src.ncol:
            raise SelectError(f"copy_squares: dest: ncol:{dest.ncol} != src: ncol:{src.ncol})")
        
        if len(dest.squares) != len(src.squares):
            raise SelectError(f"copy_squares len(dest.sqares({len(dest.squares)} != len(src.squares)({len(src.squares)}")
        if len(dest.squares[0]) != len(src.squares[0]):
            raise SelectError(f"copy_squares len(dest.sqares[0])({len(dest.squares[0])}) != len(src.squares[0])({len(src.squares[0])})")
       
        for ir in range(dest.nrow):
            for ic in range(dest.ncol):
                try:
                    dest.squares[ir][ic] = src.squares[ir][ic]
                except:
                    raise SelectError(f"copy_squares: assignment error:ir={ir} ic={ic}")



loc2desc = ChessBoard.loc2desc 
loc2tuple = ChessBoard.loc2tuple 
path_desc = ChessBoard.path_desc
squares_list = ChessBoard.squares_list
 
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
    #creation of an instance
    cB = ChessBoard()
    cb2 = ChessBoard()
    for ic in range(8):
        for ir in range(8):
            start_loc = (ir,ic)
            SlTrace.lg(f"\n Start: {cb2.loc2desc(start_loc)}")
            for move in cb2.get_legal_moves(loc=start_loc):
                SlTrace.lg(f"    move:{cb2.loc2desc(move)}")

