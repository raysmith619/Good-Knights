# paths_gen.py
"""
Generate a list of paths
"""

from datetime import datetime


from select_trace import SlTrace
from select_error import SelectError
from comp_stats import ResultCompStats
from chess_board import ChessBoard
from chess_board_display import ChessBoardDisplay
from knights_paths import KnightsPaths
from displayed_path import DisplayedPath
from chess_tour_validation import ChessTourValidation

class PathsGen:
    """ Generate and manipulate a list of paths
    """
    def __init__(self, path_starts=None, arrange=None,
                 time_out=None,
                 closed_tours=None,
                 display_move=False,
                 pW=None,
                 move_time=.5,
                 width=400,
                 height=400,
                 nrow = 8,
                 ncol = 8,
                 max_look_ahead=5):
        self.display_move = display_move
        self.pW = pW
        self.move_time = move_time
        self.width = width
        self.height = height
        self.nrow = nrow
        self.ncol = ncol
        self.board = ChessBoard(ncol=ncol, nrow=nrow)
        self.len_ckt = nrow*ncol
        if display_move:
            time_out = None             # Disable time_out if displaying moves
        self.time_out = time_out
        self.path_starts = path_starts
        self.closed_tours = closed_tours
        self.max_look_ahead = max_look_ahead
        self.arrange = arrange
        self.sqno = 0        # number within list
        self.displayed_paths = []   # Repository of displayed paths
        self.kpths = None           # Current path, if any
        self.ipstart = 0            # current start loc index

    def backup_move(self, keep_move):
        """ Backup current move, if one
        """
        if self.kpths is not None:
            self.kpths.backup_move(keep_move=keep_move)


    def next_move(self):
        """ Do next move
        """
        if self.kpths is not None:
            self.kpths.next_move()
            
    def destroy(self):
        for path in self.displayed_paths:
            path.destroy()
            
    def go(self, in_step=False):
        """ Start path search
        :in_step: True - start running with step set
        """
        cb = self.board
        if in_step:
            self.pW.set_in_step()
            
        n_complete_paths = 0
        n_having_complete_path = 0
        n_with_no_complete_path = 0
        n_with_multiple_complete_paths = 0
        longest_path = []
        longest_path_start = None
        n_closed_tour = 0
        max_success_time = None     # Maximum successful duration
        total_success_time = 0      # Total successful times        
        self.is_stop_gen = False       # Set to stop generation
        success_comp_stats = ResultCompStats()
        fail_comp_stats = ResultCompStats()    
        while True:
            if self.ipstart >= len(self.path_starts):
                break
            self.is_change_tour = False    # Set for change tour cmd
            
            self.sqno = self.ipstart + 1
            loc = self.path_starts[self.ipstart]
            SlTrace.lg(f"{self.sqno:2d}: {cb.loc2desc(loc)}", dp=3)
            if self.kpths is not None:
                self.kpths.destroy()
            self.kpths = kpths = KnightsPaths(loc=loc, closed_tours=self.closed_tours,
                                 display_move=self.display_move,
                                 pW=self.pW,
                                 move_time = self.move_time,
                                 time_limit=self.time_out,
                                 nrow=self.nrow, ncol=self.ncol,
                                 max_look_ahead=self.max_look_ahead)
            self.ipstart += 1   # Bump for next iteration
            time_beg = datetime.now()
            path = kpths.next_path()
            if self.is_change_tour:
                continue            # Change tour cmd
            if self.is_stop_gen:
                SlTrace.lg("Stop generation")
                return
                
            nmove = kpths.get_nmove()
            track_level = kpths.get_track_level()
            time_end = datetime.now()
            time_dur = (time_end-time_beg).total_seconds()
            npath = kpths.get_ncomplete_path()
            ntrack_ntie = kpths.ntrack_ntie
            ntie = kpths.ntie
            comp_stats = (f"Comp Stats: time={time_dur:.3f} paths={npath}"
                        f" move={nmove} track_level={track_level} tie_track={ntrack_ntie} ntie={ntie}")
            if path is None:
                what = "tours" if self.closed_tours else "paths"
                SlTrace.lg(f"No {what} found - {npath} complete paths found")
                SlTrace.lg(f"    {comp_stats}")
                fail_comp_stats.add(time_dur=time_dur, npath=npath, nmove=nmove,
                                track_level=track_level, ntrack_ntie=ntrack_ntie,
                                ntie=ntie)
                pth = kpths.last_complete_path
                if pth is None:
                    pth_desc = "NO PATH"
                elif len(pth) < self.nrow*self.ncol:
                    pth_desc = "INCOMPLETE"
                else:
                    pth_desc = "NOT CLOSED"
                    kpths.is_complete_tour = True
                path_description = f" {self.sqno}: {cb.loc2desc(loc)} {pth_desc} {time_dur:.3f} sec: "
                SlTrace.lg(path_description)
                dp = ChessBoardDisplay.display_path(pth, desc=path_description,
                                  nrow=self.nrow, ncol=self.ncol, 
                                   width=self.width, height=self.height)
                if dp is None:
                    dp = ChessBoardDisplay(nrow=self.nrow, ncol=self.ncol, 
                                   width=self.width, height=self.height)    # place holder
                self.displayed_paths.append(DisplayedPath(disp_board=dp, org_no=self.sqno,
                                                    desc=path_description,
                                                    is_closed_tour=kpths.is_closed_tour,
                                                    is_complete_tour=kpths.is_complete_tour))
                continue
            
            if len(path) == self.len_ckt:
                kpths.is_complete_tour = True
                success_comp_stats.add(time_dur=time_dur, npath=npath, nmove=nmove,
                                track_level=track_level, ntrack_ntie=ntrack_ntie,
                                ntie=ntie)
                ct_desc = ""        # Closed tour description, if one
                if kpths.is_neighbor(path[0], path[-1]):
                    kpths.is_closed_tour = True
                    n_closed_tour += 1
                    ndesc = "th"
                    if n_closed_tour%10 == 1:
                        ndesc = "st"
                    elif n_closed_tour%10 == 2:
                        ndesc = "nd"
                    elif n_closed_tour%10 == 3 and n_closed_tour != 13:
                        ndesc = "d"
                    ct_desc = (f" {n_closed_tour:d}{ndesc} closed tour"
                            + f" paths={npath}")
                SlTrace.lg(f"{ct_desc} (in {time_dur:.3f} sec)"
                           + f" from {cb.loc2desc(path[0])}"
                           + f" to {cb.loc2desc(path[-1])}"
                           + f" path: {cb.path_desc(path)}")
                n_complete_paths += 1
                n_having_complete_path += 1
                total_success_time += time_dur
                if max_success_time is None or time_dur > max_success_time:
                    max_success_time = time_dur
                path_description = f" {self.sqno}: {cb.loc2desc(loc)} {ct_desc} {time_dur:.3f} sec: "
                SlTrace.lg(path_description)
                dp = ChessBoardDisplay.display_path(path, desc=path_description, nrow=self.nrow, ncol=self.ncol, 
                                   width=self.width, height=self.height)
                self.displayed_paths.append(DisplayedPath(disp_board=dp, org_no=self.sqno,
                                                        desc=path_description,
                                                        is_closed_tour=kpths.is_closed_tour,
                                                        is_complete_tour=kpths.is_complete_tour))
            else:
                dp = cbdisplay_path(path, desc=f"Short Path: len={len(path)}", nrow=self.nrow, ncol=self.ncol)
                self.displayed_paths.append(DisplayedPath(disp_board=dp, org_no=self.sqno,
                                                          desc="Short Path"))
            SlTrace.lg(f"    {comp_stats}")
            SlTrace.lg(f"prunes non-closed-tour: {kpths.nprune_closed}")            
        SlTrace.lg(f"{n_complete_paths:4d} complete paths")
        SlTrace.lg(f"{n_closed_tour:4d} closed tours")
        
        SlTrace.lg(f"{n_having_complete_path:4d} starting squares having complete path")
        SlTrace.lg(f"{n_with_no_complete_path:4d} starting squares with no complete path")
        SlTrace.lg(f"{n_with_multiple_complete_paths:4d} starting squares with multiple complete paths")
        if n_complete_paths > 0:
            SlTrace.lg(f"  Average success time: {total_success_time/n_complete_paths:.3f}")
            SlTrace.lg(f"  Maximum success time: {max_success_time:.3f}")
        SlTrace.lg()
        SlTrace.lg("    Computational Statistics")
        success_comp_stats.report_heading("  Successful")
        success_comp_stats.min.report_line("    minimum")
        success_comp_stats.max.report_line("    maximum")
        success_comp_stats.avg.report_line("    average")
        fail_comp_stats.report_heading("  Failed")
        fail_comp_stats.min.report_line("    minimum")
        fail_comp_stats.max.report_line("    maximum")
        fail_comp_stats.avg.report_line("    average")
        if longest_path_start is not None:
            SlTrace.lg(f"  {cb.loc2desc(longest_path_start)} starts the longest path({len(longest_path):d})"
                       + f"  {cb.path_desc(longest_path)}"
                       )

        SlTrace.lg("Do validation")
        ctv = ChessTourValidation(ncol=self.ncol, nrow=self.nrow,
                                       closed_tours=self.closed_tours)
        SlTrace.lg("Reporting any duplicate paths")
        ctv.report_duplicate_paths(self.displayed_paths)
        SlTrace.lg("\nVerifying valid tours")
        if not ctv.is_valid_tours(self.displayed_paths):
            SlTrace.lg("We have some looking to do")
        SlTrace.lg("End of Run")

    def next_tour(self):
        if self.kpths is not None and self.ipstart >= len(self.path_starts):
            return
        
        # ipstart index already bumped
        self.is_change_tour = True
        if self.kpths is not None:
            self.kpths.is_change_tour = True    # Short circuit stack_gen
            
    def prev_tour(self):
        if self.ipstart < 2:                    # Already bumped
            return
        
        self.ipstart -= 2                       # Already bumped to next
        self.is_change_tour = True
        if self.kpths is not None:
            self.kpths.is_change_tour = True    # Short circuit stack_gen

    def stop_gen(self):
        self.is_stop_gen = True
        if self.kpths is not None:
            self.kpths.is_stop_gen = True    # Short circuit stack_gen
        