# displayed_path.py
"""
Data for displayed path
"""
from select_trace import SlTrace
from select_error import SelectError
from chess_board import ChessBoard
from chess_board_display import ChessBoardDisplay

class DisplayedPath:
    """ Displayed path info to facilitate display arrangement/access/manipulation
    """
    org_no = None       # Original order
    def __init__(self,
                 path=None, disp_board=None, org_no=None, time=None, desc=None,
                is_closed_tour=False,
                is_complete_tour=False
                ):
        """ Setup
        :path: path (list of locs in order)
        :disp_board: ChessBoardDisplay instance
        :org_no: original order(starting at one) default: numbered as called
        :time: time for path creation Default: Unknown
        :description: description of display default: None
        """
        if disp_board is None:
            raise SelectError("Required disp_board is missing")
        self.disp_board = disp_board
        if path is None:
            path = disp_board.path
        self.path = path
        if org_no is None:
            if DisplayedPath.org_no is None:
                DisplayedPath.org_no = 0
            DisplayedPath.org_no += 1
            org_no = DisplayedPath.org_no
        self.org_no = org_no
        self.desc = desc
        self.time = time
        self.disp_board.wm.protocol("WM_DELETE_WINDOW", self.destroy)
        self.is_closed_tour = is_closed_tour
        self.is_complete_tour = is_complete_tour
        
    def destroy(self):
        if self.disp_board is not None:
            self.disp_board.destroy()
            
    def get_wm(self):
        return self.disp_board.wm

    def hide(self):
        wm = self.get_wm()
        wm.withdraw()
        
    def show(self):
        wm = self.get_wm()
        wm.update()
        wm.deiconify()


    def get_size_pos(self):
        """ Get widow position and size
        :returns: (w, h, x, y) in pixels
        """
        wm = self.get_wm()                      # Protect against closed windows
        if wm is None:
            self.recreate()
        geo = self.get_wm().geometry()
        args1 = geo.split("+")
        wh_strs = args1[0].split("x")
        width, height = int(wh_strs[0]), int(wh_strs[1])
        x, y = int(args1[1]), int(args1[2])
        return (width, height, x, y)


    def recreate(self):
        """ Recreate displayed path
        """
        SlTrace.lg(f"recreate display: {ChessBoard.path_desc(self.path)}")
        disp_board = ChessBoardDisplay.display_path(self.path,
                     desc=self.disp_board.desc, nrow=self.disp_board.nrow,
                     ncol=self.disp_board.ncol,
                     width=self.disp_board.width, height=self.disp_board.height)
        self.disp_board = disp_board
        self.path = disp_board.path
        
            
    def resize(self, width=None, height=None, x=None, y=None):
        """ Resize/position display window
        :width: window width default: unchanged
        :height: window height default unchanged
        :x: x window position, default unchanged
        :y: y window position default unchanged
        """
        disp_width, disp_height, disp_x,  disp_y = self.get_size_pos()
        if width is None:
            width = disp_width
        if height is None:
            height = disp_height
        if x is None:
            x = disp_x
        if y is None:
            y = disp_y
        if width != disp_width or height != disp_height:
            disp_board = ChessBoardDisplay.display_path(self.path,
                         desc=self.disp_board.desc, nrow=self.disp_board.nrow,
                         ncol=self.disp_board.ncol,
                         width=width, height=height)
            if self.disp_board is not None:
                self.disp_board.destroy()
                ###self.disp_board.wm.destroy()
            self.disp_board = disp_board
        new_wm = self.disp_board.wm
        width = int(width)
        height = int(height)
        x = int(x)
        y = int(y)
        geo = f"{width}x{height}+{x}+{y}"
        new_wm.geometry(geo)
        