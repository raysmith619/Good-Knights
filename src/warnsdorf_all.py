# Knight's Tour using Warnsdorff's Rule
# warnsdorf_all.py
# do all starting sqares
# http://en.wikipedia.org/wiki/Knight's_tour
# FB - 20121216
from heapq import heappush, heappop # for priority queue
import random
import string
cbx = 8; cby = 8 # width and height of the chessboard
# directions the Knight can move on the chessboard
dx = [-2, -1, 1, 2, -2, -1, 1, 2]
dy = [1, 2, 2, 1, -1, -2, -2, -1]

def is_neighbor(loc1, loc2):
    """ Test if loc2 is one knight move away from loc1
    :loc1: (icol,irow) board location row index(0-cbx) col index(0-cby)
    :loc2: (icol,irow) board location
    :returns: True if neighbor
    """
    ic, ir = loc1
    ic2, ir2 = loc2
    for i in range(len(dx)):
        ic_new = ic + dx[i]
        ir_new = ir + dy[i]
        if ic_new == ic2 and ir_new == ir2:
            return True         # move to loc2
    
    return False


def tuple2desc(tp):
    """ Convert ci,ri tuple to description string
    :tp: (ci,ri) tuple
    :returns: algebraic description string
    """
    col_index,row_index = tp[0],tp[1]
    c1=chr(col_index + ord('a'))
    c2=chr(row_index + ord('1'))
    loc_str = c1+c2
    return loc_str


# start the Knight each position
for irow in range(cby):
    for icol in range(cby):
        moves = []              # moves (icol,irow) in order
        kx = icol
        ky = cby - irow-1
        cb = [[0 for x in range(cbx)] for y in range(cby)] # chessboard    initialization
        for k in range(cbx * cby):
            cb[ky][kx] = k + 1
            moves.append((kx, cby-ky-1))
            pq = [] # priority queue of available neighbors
            for i in range(8):
                nx = kx + dx[i]; ny = ky + dy[i]
                if nx >= 0 and nx < cbx and ny >= 0 and ny < cby:
                    if cb[ny][nx] == 0:
                        # count the available neighbors of the neighbor
                        ctr = 0
                        for j in range(8):
                            ex = nx + dx[j]; ey = ny + dy[j]
                            if ex >= 0 and ex < cbx and ey >= 0 and ey < cby:
                                if cb[ey][ex] == 0: ctr += 1
                        heappush(pq, (ctr, i))
            # move to the neighbor that has min number of available neighbors
            if len(pq) > 0:
                (p, m) = heappop(pq)
                kx += dx[m]; ky += dy[m]
            else: break
        
        # print cb
        print("\nstarting at: {}".format(tuple2desc((icol,irow))))
        for cy in range(cby):
            for cx in range(cbx):
                n = cb[cy][cx]
                if n == 1 or n == cbx*cby:
                    lt = "["
                    rt = "]"
                else:
                    lt = rt = " "
                print("{}{:2d}{}".format(lt,n,rt), end="")
            print()
            
        # Check is_neighbor for each move
        for imove in range(len(moves)):
            if imove > 0:
                loc1 = moves[imove-1]
                loc2 = moves[imove]
                if not is_neighbor(loc1, loc2):
                    print("{} not neighbor of {}".format(loc1, loc2))
                    break
        if is_neighbor(moves[-1], moves[0]):
            print("{} completes closed tour starting at {}".format(tuple2desc(moves[-1]), tuple2desc(moves[0])))
