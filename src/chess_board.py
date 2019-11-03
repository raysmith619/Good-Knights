# chess_board_display.py    26-Oct-2019    crs Split display from chess_board.py/ChessBoard

from tkinter import *
from enum import Enum
import re


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
    ncols = 8
    nrows = 8
    tracking_path = []
    track_all_path = False
    board_picts_mw = []
                    
    @classmethod
    def tuple2desc(cls, tp):
        """ Convert ci,ri tuple to description string
        :tp: (ci,ri) tuple
        :returns: algebraic description string
        """
        col_index,row_index = tp[0],tp[1]
        c1=chr(col_index + ord('a'))
        c2=chr(row_index + ord('1'))
        loc_str = c1+c2
        return loc_str
    
    @classmethod
    def loc2tuple(cls, loc):
        """ Convert location to tuple
        :loc: if string  - letter a-h, number 1-8  algeraic chess Notation
                if tuple - (file index (0-7 for a-h, row index 0-7 for 1-8))
        """
        if isinstance(loc, str):
            if len(loc) != 2:
                raise SelectError("Unrecognized notation not 2 chars: {}".format(loc))
            col_let = loc[0].lower()
            col_index = ord(col_let) - ord('a')
            row_let = loc[1]
            row_index = int(row_let) - 1
        else:
            col_index = loc[0]
            row_index = loc[1]
        if col_index < 0 or col_index >= cls.ncols:
            raise SelectError(f"{loc} col index {col_index:d} is out of range")
        if row_index < 0 or row_index >= cls.nrows:
            raise SelectError(f"{loc} row index {row_index:d} is out of range")
        return (col_index, row_index)
    
    @classmethod
    def loc2desc(cls, loc):
        """ Get location description
        :loc: location
        """
        loc = cls.loc2tuple(loc)
        return cls.tuple2desc(loc)


    @classmethod
    def path_desc(cls, path):
        """ Generate string with path description
        :path: list of loc descriptions
        :returns: string of path
        """
        path_str = ""
        for loc in path:
            if path_str != "":
                path_str += " "
            desc = cls.loc2desc(loc)
            path_str += desc 
        return path_str

    @classmethod
    def path_dups(cls, path, logit=True):
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
                nrows=8,
                ncols=8,
                 ):
        self.label_number = 0               # Number for default square labeling
        self.squares = [['' for ri in range(nrows)] for ci in range(ncols)]
        if base_board is not None:
            nrows = base_board.nrows
            ncols = base_board.ncols
            self.nempty = base_board.nempty
            for ri in range(nrows):
                for ci in range(ncols):
                    self.squares[ri][ci] = base_board.squares[ri][ci]
        else:
            self.nempty = nrows*ncols
        self.nrows = nrows
        self.ncols = ncols


    def get_legal_moves(self, piece=None, loc=None):
        """ Get legal moves for given piece, from loc
        :piece: piece to move default: Knight
        :loc: location str or tuple
        :returns: list of tuples for legal moves
        """
        loc = self.loc2tuple(loc)
        return self.get_knight_moves(loc)


    def get_knight_moves(self, loc=None):
        """ Get legal moves for given piece, from loc
        :piece: piece to move default: Knight
        :loc: location str or tuple
        :returns: list of tuples for legal moves
        """

        nrows = self.nrows
        ncols = self.ncols
        col_index, row_index = self.loc2tuple(loc)
        if col_index < 0 or col_index >= ncols:
            raise SelectError("get_knight_moves: col_index {:d} is out of bounds".format(col_index))
        
        if row_index < 0 or row_index >= nrows:
            raise SelectError("get_knight_moves: row_index {:d} is out of bounds".format(row_index))
        
        pbs = []
        ci,ri = col_index-2,row_index+1         # (1)
        if ci >= 0 and ri < nrows:
            pbs.append((ci,ri))
        ci,ri = col_index-1,row_index+2         # (2)
        if ci >= 0 and ri < nrows:
            pbs.append((ci,ri))
        ci,ri = col_index+1,row_index+2         # (3)
        if ci < ncols and ri < nrows:
            pbs.append((ci,ri))
        ci,ri = col_index+2,row_index+1         # (4)
        if ci < ncols and ri < nrows:
            pbs.append((ci,ri))
        ci,ri = col_index+2,row_index-1         # (5)
        if ci < ncols and ri >= 0:
            pbs.append((ci,ri))
        ci,ri = col_index+1,row_index-2         # (6)
        if ci < ncols and ri >= 0:
            pbs.append((ci,ri))
        ci,ri = col_index-1,row_index-2         # (7)
        if ci >= 0 and ri >=0:
            pbs.append((ci,ri))
        ci,ri = col_index-2, row_index-1        # (8)
        if ci >= 0 and ri >= 0:
            pbs.append((ci,ri))
        return pbs


    def is_neighbor(self, loc, loc2):
        """ Check if one move away
        :loc: location of us
        :loc2: location of candidate neighbor
        :returns: True if is neighbor
        """
        moves = self.get_knight_moves(loc)
        if loc2 in moves:
            return True
        
        return False
        

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
            raise SelectError(f"Tried to place {piece} in nonempty square {self.loc2desc(loc)}") 
           
        self.squares[loc[0]][loc[1]] = pstr
        self.nempty -= 1        


    def is_empty(self, loc):
        """ Check if square is empty (unoccupied)
        """
        loc = self.loc2tuple(loc)
        if self.squares[loc[0]][loc[1]] == "":
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
    for ci in range(8):
        for ri in range(8):
            start_loc = (ri,ci)
            SlTrace.lg(f"\n Start: {cb2.loc2desc(start_loc)}")
            for move in cb2.get_legal_moves(loc=start_loc):
                SlTrace.lg(f"    move:{cb2.loc2desc(move)}")

