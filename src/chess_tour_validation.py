# chess_tour_validation.py    27Nov2019  crs Create
"""
Move path validation support
An attempt to validate paths as valid move tours e.g. closed knight's tour
We try to make the calculations different than the path generation tools to avoid 
"error" blindness in which the same flaw appears in the testing as in the production
code.
Although no initial support is given, an attempt is to facilitate extension to tours
of pieces other than knights.
"""
from select_error import SelectError
from select_trace import SlTrace
from chess_board import ChessBoard
from displayed_path import DisplayedPath

class ChessTourValidation:
    def __init__(self, locs=None, ncol=None, nrow=None, piece=None, closed_tours=True):
        """ Set up validation constraints on which validation is made
        :locs: squares for which possible tour default ncolxnrow
        :ncol: number of columns default: nrow if nrow is not None else 8
        :nrow: number of rows default: ncol if ncol is not None else 8
        :piece: Chess piece letter e.g. 'K' for black king default: 'N' - black knight
        :closed_tours: Check for closed tour (ending square is one piece move from start)
                        default: True
        """
        if ncol is None:
            ncol = 8 if nrow is None else nrow
        self.ncol = ncol
        if nrow is None:
            nrow = 8 if ncol is None else ncol
        self.nrow = nrow
        if locs is None:
            locs = []
            for ic in range(ncol):
                for ir in range(nrow):
                    locs.append((ic,ir))
        self.locs = locs
        if piece is None:
            piece = 'N'
        self.piece = piece
        self.closed_tours = closed_tours
        self.cb = ChessBoard(ncol=self.ncol, nrow=self.nrow)    # For acces to basic fns


    def find_path_duplicates(self, dpaths=None):
        """ Find any duplicate paths
        :path_list: list of displayed paths
        :returns: list of lists of matching dpaths
        """
        if dpaths is None:
            raise SelectError("Missing REQUIRED dpaths")
        matches = []
        dpaths_to_check = dpaths[:]     # Copy so pop won't modify dpaths
        while len(dpaths_to_check) > 1:
            dpgrp = []           # latest group of matches
            dp1 = dpaths_to_check.pop(0)
            p1 = dp1.path
            dptc_next = []       # Next remaining group
            for dp2 in dpaths_to_check:
                p2 = dp2.path
                if self.match_path(p1, p2, bidirectional=True):
                    if len(dpgrp) ==  0:
                        dpgrp.append(dp1)     # Add first
                    dpgrp.append(dp2)         # Add in match
                else:
                    dptc_next.append(dp2)     # Add to remaining list
            if len(dpgrp) > 1:
                matches.append(dpgrp)        # Add to group of matches
            dpaths_to_check = dptc_next       # Set remaining list
        return matches

    def match_path(self, p1, p2, bidirectional=True):
        """ Match two paths each containing a list of unique locs
        :p1: path 1 list of locs
        :p2: path 2 list of locs
        :bidirectional: check for reversed default: True
        :returns: return True if exact match
        """
        if len(p1) != len(p2):
            return False            # Unequal lengths
        
        if len(p1) == 0:
            return True             # Both empty
        
        loc1 = p1[0]
        if loc1 not in p2:
            return False            # loc in p1 not in p2
        
        iloc2 = p2.index(loc1)
        p2 = p2[iloc2:] + p2[:iloc2]    # Wrap p2 matching first loc of p1,p2
        
        if p1 == p2:
            return True

        if bidirectional:
            p2 = p2[::-1] 
        if p1 == p2:
            return True

    def is_valid_moves(self, dpath, closed_tours=None, quiet=False, prefix=None):
        """ Check if locs path consists of a list of valid piece moves
        
        :dpath: display path (square denotations) tuple or algebraic notation
        :closed_tours: check for closed tour default:self.closed_tour else True
        :quiet: suppress diagnostic output default: False
        :prefix: optional prefix to diagnostic messages
        :returns: True if legitimate moves within validation squares
        
        """
        cb = self.cb
        path = dpath.path
        if prefix is None:
            prefix = ""
        if closed_tours is None:
            closed_tours = True if self.closed_tours is None else self.closed_tours
        prev_loc = None
        for loc in path:
            loc = cb.loc2tuple(loc)
            if loc not in self.locs:
                if not quiet:
                    SlTrace.lg(f"{prefix} move {cb.loc2desc(loc)} is not in squares:{cb.path_desc(self.locs)}")
                return False
            
            if prev_loc is not None:
                if not self.cb.is_neighbor(prev_loc, loc):
                    if not quiet:
                        SlTrace.lg(f"move {loc2desc(prev_loc)} to {loc2desc(loc)} is not legal")
                    return False
            prev_loc = loc
        if closed_tours:
            prev_loc = path[-1]
            loc = path[0]
            if not self.cb.is_neighbor(prev_loc, loc):
                if not quiet:
                    SlTrace.lg(f"path closing move {loc2desc(prev_loc)} to {loc2desc(loc)} is not legal")
                return False
            
        return True    

    def is_covering_but_once(self, dpath, quiet=False, prefix=None):
        """ Check if path covers the board(self.locs) touching each square
        but once
        :dpath: display path of squares traversed
        :quiet: suppress diagnostics default: False
        """
        cb = self.cb
        path = dpath.path
        if prefix is None:
            prefix = ""
        touches = {}
        for loc in path:
            loc = cb.loc2tuple(loc)
            if loc not in touches:
                touches[loc] = 1
            else:
                if not quiet:
                    SlTrace.lg(f"\n    {prefix} Repeating square {cb.loc2desc(loc)}")
                return False
        
        for loc in self.locs:
            loc = cb.loc2tuple(loc)
            if loc not in touches:
                if not quiet:
                    SlTrace.lg(f"\n    {prefix} {cb.loc2desc(loc)} not in {cb.squares_list(path)}")
                return False
            
        return True

    def is_valid_tour(self, dpath, closed_tours=True, quiet=False, prefix=None):
        """ Test if valid tour
        :dpath: DisplayPath of tour
        :closed_tours: accept only closed tours default: True
        :quiet: suppress diagnostics default: False
        :prefix: optional prefix to fail diagnostic messages
        :returns: True iff path is a valid tour
        """
        if prefix is None:
            prefix = ""
        if not self.is_covering_but_once(dpath, quiet=quiet, prefix=prefix):
            return False
        
        if not self.is_valid_moves(dpath, closed_tours=closed_tours, quiet=quiet, prefix=prefix):
            return False
        
        return True
    
    def is_valid_tours(self, dpaths, closed_tours=True, quiet=False, all_fails=True):
        """ Test if valid tour
        :dpaths: list of display paths(DisplayedPath) (each a sequence of locs)
        :closed_tours: accept only closed tours default: True
        :quiet: suppress diagnostics default: False
        :all_fails: test and report on all False=> report first fail and stop default:all
        :returns: True iff all paths are valid tours
        """
        cb = self.cb
        res = True
        for dpath in dpaths:
            path = dpath.path
            prefix = f"{dpath.org_no}: {cb.loc2desc(path[0])}: {dpath.desc}\n        "
            if not self.is_valid_tour(dpath, closed_tours=closed_tours, quiet=quiet, prefix=prefix):
                res = False
                if not all_fails:
                    break
        return res

    def report_duplicate_paths(self, dpaths):
        cb = self.cb
        dup_paths = self.find_path_duplicates(dpaths)
        if len(dup_paths) > 0:
            SlTrace.lg(f"{len(dup_paths)} duplicate path groups")
            for igrp, dup_grp in enumerate(dup_paths):
                SlTrace.lg(f"{igrp+1}: {cb.loc2desc(dup_grp[0].path[0])}")
                for grp in dup_grp:
                    SlTrace.lg(f"{cb.loc2desc(grp.path[0])}-{cb.loc2desc(grp.path[-1])}: {cb.path_desc(grp.path)}")
        
