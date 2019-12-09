#knights_paths.py
"""
Support searching for knights paths on a chess board calculation
"""
import datetime
import traceback
from select_trace import SlTrace
from select_error import SelectError
from select_timeout import SelectTimeout

from chess_board import ChessBoard
from chess_board_display import ChessBoardDisplay, ChessPiece

loc2desc = ChessBoard.loc2desc 
loc2tuple = ChessBoard.loc2tuple 
path_desc = ChessBoard.path_desc
display_path = ChessBoardDisplay.display_path


""" 
From Stackoverflow.com
"""
import time
def by_first(tp):
    """ Sort helper to pick first tuple element
    """
    return tp[0]

class PathStackEntryDisplayInfo:
    """ Display info, setup in display_move, used in undisplay_move
    """
    def __init__(self, connect_tags=None):
        """ Setup Display info
        :connect_tags: canvas tags for connection lines
        """
        if connect_tags is None:
            connect_tags = []
        self.connect_tags = connect_tags
        

class PathStackEntry:
    """ move stack, containing information to suggest next move,
    display move, etc.
    """
    def __init__(self, piece=None, loc=None, board=None, best_moves=None, display_info=None):
        """ setup path stack entry
        :piece: Chess piece string, e.g. N for black knight default: black knight
        :loc: destination move location
        :board: ChessBoard default: self.board playing board with move in place
        :best_moves: list of follow-on moves in decreasing benefit default: unknown - calculate them
                        next_move_list element: (score, move) where lower is better
        :display_info: display info, used by display_move, undisplay_move
        """
        if piece is  None:
            piece = "N"
        self.piece = piece
        if loc is None:
            raise SelectError("loc missing")
        
        self.loc = loc
        if board is None:
            board = self.board
        self.board = board
        self.best_moves = best_moves
        self.display_info = display_info

        
