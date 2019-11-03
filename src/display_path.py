# display_path.py    14-Oct-2019
"""
Display Knights path from command line or stdin
"""
from tkinter import *

from chess_board import ChessBoard


ChessBoard.set_path_tracking()
mw = ChessBoard.mw
while True:
    inp = input("Enter path:")
    if ":" in inp:
        inp = inp.split(":")[1]
    path = inp.split()
    ChessBoard.display_path("",path)

mw.mainloop()                        