if __name__ == "__main__":
    from chess_board_display import ChessBoardDisplay
    
    dboard = ChessBoardDisplay()
    cb = ChessBoard()
    def test_find_path_duplicates():
        SlTrace.lg("\ntest_find_path_duplicates")
        test_paths = [
            ['a1', 'a2', 'a3'],
            ['a2', 'a3', 'a1'],
            ['a3', 'a1', 'a2'],
            ['b1', 'b2', 'b3'],             # Alone
            ['b1', 'b2', 'b3', 'b4'],
            ['b2', 'b3', 'b1', 'b4'],     # Not a match
            ['b4', 'b3', 'b2', 'b1'],     # reverse match
            ['b2', 'b3', 'b4', 'b1'],
            ]
        test_dpaths = []
        for test_path in test_paths:
            test_dpaths.append(DisplayedPath(path=test_path, disp_board=dboard))
        ctv = ChessTourValidation()
        SlTrace.lg("Checking for duplicate paths")
        dup_dpaths = ctv.find_path_duplicates(test_dpaths)
        if len(dup_dpaths) > 0:
            SlTrace.lg(f"{len(dup_dpaths)} duplicate path groups")
            for igrp, dup_dgrp in enumerate(dup_dpaths):
                SlTrace.lg(f"{igrp+1}: {cb.loc2desc(dup_dgrp[0].path[0])}")
                for dpath in dup_dgrp:
                    path = dpath.path
                    SlTrace.lg(f"{cb.loc2desc(path[0])}-{cb.loc2desc(path[-1])}: {cb.path_desc(path)}")
 
    def test_is_valid_moves():
        SlTrace.lg("\ntest_is_valid_moves")
        good1 = ['b1', 'a3', 'c4', 'd2']
        dgood1 = DisplayedPath(path=good1, disp_board=dboard)
        ctv = ChessTourValidation(ncol=3, nrow=3)
        if not ctv.is_valid_moves(dgood1):
            SlTrace.lg(f"expected failing for {good1} in (3x3)")
        else:
            SlTrace.lg(f"UNEXPECTED failing for {good1} in (3x3)")
            
        ctv = ChessTourValidation(ncol=4, nrow=4)
        if not ctv.is_valid_moves(dgood1):
            SlTrace.lg(f"UNEXPECTED failing for {good1} in (4x4)")
        else:
            SlTrace.lg(f"expected passing for {good1} in (4x4)")

        bad2 = ['b1', 'a3', 'c5', 'd2']
        dbad2 = DisplayedPath(path=bad2, disp_board=dboard)
        ctv = ChessTourValidation()
        if not ctv.is_valid_moves(dbad2):
            SlTrace.lg(f"expected failing for {bad2}")
        else:
            SlTrace.lg(f"UNEXPECTED passing for {bad2}")


    def test_is_covering_but_once(): 
        SlTrace.lg("\ntest_covering_but_once")
        good1 = ['g7', 'g8', 'h8', 'h7']
        dgood1 = DisplayedPath(path=good1, disp_board=dboard)
        ctv = ChessTourValidation(locs=good1)
        if ctv.is_covering_but_once(dgood1):
            SlTrace.lg(f"expected: pass of {good1}")
        else:
            SlTrace.lg(f"UNEXPECTED FAIL of {good1}")

    def test_is_valid_tours(force_fail=False):
        SlTrace.lg("\ntest_is_valid_tours")
        paths =  [
        [ "a1", "b3", "c1", "a2", "b4", "a6", "b8", "d7", "f8", "h7", "g5", "h3", "g1", "e2", "g3", "h1", "f2", "d1", "b2", "a4", "c5", "b7", "a5", "c6", "a7", "c8", "b6", "a8", "c7", "e8", "g7", "h5", "f6", "g8", "h6", "g4", "h2", "f1", "d2", "b1", "c3", "e4", "d6", "b5", "a3", "c4", "e3", "d5", "e7", "f5", "d4", "e6", "d8", "f7", "h8", "g6", "h4", "g2", "f4", "d3", "e5", "f3", "e1", "c2",
],
        [ "b1", "a3", "c2", "a1", "b3", "c1", "a2", "b4", "a6", "b8", "d7", "f8", "h7", "g5", "h3", "g1", "e2", "g3", "h1", "f2", "d1", "b2", "a4", "c3", "b5", "a7", "c8", "b6", "a8", "c7", "e8", "g7", "h5", "f6", "g8", "h6", "g4", "h2", "f1", "e3", "d5", "e7", "f5", "h4", "g2", "e1", "f3", "d4", "e6", "f4", "g6", "h8", "f7", "d8", "c6", "e5", "d3", "c5", "b7", "a5", "c4", "d6", "e4", "d2",
],
        [ "c1", "a2", "b4", "a6", "b8", "d7", "f8", "h7", "g5", "h3", "g1", "e2", "g3", "h1", "f2", "d1", "b2", "a4", "b6", "a8", "c7", "e8", "g7", "h5", "f6", "g8", "h6", "g4", "h2", "f1", "d2", "b1", "c3", "e4", "c5", "b3", "a1", "c2", "a3", "b5", "a7", "c8", "d6", "b7", "a5", "c4", "e3", "d5", "e7", "f5", "d4", "e6", "d8", "c6", "e5", "f7", "h8", "g6", "h4", "f3", "e1", "g2", "f4", "d3",
],
        [ "d1", "b2", "a4", "b6", "a8", "c7", "a6", "b8", "d7", "f8", "h7", "g5", "h3", "g1", "e2", "c1", "a2", "c3", "b1", "a3", "b5", "a7", "c8", "e7", "g8", "h6", "f7", "h8", "g6", "h4", "g2", "e1", "c2", "a1", "b3", "a5", "b7", "d8", "c6", "b4", "d5", "f4", "e6", "d4", "f3", "h2", "f1", "d2", "c4", "e5", "d3", "c5", "e4", "f2", "h1", "g3", "h5", "g7", "f5", "d6", "e8", "f6", "g4", "e3",
],
        [ "e1", "g2", "h4", "g6", "h8", "f7", "h6", "g8", "e7", "c8", "a7", "b5", "a3", "b1", "d2", "f1", "h2", "f3", "g1", "h3", "g5", "h7", "f8", "d7", "b8", "a6", "c7", "a8", "b6", "a4", "b2", "d1", "f2", "h1", "g3", "h5", "g7", "e8", "f6", "g4", "e5", "c4", "d6", "f5", "e3", "c2", "a1", "b3", "a5", "b7", "d8", "c6", "d4", "e6", "c5", "e4", "c3", "d5", "f4", "e2", "c1", "a2", "b4", "d3",
],
        [ "f1", "h2", "g4", "h6", "g8", "e7", "c8", "a7", "b5", "a3", "b1", "d2", "b3", "a1", "c2", "e1", "g2", "h4", "g6", "h8", "f7", "d8", "b7", "a5", "c6", "b8", "a6", "b4", "a2", "c1", "e2", "g1", "f3", "d4", "f5", "g3", "h1", "f2", "h3", "g5", "h7", "f8", "e6", "g7", "h5", "f4", "d3", "e5", "d7", "c5", "e4", "d6", "e8", "f6", "d5", "c7", "a8", "b6", "c4", "b2", "a4", "c3", "d1", "e3",
],
        [ "g1", "h3", "f2", "h1", "g3", "f1", "h2", "g4", "h6", "g8", "e7", "c8", "a7", "b5", "a3", "b1", "d2", "b3", "a1", "c2", "e1", "g2", "h4", "f3", "g5", "h7", "f8", "g6", "h8", "f7", "d8", "b7", "a5", "c6", "b8", "a6", "b4", "a2", "c1", "d3", "e5", "d7", "c5", "a4", "b2", "d1", "c3", "e4", "d6", "c4", "b6", "a8", "c7", "e8", "f6", "d5", "e3", "f5", "g7", "h5", "f4", "e6", "d4", "e2",
],
        [ 
          "h1", "f2", "h3", "g1", "e2", "c1", "a2", "b4", "a6", "b8", "d7", "f8", "h7", "g5", "f7", "h8", "g6", "h4", "g2", "e1", "d3", "b2", "d1", "c3", "a4", "b6", "a8", "c7", "e8", "g7", "h5", "f4", "e6", "d8", "b7", "c5", "b3", "a1", "c2", "a3", "b1", "d2", "f3", "h2", "f1", "e3", "d5", "f6", "g4", "e5", "c4", "a5", "c6", "a7", "b5", "d4", "f5", "h6", "g8", "e7", "c8", "d6", "e4", "g3",
],
]
        if force_fail:
            SlTrace.lg(f"forcing failure by poping off first move({loc2desc(paths[-1][0])}) of last path")
            paths[-1].pop(0)
        dpaths = []
        for path in paths:
            dpath = DisplayedPath(path, disp_board=dboard)
            dpaths.append(dpath)
        ctv = ChessTourValidation()
        if ctv.is_valid_tours(dpaths):
            SlTrace.lg("Passed")
        else:
            SlTrace.lg("Failed")

                   
    do_duplicates = True
    ###do_duplicates = False
    do_valid_moves = True
    do_covering = True
    do_valid_tours = True
                       
    if do_duplicates:
        test_find_path_duplicates()
    if do_valid_moves:
        test_is_valid_moves()               
    if do_covering:
        test_is_covering_but_once()
    if do_valid_tours:
        test_is_valid_tours(force_fail=True)
        test_is_valid_tours()