class KnightsPaths:
    """ Generates knight paths, given starting position
    """
    def __init__(self, board=None, loc=None, closed_tours=False, max_try=None, time_limit=None,
                 backup_limit=500,
                 display_move=False,
                 pW=None,
                 move_time=.5,
                 nrow=None, ncol=None,
                 max_look_ahead=5):
        """ Setup for kight path generation
        Via depth-first search of night moves which traverse board without revisiting any square.
        
        :board: Current chess board, default: generate empty board
        :nrow: number of rows if board not present
        :ncol: number of cols if board not present
        :loc: starting knight position                
        :closed_tours: return only closed tours
        :max_look_ahead: maximum number of moves to look ahead in best move determination
        :max_tries: Number of tries (no more moves) for path default: no max
        :time_Limit: time limit, in seconds to produce a result (return path)
                    default: 5 seconds
        :backup_limit: Number of backups at which we try secondary search start point
        :display_move: True - display move on board
        :pW: control window (PathsWindow)
        :move_time: time to display move default: .5 second
        """
        self.ntry = 0                            # number of tries so far
        self.nmove = 0                           # NUmber of moves, including retries
        self.path_stack = None
        self.max_look_ahead = max_look_ahead
        self.max_try = max_try
        self.is_display_move = display_move
        self.pW = pW
        self.pW = pW
        self.time_begin = datetime.datetime.now()
        self.move_time = move_time
        if board is None:
            board = ChessBoard(ncol=ncol, nrow=nrow)
        self.board = board
        self.ncol = board.ncol
        self.nrow = board.nrow
        self.len_ckt = self.ncol*self.nrow
        self.display_board = None       # Board displaying moves during run
        if self.is_display_move:
            self.display_move_setup()
            time_limit = 99999
        elif time_limit is None:
            time_limit = 1.0
        else:
            time_limit = float(time_limit)
        self.time_limit = time_limit
        self.time_end = self.time_begin + datetime.timedelta(seconds=time_limit)
        self.loc_start = loc
        self.closed_tours = closed_tours
        self.candidate_end_moves = self.get_knight_moves(loc)       # Possible end moves for closed tour
        self.nprune_closed = 0              # count pruning
        self.make_move('N', self.loc_start)
        self.track_level = self.len_ckt
        self.ncomplete_path = 0     # Number of paths found
        self.nbackup = 0           # Number of backups, not including non-tour paths
        self.ntrack_ntie = 0
        self.ntie = 0
        self.last_complete_path = None  # Recording non-tours, iff looking for one
        self.is_complete_tour = False
        self.is_closed_tour = False
        self.backup_limit = backup_limit
        self.nprune_closed = 0
        self.widen_level = 1            # Level to backup for widening
        self.is_change_tour = False        # Short circuit operation
        self.is_stop_gen = False           # Short circuit operation
        self.display_first_loc = loc
              
    ###@timeout(time_limit)
    def build_path_stack(self):
        """ Agument path_stack with a next move
        :returns: True if successful, False if no such path found
        """
        
        board = self.board
        len_ckt = self.len_ckt
        
        while True:
            self.time_check()
            ###board.update_display()      # Don't let display block
            len_stk = len(self.path_stack)
            
            if len_stk == 0:
                return False                # No paths
            
            if len_stk == len_ckt:
                if SlTrace.trace("complete_paths"):
                    self.display_stack_path("complete_paths")
                self.ncomplete_path += 1             # Count all complete paths
                self.is_complete_tour = True
                if self.closed_tours:
                    start_loc = self.path_stack[0].loc
                    end_loc = self.path_stack[-1].loc
                    if board.is_neighbor(start_loc, end_loc):
                        self.is_closed_tour = True
                        return True
                    
                    self.last_complete_path = self.path_stack_path()
                    
                    if SlTrace.trace("non-closed"):
                        self.display_stack_path("ignoring non-closed tour {} to {}"
                                                .format(loc2desc(self.path_stack[0].loc),
                                                        loc2desc(self.path_stack[-1].loc)))
                        self.display_stack("non-closed")
                    if self.max_try is not None and self.ntry >= self.max_try:
                        SlTrace.lg(f"Giving up looking for closed tour after {self.ntry:d} tries")
                        return True
                    
                    ###self.backup_move()
                    if self.is_stop_gen or self.is_change_tour:
                        break                       # Short circuit
                    self.widen_search()
                    continue                        # look again
                else:
                    return True
        
            ###if self.path_stack is None or len(self.path_stack) == 0:
            ###    raise SelectError("empty self.path_stack")
            
            if self.operator_action_check():
                if self.is_change_tour:
                    return False
                
                if self.is_stop_gen:
                    return False
                
                continue
            
            if self.next_move():
                return True                         # End of path search
    
            # Continue search
        return False                                # Short circuit
    
    
    def next_move(self):
        """ Execute the next (currenly set) move, updating the path stack
        and displaying move if appropriate
        :returns: True iff at end of path search
        """
        if self.closed_tours:
            self.prune_not_closed()                
        stke = self.path_stack[-1]
        next_move = stke.loc
        board = stke.board
        best_moves = stke.best_moves
        SlTrace.lg(f"best_moves = {best_moves}", "stack_build")
        if best_moves is None:
            SlTrace.lg(f"best_moves tested is None", "stack_build")
            best_moves = self.get_best_moves(board, next_move)
            SlTrace.lg(f"best_moves = {best_moves}", "stack_build")
            SlTrace.lg(f"len(best_moves)={len(best_moves)}", "stack_build")
        if len(best_moves) == 0:
            SlTrace.lg("tested as 0", "stack_build")
            self.ntry += 1
            if SlTrace.trace("no_more_moves"):
                SlTrace.lg("{:d}: No more moves at {} len_stk={:d}"
                           .format(self.ntry, loc2desc(next_move), len_stk))
            if self.max_try is not None and self.ntry > self.max_try:
                SlTrace.lg("Giving up this search")
                return True
            
            if SlTrace.trace("no_more_moves"):
                self.display_stack_path("no_more_moves")
            if (self.last_complete_path is None
                    or len(self.path_stack) > len(self.last_complete_path)):
                self.last_complete_path = self.path_stack_path()
            if len(self.path_stack) <= self.track_level:
                self.track_level = len(self.path_stack)
                if SlTrace.trace("back_off_trace"):
                    if self.track_level > 0:
                        stke = self.path_stack[-1]
                        nxt_move, board, bst_moves = stke.loc, stke.board, stke.best_moves
                        self.board = board
                        SlTrace.lg("back_off_trace stk_len={:d} start={} at {} best_moves={}"
                               .format(self.track_level, loc2desc(self.loc_start),
                                       loc2desc(nxt_move), path_desc(bst_moves)))
                        self.display_stack_path("back_off_trace")
            self.widen_search()
            return False                            # Backup
        else:
            SlTrace.lg(f"len(best_moves)={len(best_moves)} failed test for 0", "stack_build")
        
        follow_move = best_moves.pop(0)
        stke = self.path_stack[-1]
        stke.best_moves = best_moves            # Update best moves
        new_board = ChessBoard(base_board=board)
        self.make_move(loc=follow_move, board=new_board)
        return False

    def time_check(self):
        """ Check for timeout
        """
        now = datetime.datetime.now()
        if now > self.time_end:
            raise SelectTimeout
                
    def destroy(self):
        if self.is_display_move and self.display_board is not None:
            self.display_board.destroy()
            self.display_board = None

    def display_move_setup(self):
        """ Setup for move display
        """
        self.display_board = ChessBoardDisplay(x=600,y=100, width=600, height=600,
                                               board=self.board,
                                               move_time=self.move_time)

    def prune_not_closed(self):
        """ Back up if no closed tour is possible with
        current path_stack.  There can be no closed tour possible
        if the path stack length is at less than the circuit length
        (self.len_ckt) and there is no empty square one knight's
        move away (self.candidate_end_moves) from the starting
        square(self.start_loc).
        """
        if len(self.path_stack) == self.len_ckt:
            return          # Might be done
        
        if self.has_candidate_moves():
            return
            
        self.nprune_closed += 1              # count pruning
        while len(self.path_stack) > 1:
            self.backup_move()
            if self.has_candidate_moves():
                break
            
    
    def has_candidate_moves(self):
        """ Test if any empty candidate end squares for closed tour
        """
        for loc in self.candidate_end_moves:
            if self.is_empty(loc):
                return True      # At least empty candidate
        
        return False
                
        
    def make_move(self, piece=None, loc=None, board=None):
        """ Make top level (visible) move
        :piece: algebraic move default: 'N'
        :loc: location /square
        :board: board default self.board
        """
        self.nmove += 1
        if piece is None:
            piece = 'N'
        if board is None:
            board = self.board
        self.board = board                  # Update board
        if self.path_stack is None:
            self.path_stack = []
        self.path_stack.append(PathStackEntry(loc=loc, board=self.board))
        if SlTrace.trace("stack_grow"):
            SlTrace.lg(f"stk_len:{len(self.path_stack):d} at {loc2desc(loc)}")
        board.set_piece(piece, loc)
        if self.is_display_move:
            self.display_move()
 
    def display_move(self):
        """ Display current move on the path stack
        """
        move_no = len(self.path_stack)   # Use stack len as move number
        if move_no == 0:
            return                  # Nothing to display

        dboard = self.display_board # Display board
        stke = self.path_stack[-1]
        dboard.update_display()
        piece = stke.piece
        if piece is None:
            piece = "N"
        prev_loc = None
        if  move_no > 1:
            prev_loc = self.path_stack[-2].loc
        loc = stke.loc
        if not dboard.is_empty(loc):            # Indicate if square occupied
            sq = dboard.get_square(loc)
            dboard.set_empty(loc)                   # HACK to continue TFD
            dboard.draw_outline(sq, color="pink", width=4)
            ### return                            ### HACK to continue
        
        dboard.set_piece(piece, loc=loc)
        sq_w, sq_h = dboard.get_square_size()
        text_w = text_h = None          # default use default
        if sq_w != 0 and sq_h != 0:
            text_w = sq_w*2
            text_h = sq_h*2
        dboard.add_centered_text(loc, text=ChessPiece.desc(piece),
                          color="black", width=text_w, height=text_h,
                          font_name="Helvetica24")
        dboard.add_centered_text(loc, text=f" {move_no}", x=15, y=15)
        if move_no == 1:
            sq = dboard.get_square(loc)
            sq.draw_outline(color="green", width=4)
            self.display_first_loc = loc
        elif move_no == self.nrow*self.ncol:
            sq = dboard.get_square(loc)
            sq.draw_outline(color="red", width=4)
            if self.is_neighbor(loc, self.display_first_loc):
                dboard.display_connected_moves(loc=self.display_first_loc,
                                               prev_loc=loc,
                                               color= "blue", width=4, leave=True)
        connect_tags = []
        if prev_loc is not None:
            connect_tags = dboard.display_connected_moves(loc=loc, prev_loc=prev_loc, leave=True)
        stke.display_info = PathStackEntryDisplayInfo(connect_tags=connect_tags)
        dboard.wm.after(int(1000*self.move_time))
        dboard.update_display()

    def undisplay_move(self):
        """ Remove previous displayed move
        """
        if len(self.path_stack) == 0:
            return
        
        stke = self.path_stack[-1]
        dboard = self.display_board
        loc = stke.loc
        connect_tags = []
        if stke.display_info is not None:
            connect_tags = stke.display_info.connect_tags
        sq = dboard.get_square(loc)
        sq.display_clear()
        dboard.clear_display_canvas(connect_tags)
        ic,ir = loc[0],loc[1]
        dboard.board.squares[ir][ic] = ""
        dboard.wm.after(int(1000*self.move_time))
        dboard.update_display()

    def display_stack_path(self, desc=None):
        """ Display current path on stack
        :desc: optional description
        """
        if desc is None:
            desc = ""
        path = self.path_stack_path()
        ChessBoardDisplay.display_path(desc, path) 


    def operator_action_check(self):
        """ Check if operator action occurred
        since last operator action
        """
        if not self.is_display_move:
            return False            # No operator checking if no display move
        
        if self.is_change_tour or self.is_stop_gen:
            return True             # Short-circuit operation
        
        pW = self.pW
        if pW is None:
            return False
        
        self.update_display()
        pW.update_display()
        if pW.is_step:
            pW.is_step = False
            pW.is_pause = True
            return True
        
        if pW.is_pause:
            return True
        
        return False
        
        
    def move_check(self):
        """ Check for move progress / pause, step, continue
        Only in effect for display_move
        :returns: True if action was taken and current move should be ignored
        """
        if not self.is_display_move:
            return False
        
        was_paused = self.paused()
        while self.paused():
            self.update_display()
            self.display_board.wm.after(100)

        if self.steped():
            self.pW.is_pause = True     # Reset paused
        if was_paused:
            SlTrace.lg("after pause")
        
    def paused(self):
        pW = self.pW
        if pW is not None and pW.is_pause:
            return True
        
        return False


    def steped(self):
        pW = self.pW
        if pW is not None and pW.is_step:
            return True
        
        return False
    

    def display_stack(self, desc=None, nent=None, display_board=False):
        """ Display current stack
        :desc: optional description
        :nent: number of most recent stack entries default: 10
        :display_board: True - include board display default: False
        """
        if desc is None:
            desc = ""
        if desc != "":
            SlTrace.lg(desc)
        if nent is None:
            nent = 10
        iend = len(self.path_stack) - nent + 1
        if iend < 0:
            iend = 0                    # Limit to top of stack
        for ient in range(len(self.path_stack)-1, iend-1, -1):
            stkent = self.path_stack[ient] 
            next_move, board = stkent[0], stkent[1]
            ktmoves = board.get_knight_moves(next_move)                 # Force new look
            bestmoves = self.order_moves_by_warnsdorff(ktmoves)        # Force new look
            txt = "[{:2d}]: {}  {}".format(ient, loc2desc(next_move), path_desc(bestmoves))
            SlTrace.lg(txt)
        SlTrace.lg()
        if display_board:
            self.display_stack_path(desc)

    
    def get_best_moves(self, board, loc):
        """ Retrieve an ordered list of best moves for piece at loc
        if max_lookahead == -1 ==> just give all legal knight moves
        :board: chess board
        :loc: piece location
        """
        
        if self.max_look_ahead == -1:
            ktmoves = board.get_knight_moves(loc, only_empty=True)
            return ktmoves
        
        ktmoves = board.get_knight_moves(loc)
        best_moves = self.order_moves_by_warnsdorff(board, ktmoves)
        if SlTrace.trace("best_moves"):
            SlTrace.lg(f"best_moves(for {loc2desc(loc)}): {path_desc(best_moves)}")
        return best_moves

    def get_ncomplete_path(self):
        """ Get number of complete paths found so far
        """
        return self.ncomplete_path

    def get_nbackup(self):
        """ Get number of backups (not including non-tour complete paths)
        """
        return self.nbackup

    def get_nmove(self):
        """ Get number of moves (not including non-tour complete paths)
        """
        return self.nmove

    def get_track_level(self):
        """ Get minimum backup stack level
        """
        return self.track_level
    
    
    def is_neighbor(self, loc, loc2, board=None):
        """ Check if one move away
        :loc: location of us
        :loc2: location of candidate neighbor
        :board: current board default: self.board
        :returns: True if is neighbor
        """
        if board is None:
            board = self.board
        return board.is_neighbor(loc, loc2)

    def is_empty(self, loc, board=None):
        """ Check if square is empty (unoccupied)
        """
        if board is None:
            board = self.board
        return board.is_empty(loc)
                    
    def pop_path_stack(self):
        """ return next path, removing it from stack
        :returns: path,if one, else None
        """
        path = self.path_stack_path()
        self.backup_move()
        return path

    def path_stack_path(self):
        """ Returns path on stack
        """
        path = []
        for se in self.path_stack:
            path.append(se.loc)
        return path
    
                   
    def next_path(self):
        """ Get next path
        1. if necessary, build path to nrow*ncol depth
        2. get list of moves from stack
        
        :returns: next path, None if none
        """
        try:
            if not self.build_path_stack():
                return None
            
            path = self.path_stack_path()
            return path
                
        except SelectTimeout:
            t = self.time_limit
            if t is None:
                t = -1
            SlTrace.lg(f"path find timeout({t:.3f} sec)")
            return None

        except BaseException:
            SlTrace.lg("path find exception: {traceback.format_exc()}")
            raise Exception

    

    def order_moves_by_warnsdorff(self, board, moves, max_look_ahead=None):
        """ Order moves by Warnsdorff algorithm (minimum neighbors)
        :board: current board
        :moves: Candidate list of moves
        :max_look_ahead: maximum level look ahead to break ties
                        default: 5
        :returns: list in decreasing order of preference
        """
            
        if len(moves) <= 1:
            return moves[:]

        if max_look_ahead is None:
            max_look_ahead = self.max_look_ahead        
        sorted_move_tuples1 = self.order_moves_by_warnsdorff_1(board, moves)
        if not self.check_order(sorted_move_tuples1):
            SlTrace.lg("Re-sorting warnsdorff_1")
            self.list_tuples(sorted_move_tuples1, desc="to")
            sorted_move_tuples1 = self.sorted_tuples(sorted_move_tuples1)
            self.list_tuples(sorted_move_tuples1, desc="to")
        if max_look_ahead < 2:
            sorted_moves1 = self.moves_from_sorted(sorted_move_tuples1)
            return sorted_moves1
        if SlTrace.trace("track_refine"):
            self.list_tuples(sorted_move_tuples1, desc="before refine")
        sorted_move_tuples = self.order_warn_refine(board, sorted_move_tuples1,
                                                max_look_ahead=max_look_ahead)
        if SlTrace.trace("track_refine"):
            self.list_tuples(sorted_move_tuples, "after refine")
        if not self.check_order(sorted_move_tuples):
            SlTrace.lg("Re-sorting")
            sorted_move_tuples2 = self.sorted_tuples(sorted_move_tuples)
            self.list_tuples(sorted_move_tuples2, desc="to")
            if not self.check_order(sorted_move_tuples2):
                SlTrace.lg("Still not sorted")
            else:
                SlTrace.lg("sorted")
                sorted_move_tuples = sorted_move_tuples2
        self.track_ties(sorted_move_tuples)
        sorted_moves = self.moves_from_sorted(sorted_move_tuples)
        return sorted_moves

    def track_ties(self, sorted_move_tuples):
        """ Keep statistics on number of ties in final best_moves list
        :sorted_move_tuples: tuple: (len(score), move, next_moves)
        :returns: number of ties
        """
        scoreh = {}
        for move_tuple in sorted_move_tuples:
            score = move_tuple[0]
            if score not in scoreh:
                scoreh[score] = 1
            else:
                scoreh[score] += 1
        tieh = {}                   # number of n-way ties
        nties = 0                   # Any duplication
        for score in scoreh:
            ntie = scoreh[score]
            if ntie < 2:
                continue
            if ntie not in tieh:
                tieh[ntie] = 1
            else:
                tieh[ntie] += 1
                tieh[ntie] += 1
        for tie in tieh:
            nties += tieh[tie]-1        # Add the extra past no-tie
        self.ntrack_ntie += 1
        self.ntie += nties
        return nties

    
    def list_tuples(self, tuples, desc=None, end=None):
        if desc is not None:
            SlTrace.lg(desc)
            if end is None:
                end = " "
        for tup in tuples:
            SlTrace.lg("    {} len:{:d}".format(loc2desc(tup[1]), tup[0]))
        if end is not None:
            if end.startswith("-"):
                end = end*25
            SlTrace.lg(end)

    def sorted_tuples(self, move_tuples):
        """ Sort move tuples (len, move, follow_ons) by increasing len
        where len: len_str1 [" " len_str2 " " len_str3 ... ]
        :move_tuples: list of tuples
        """
        aug_tuples = []
        for move_tuple in move_tuples:
            aug_tuples.append((move_tuple[0], move_tuple))
        sorted_aug_tuples = sorted(aug_tuples, key=by_first)
        sorted_move_tuples = []
        for aug_tuple in sorted_aug_tuples:
            sorted_move_tuples.append(aug_tuple[1])
        return sorted_move_tuples

    def check_order(self, sorted_move_tuples):
        if len(sorted_move_tuples) < 2:
            return True
                    
        in_order = True
        prev_tuple = None
        out_of_order_tuple = None
        next_tuple = None           # one after out of order
        prev_len = None 
        for move_tuple in sorted_move_tuples:
            if prev_tuple is not None:
                prev_len = prev_tuple[0]
            list_len = move_tuple[0]
            if prev_len is not None and prev_len > list_len:       # >= to catch ties
                in_order = False
                out_of_order_tuple = prev_tuple
                next_tuple = move_tuple
                if list_len == 0:
                    SlTrace.lg("order len == 0")
                    ### TBDself.draw(desc="order len== 0")
                break
            prev_tuple = move_tuple

        if not in_order:
            if prev_len == list_len:
                SlTrace.lg(f"\nnot strictly ordered tuples: {sorted_move_tuples}")
                return True
            
            if prev_len > list_len:
                for move_tuple in sorted_move_tuples:
                    SlTrace.lg(f"    {move_tuple[1]} len:{move_tuple[0]:d}")
                desc = "???"
                if out_of_order_tuple is not None:
                    oo_move = out_of_order_tuple[1]
                    oo_len = out_of_order_tuple[0]
                    nx_move = next_tuple[1]
                    nx_len = next_tuple[0]
                    desc = (f" {oo_move}({oo_len})"
                            + f" > {nx_move}({nx_len})")
                SlTrace.lg(f"out of order - {desc}")
                for move_tuple in sorted_move_tuples:
                    SlTrace.lg("    {} len:{:d}".format(loc2desc(move_tuple[1]), move_tuple[0]))
                SlTrace.lg("-"*50)
            return False
        
        return True
    
    
    
    def order_warn_refine(self, board,  move_tuples, max_look_ahead=None):
        """ Refine move_tuples list by successively applying warnsdoff conjecture
        on subgroups with ties in score (number of follow ons).  No checks for
        collisions with already played levels
        :board: current board
        :move_tuples: list of (len, move, followon_list)
        :max_look_ahead: number of levels of look ahead default: 5
        :returns: list of further ordered tuples
        """
        if max_look_ahead is None:
            max_look_ahead = self.max_look_ahead
        for _ in range(max_look_ahead):
            sorted_lists = self.split_by_first(move_tuples)
            if len(sorted_lists) == len(move_tuples):
                return move_tuples          # No ties - list is good

            sorted_tuples = []
            for sub_list in sorted_lists:
                if len(sub_list) == 1:
                    sole_tuple = sub_list[0]
                    if len(sorted_tuples) > 0:
                        offset = sorted_tuples[-1][0] + 1    # make one greater than highest len code
                    else:
                        offset = 1 
                    next_entry = (offset, sole_tuple[1], sole_tuple[2])
                    sorted_tuples.append(next_entry)    # No need for further ordering
                    continue
                
                sorted_tuples1 = self.order_moves_by_warnsdorff_tuples(board, sub_list)
                for mtuple in sorted_tuples1:
                    if len(sorted_tuples) > 0:
                        offset = sorted_tuples[-1][0] + mtuple[0]    # start at highest previous code
                    else:
                        offset = mtuple[0]+1 
                    next_entry = (offset, mtuple[1], mtuple[2])
                    sorted_tuples.append(next_entry)    # No need for further ordering
        return sorted_tuples                # Return best so far
    
    
    def order_warn_refine_1(self, board,  move_tuples):
        """ Refine move_tuples list one level
        No checks for
        collisions with already played levels
        :board: current board
        :move_tuples: list of (len, move, followon_list)
        :returns: list of further ordered tuples
        """
        sorted_lists = self.split_by_first(move_tuples)
        if len(sorted_lists) == len(move_tuples):
            return move_tuples          # No ties - list is good
        
        sorted_tuples = []
        for sub_list in sorted_lists:
            if len(sub_list) == 1:
                sorted_tuples.append(sub_list[0])    # No need for further ordering
                continue
            
            sorted_tuples1 = self.order_moves_by_warnsdorff_tuples(board, sub_list)
            sorted_tuples.extend(sorted_tuples1)     # Add sorted list
        return sorted_tuples


    def moves_from_sorted(self, sorted_move_tuples):
        """ Retrieve moves from list of move tuples
        :returns: list of moves
        """
        mvs = []
        for smv in sorted_move_tuples:
            mvs.append(smv[1])
        return mvs
    

    def order_moves_by_warnsdorff_1(self, board, moves):
        """ Order moves by Warnsdorff algorithm (minimum neighbors) one level
        :board: current board
        :moves: Candidate list of moves
        :returns: list with moves of decreasing number of follow-on moves
                    of 3-tuples (number-of follow-on moves,
                                 move,
                                 list of this move's follow-on
                                 )
        """
        if len(moves) == 0:
            return []
        
        ###if len(moves) == 1:
        ###    return [(0, moves[0], [])]
        
        mv_by_nms = []
        for move in moves:
            if not board.is_empty(move):
                continue                    # Don't consider non-empty squares
            
            nms = board.get_knight_moves(move)
            ncs = []
            for mv in nms:
                if board.is_empty(mv):
                    ncs.append(mv)
            mv_by_nms.append((len(ncs), move, ncs))
        
        smv_by_nms_sorted = sorted(mv_by_nms, key=by_first)
        return smv_by_nms_sorted
    

    def order_moves_by_warnsdorff_tuples(self, board, move_tuples):
        """ Order moves by Warnsdorff algorithm (minimum neighbors) one level
        :board: current board
        :move_tuples: sorted list of 3-tuples
                        (number-of follow-on moves,
                        move,
                        list of this move's follow-on
                        )
        :returns: list with moves of decreasing number of follow-on's folow-on moves
                    of 3-tuples (number-of follow-on folow-on's moves,
                                 move,
                                 list of this move's follow-on's follow-ons
                                 )
        """
        ffon_tuples = []    # list of (follow-on's follow-on cnt, move, ffon_list)
        for move_tuple in move_tuples:
            follow_ons = move_tuple[2]
            follow_board = ChessBoard(board)
            follow_board.set_piece('N', move_tuple[1])
            follow_on_tuples = self.order_moves_by_warnsdorff_1(follow_board, follow_ons)
            ffon_moves = []
            for follow_on_tuple in follow_on_tuples:
                ffon_moves.extend(follow_on_tuple[2])
            ffon_tuples.append((len(ffon_moves), move_tuple[1], ffon_moves))    
        
        ffon_tuples_sorted = sorted(ffon_tuples, key=by_first)
        return ffon_tuples_sorted


    def split_by_first(self, sorted_list):
        """ Split sorted list into lists, of identical first element
        :sorted_list: list of tuples sorted by first element
        :returns: list of list of tuples grouped by identical first element
        """
        list_lists = [] # list of lists
        first_val = None    # track first value
        for entry in sorted_list:
            if first_val is None or entry[0] != first_val:
                first_val = entry[0]
                group = []     # Start new group
                list_lists.append(group)
            group.append(entry)
        return list_lists        




    def track_path(self, desc, square, path, trace_flag=None):
        """ Track path"
        :desc: description
        :square: starting square
        :path: current path
        :trace_flag: trace level flag default: no trace
        """
        if trace_flag is None:
            return
        
        if not SlTrace.trace(trace_flag):
            return
        
        if ChessBoard.track_all_path or len(path) > len(self.tracking_path):
            SlTrace.lg("{} at {} ({:d}) {}"
                       .format(desc, loc2desc(square), len(path), self.path_desc(path)), dp=3)
            ChessBoard.tracking_path = path
            if self.display_path_board:
                self.mw.update_idletasks()
                self.mw.update()
                if len(path) >= self.len_ckt-4:
                    ChessBoardDisplay.display_path(desc, path, ncol=self.ncol, nrow=self.nrow)


    def get_knight_moves(self, loc=None, board=None, only_empty=False):
        """ Get legal moves for given piece, from loc
        :loc: location str or tuple
        :board: playing board, default: current board
        :only_empty: only consider empty squares default: consider all squares
        :returns: list of tuples for legal moves
        """
        if board is None:
            board = self.board
        return board.get_knight_moves(loc=loc, only_empty=only_empty)

    def backup_move(self, keep_move=False):
        """ Backup to previous move
        :keep_move: keep current move for make_move
                default: False == discard move
        """
        if SlTrace.trace("backup_move"):
            if len(self.path_stack) > 0:
                st = self.path_stack[-1]
                SlTrace.lg(f"backup_move {len(self.path_stack)} {loc2desc(st.loc)} ")
        if len(self.path_stack) > 1:        # Don't allow backingup before first move
            if self.is_display_move:
                self.undisplay_move()       # Update display before move removal
            ste = self.path_stack[-1]
            board = ste.board
            loc = ste.loc
            board.clear_loc(loc)
            if keep_move:
                if len(self.path_stack) > 1:
                    self.path_stack[-2].best_moves.insert(0, loc)
                else:
                    self.nbackup += 1
            del self.path_stack[-1]
        if self.is_display_move and keep_move:
            SlTrace.lg("after backup_move")

    def widen_search(self):
        """ Do a little "breath-first" by looking at a new choice at top
        of stack
        """
        if self.nbackup < self.backup_limit:
            self.backup_move()
            return
        
        SlTrace.lg("widen search")
        while len(self.path_stack) > self.widen_level:
            self.backup_move()
        self.nbackup = 0
        self.widen_level += 1
        SlTrace.lg(f"widen_level:{self.widen_level}")
        
    def update_display(self):
        self.display_board.update_display()
