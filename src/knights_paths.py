#knights_paths.py
"""
Support searching for knights paths on a chess board calculation
"""
import datetime
import traceback
from select_trace import SlTrace
from select_timeout import SelectTimeout

from chess_board import ChessBoard
from chess_board_display import ChessBoardDisplay
from pydoc import describe

loc2desc = ChessBoard.loc2desc 
loc2tuple = ChessBoard.loc2tuple 
path_desc = ChessBoard.path_desc
display_path = ChessBoardDisplay.display_path


""" 
From Stackoverflow.com
"""
import time
import concurrent.futures as futures


def timeout(timelimit):
    def decorator(func):
        def decorated(*args, **kwargs):
            with futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    result = future.result(timelimit)
                except futures.TimeoutError:
                    print('Timedout!')
                    raise TimeoutError from None
                else:
                    print(result)
                executor._threads.clear()
                futures.thread._threads_queues.clear()
                return result
        return decorated
    return decorator

 
def by_first(tp):
    """ Sort helper to pick first tuple element
    """
    return tp[0]


class KnightsPaths:
    """ Generates knight paths, given starting position
    """
    time_limit = 60
    
    def __init__(self, board=None, loc=None, closed_tours=False, max_try=None, time_limit=None,
                 max_look_ahead=5):
        """ Setup for kight path generation
        Via depth-first search of night moves which traverse board without revisiting any square.
        
        :board: Current chess board, default: generate empty board
        :loc: starting knight position                
        :closed_tours: return only closed tours
        :max_look_ahead: maximum number of moves to look ahead in best move determination
        :max_tries: Number of tries (no more moves) for path default: no max
        :time_Limit: time limit, in seconds to produce a result (return path)
                    default: 60 seconds
        """
        self.ntry = 0                            # number of tries so far
        self.max_look_ahead = max_look_ahead
        self.max_try = max_try
        if time_limit is None:
            time_limit = 60
        KnightsPaths.time_limit = time_limit    # Make class variable to support wrapper
        self.time_begin = datetime.datetime.now()
        self.time_end = self.time_begin + datetime.timedelta(seconds=time_limit)
        if board is None:
            board = ChessBoard(ncols=8, nrows=8)
        self.board = board
        self.ncols = board.ncols
        self.nrows = board.nrows
        self.loc_start = loc
        self.closed_tours = closed_tours
        self.board.set_piece('N', self.loc_start)
        self.path_stack = [(self.loc_start, self.board, None)]
                                    # (move, board, next_move list)
                                    # board: playing board with move in place
                                    # next_move_list element: (score, move) where lower is better
        self.track_level = self.ncols*self.nrows
        self.ncomplete_path = 0     # Number of paths found
        self.nbackup = 0           # Number of backups, not including non-tour paths
        self.ntrack_ntie = 0
        self.ntie = 0
 
    ###@timeout(time_limit)
    def build_path_stack(self):
        """ Agument path_stack with a next move
        :returns: True if successful, False if no such path found
        """
        
        board = self.board
        len_ckt = self.ncols*self.nrows
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
                if self.closed_tours:
                    start_loc = self.path_stack[0][0]
                    end_loc = self.path_stack[-1][0]
                    if board.is_neighbor(start_loc, end_loc):
                        return True
                    
                    if SlTrace.trace("non-closed"):
                        self.display_stack_path("ignoring non-closed tour {} to {}"
                                                .format(loc2desc(self.path_stack[0][0]),
                                                        loc2desc(self.path_stack[-1][0])))
                        self.display_stack("non-closed")
                    if self.max_try is not None and self.ntry >= self.max_try:
                        SlTrace.lg("Giving up looking for closed tour after {:d} tries". format(self.ntry))
                        return True
                    
                    
                    del self.path_stack[-1]         # Not a closed tour
                    continue                        # look again
                else:
                    return True
        
            next_move, board, best_moves = self.path_stack[-1]
            if best_moves is None:
                best_moves = self.get_best_moves(board, next_move)
            if len(best_moves) == 0:
                self.ntry += 1
                if SlTrace.trace("no_more_moves"):
                    SlTrace.lg("{:d}: No more moves at {} len_stk={:d}"
                               .format(self.ntry, loc2desc(next_move), len_stk))
                if self.max_try is not None and self.ntry > self.max_try:
                    SlTrace.lg("Giving up this search")
                    return True
                
                if SlTrace.trace("no_more_moves"):
                    self.display_stack_path("no_more_moves")
                self.nbackup += 1
                del self.path_stack[-1]
                if len(self.path_stack) <= self.track_level:
                    self.track_level = len(self.path_stack)
                    if SlTrace.trace("back_off_trace"):
                        if self.track_level > 0:
                            nxt_move, board, bst_moves = self.path_stack[-1]
                            self.board = board
                            SlTrace.lg("back_off_trace stk_len={:d} start={} at {} best_moves={}"
                                   .format(self.track_level, loc2desc(self.loc_start),
                                           loc2desc(nxt_move), path_desc(bst_moves)))
                            self.display_stack_path("back_off_trace")
                continue                            # Backup one
            
            follow_move = best_moves.pop(0)
            self.path_stack[-1] = (next_move, board, best_moves)
            new_board = ChessBoard(base_board=board)
            new_board.set_piece('N', follow_move)
            self.path_stack.append((follow_move, new_board, None))
            if SlTrace.trace("stack_grow"):
                SlTrace.lg("stk_len:{:d} at {}"
                        .format(len(self.path_stack), loc2desc(follow_move)))
            continue

    def time_check(self):
        """ Check for timeout
        """
        now = datetime.datetime.now()
        if now > self.time_end:
            raise SelectTimeout



    def display_stack_path(self, desc=None):
        """ Display current path on stack
        :desc: optional description
        """
        if desc is None:
            desc = ""
        path = self.path_stack_path()
        ChessBoardDisplay.display_path(desc, path) 


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
        :board: chess board
        :loc: piece location
        """
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
        del self.path_stack[-1]
        return path

    def path_stack_path(self):
        """ Returns path on stack
        """
        path = []
        for se in self.path_stack:
            path.append(se[0])
        return path
    
                   
    def next_path(self):
        """ Get next path
        1. if necessary, build path to nrows*ncols depth
        2. get list of moves from stack
        
        :returns: next path, None if none
        """
        try:
            if not self.build_path_stack():
                return None
            
            path = self.pop_path_stack()
            return path
                
        except SelectTimeout:
            SlTrace.lg(f"path find timeout({self.time_limit:.3f} sec)")
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
                if len(path) >= self.ncols*self.nrows-4:
                    ChessBoard.display_path(desc, path, ncols=self.ncols, nrows=self.nrows)


    def get_knight_moves(self, loc=None, board=None):
        """ Get legal moves for given piece, from loc
        :loc: location str or tuple
        :board: playing board, default: current board
        :returns: list of tuples for legal moves
        """
        if board is None:
            board = self.board
        return board.get_knight_moves(loc=loc)

