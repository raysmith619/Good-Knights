# paths_gen.py
"""
Generate a list of paths
"""

from datetime import datetime


from select_trace import SlTrace
from select_error import SelectError
from comp_stats import ResultCompStats
from chess_board import loc2desc, path_desc
from chess_board_display import ChessBoardDisplay, display_path
from knights_paths import KnightsPaths
from displayed_path import DisplayedPath

class PathsGen:
    """ Generate and manipulate a list of paths
    """
    def __init__(self, path_starts=None, arrange=None,
                 time_out=None,
                 closed_tours=None,
                 width=400,
                 height=400,
                 nrows = 8,
                 ncols = 8,
                 max_look_ahead=5):
        self.width = width
        self.height = height
        self.nrows = nrows
        self.ncols = ncols
        self.time_out = time_out
        self.path_starts = path_starts
        self.closed_tours = closed_tours
        self.max_look_ahead = max_look_ahead
        self.arrange = arrange
        self.sqno = 0        # number within list
        self.displayed_paths = []   # Repository of displayed paths

    def go(self):
        n_complete_paths = 0
        n_having_complete_path = 0
        n_with_no_complete_path = 0
        n_with_multiple_complete_paths = 0
        longest_path = []
        longest_path_start = None
        n_closed_tour = 0
        max_success_time = None     # Maximum successful duration
        total_success_time = 0      # Total successful times        

        success_comp_stats = ResultCompStats()
        fail_comp_stats = ResultCompStats()    
        for loc in self.path_starts:
            self.sqno += 1
            SlTrace.lg(f"{self.sqno:2d}: {loc2desc(loc)}", dp=3)
            kpths = KnightsPaths(loc=loc, closed_tours=self.closed_tours,
                                 time_limit=self.time_out,
                                 max_look_ahead=self.max_look_ahead)
            time_beg = datetime.now()
            path = kpths.next_path()
            nbackup = kpths.get_nbackup()
            track_level = kpths.get_track_level()
            time_end = datetime.now()
            time_dur = (time_end-time_beg).total_seconds()
            npath = kpths.get_ncomplete_path()
            ntrack_ntie = kpths.ntrack_ntie
            ntie = kpths.ntie
            comp_stats = (f"Comp Stats: time={time_dur:.3f} paths={npath}"
                        f" backup={nbackup} track_level={track_level} tie_track={ntrack_ntie} ntie={ntie}")
            if path is None:
                what = "tours" if self.closed_tours else "paths"
                SlTrace.lg(f"No {what} found - {npath} complete paths found")
                SlTrace.lg(f"    {comp_stats}")
                fail_comp_stats.add(time_dur=time_dur, npath=npath, nbackup=nbackup,
                                track_level=track_level, ntrack_ntie=ntrack_ntie,
                                ntie=ntie)
                pth = kpths.last_complete_path
                if pth is None:
                    pth_desc = "NO PATH"
                    pth = ""
                elif len(pth) < self.nrows*self.ncols:
                    pth_desc = "INCOMPLETE"
                else:
                    pth_desc = "NOT CLOSED"
                    kpths.is_complete_tour = True
                path_description = f" {self.sqno}: {loc2desc(loc)} {pth_desc} {time_dur:.3f} sec: "
                SlTrace.lg(path_description)
                dp = display_path(pth, desc=path_description, 
                                   width=self.width, height=self.height)
                self.displayed_paths.append(DisplayedPath(disp_board=dp, desc=path_desc,
                                                          is_closed_tour=kpths.is_closed_tour,
                                                          is_complete_tour=kpths.is_complete_tour))
                continue
            
            if len(path) == self.ncols*self.nrows:
                kpths.is_complete_tour = True
                success_comp_stats.add(time_dur=time_dur, npath=npath, nbackup=nbackup,
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
                           + f" from {loc2desc(path[0])}"
                           + f" to {loc2desc(path[-1])}"
                           + f" path: {path_desc(path)}")
                n_complete_paths += 1
                n_having_complete_path += 1
                total_success_time += time_dur
                if max_success_time is None or time_dur > max_success_time:
                    max_success_time = time_dur
                path_description = f" {self.sqno}: {loc2desc(loc)} {ct_desc} {time_dur:.3f} sec: "
                SlTrace.lg(path_description)
                dp = display_path(path, desc=path_description, 
                                   width=self.width, height=self.height)
                self.displayed_paths.append(DisplayedPath(disp_board=dp, desc=path_desc,
                                                        is_closed_tour=kpths.is_closed_tour,
                                                        is_complete_tour=kpths.is_complete_tour))
            else:
                dp = display_path("Short Path", path, desc="short_path")
                self.displayed_paths.append(DisplayedPath(disp_board=dp, desc="Short Path"))
            SlTrace.lg(f"    {comp_stats}")
                        
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
            SlTrace.lg(f"  {loc2desc(longest_path_start)} starts the longest path({len(longest_path):d})"
                       + f"  {path_desc(longest_path)}"
                       )
        