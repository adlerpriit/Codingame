import sys
# import math
import random
# import copy
from timeit import default_timer as timer


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


def place(n, m, x, r):
    if r == 0:
        if x == 5 or m[x][0] != '.' or m[x+1][0] != '.':
            return None
        for y in range(12):
            if m[x][y] != '.':
                m[x] = m[x][:y-1] + n[0] + m[x][y:]
                break
        for y in range(12):
            if m[x+1][y] != '.':
                m[x+1] = m[x+1][:y-1] + n[1] + m[x+1][y:]
                break
        return [x,x+1]
    if r == 2:
        if x == 0 or m[x][0] != '.' or m[x-1][0] != '.':
            return None
        for y in range(12):
            if m[x][y] != '.':
                m[x] = m[x][:y-1] + n[0] + m[x][y:]
                break
        for y in range(12):
            if m[x-1][y] != '.':
                m[x-1] = m[x-1][:y-1] + n[1] + m[x-1][y:]
                break
        return [x-1,x]
    if r == 3:
        n = n[::-1]
    for y in range(11, 0, -1):
        if m[x][y] == '.':
            m[x] = m[x][:y - 1] + n + m[x][y + 1:]
            return [x]
    return None


def crawl(m, x, y, c, M, n):
    if x < 0 or x > 5 or y < 0 or y > 11:
        return n
    # check if we have a match in the grid
    if m[x][y] == c and (x, y) not in M:
        M[x, y] = True
        n += 1
        n = crawl(m, x, y - 1, c, M, n)
        n = crawl(m, x, y + 1, c, M, n)
        n = crawl(m, x - 1, y, c, M, n)
        n = crawl(m, x + 1, y, c, M, n)
    elif m[x][y] == '0':
        M[x, y] = True
    return n


def collapse(m, M):
    # [print(m[i],file=sys.stderr) for i in range(len(m))]
    X, Y = None, None
    re = []
    for x, y in sorted(M, reverse=True):
        if x != X:
            re.append(x)
            if Y:
                m[X] = ''.join(['.' for i in range(Ymax - Y + 1)]) + m[X][:Y] + m[X][Ymax + 1:]
                # new line
            X = x
            Ymax = y
        Y = y
        # print([x,y],[X,Y,Ymin,Ymax],file=sys.stderr)
    m[X] = ''.join(['.' for i in range(Ymax - Y + 1)]) + m[X][:Y] + m[X][Ymax + 1:]
    # [print(m[i],file=sys.stderr) for i in range(len(m))]
    return re


def meval(m, re, sc, cp):
    # [print(m[i],file=sys.stderr) for i in range(len(m))]
    M = {}
    N = 0
    # sc = {'B':0,'CP':0,'CB':0,'GB':0}
    # 'B' 10 * nr of blocks (len(M))
    # 'CP' chain power. 0,8,16,32,etc
    # 'CB' colour bonus number of different colurs destroyed. 0 .. 16
    # 'GB' Group bonus. nr of blocks -4, max score 8, skulls don't count?
    for x in re:
        for y in range(11, 1, -1):
            if m[x][y] == '.':
                break
            if m[x][y] != '0':
                n = 0
                n = crawl(m, x, y, m[x][y], M, n)
                if n >= 4:
                    N += n
                    sc['B'] = len(M)
                    sc['GB'] += n
                    sc['CB'][m[x][y]] = 1
                    sc['CP'] = cp
    if N >= 4:
        re = collapse(m, M)
        if re:
            meval(m, re, sc, cp+1)


def output(n, m, d):
    # [print(m[i],file=sys.stderr) for i in range(len(m))]
    opt = [[None, None, 0]]
    # msc = 0
    # mx = None
    # R = None
    # N = n.pop(0)
    N = n.pop(0)
    for x in range(6):
        if m[x][1] == '.':
            for r in [1, 3]:
                tm, re = place(N, m[:], x, r)
                sc = {'B':0,'CP':0,'CB':{},'GB':0}
                if not tm:
                    continue
                meval(tm, re, sc, 0)
                tsc = 0 #TODO this does not work currently
                if d < 2:
                    tmx, tr, ttsc = output(n[:], tm, d + 1)
                    tsc += ttsc / 4
                if tsc > opt[0][-1]:
                    opt = [[x, r, tsc]]
                    # msc = tsc
                    # mx = x
                    # R = r
                if tsc == opt[0][-1] and opt[0][-1] != 0:
                    opt.append([x, r, tsc])
                    # print(tsc,file=sys.stderr)
    # print(opt,file=sys.stderr)
    return random.choice(opt)


def calcscore(sc):
    # sc = {'B':0,'CP':0,'CB':{},'GB':0}
    # 'B' 10 * nr of blocks (len(M))
    # 'CP' chain power. 0,8,16,32,etc
    # 'CB' colour bonus number of different colurs destroyed. 0 .. 16
    # 'GB' Group bonus. nr of blocks -4, max score 8, skulls don't count?
    m = 2 ** (sc['CP'] - 1) * 8 if sc['CP'] > 0 else 0
    m += 2 ** (len(sc['CB']) - 1) if len(sc['CB']) > 1 else 0
    m += sc['GB'] - 4 if sc['GB'] < 13 else 8
    m = 1 if m < 1 else 999 if m > 999 else m
    return 10 * sc['B'] * m


def genrand(n, m, x, r):
    tsc = 0
    for i in range(4):
        sc = {'B':0,'CP':0,'CB':{},'GB':0}
        N = n.pop(0)
        re = place(N, m, x, r)
        if not re:
            return tsc
        #if 3 < sc < 10:
        #    return 0
        meval(m, re, sc, 0)
        tsc += calcscore(sc) / (i + 1)
        x = int(random.random()*6)
        r = int(random.random()*4)
    return tsc


def genrand2(n, m, x, r):
    for i in range(5):
        sc = {'B': 0, 'CP': 0, 'CB': {}, 'GB': 0}
        N = n.pop(0)
        tm, re = place(N, m, x, r)
        if not tm:
            break
        x = int(random.random()*6)
        r = int(random.random()*4)
    return meval(m, re, sc, 0)


def outputrand(n, m, sTime):
    X = -1
    R = None
    SC = 0
    i = 0
    while timer() - sTime < 0.0999:
        i+=1
        x = int(random.random()*6)
        r = int(random.random()*4)
        sc = genrand(n[:], m[:], x, r)
        if sc > SC:
            SC = sc
            X = x
            R = r
    return X, R, SC, i


def init():
    m = [''.join(['.' for y in range(12)]) for x in range(6)]
    [print(m[x]) for x in range(6)]
    n = [''.join([str(random.randint(1, 5)) for c in range(2)]) for i in range(8)]
    print(n)
    return m, n


def updateturn(m, n, i, r):
    if not place(n.pop(0), m, i, r):
        exit()
    tsc = meval(m, i)
    print(', Score', tsc)
    n.append(''.join([str(int(random.random()*5)+1) for c in range(2)]))
    [print(m[x]) for x in range(6)]
    print(n)
    return tsc


def play():
    m, n = init()
    sc = 0
    past = None
    for t in range(200):
        sTime = timer()
        print("Turn", t, end="")
        # i, r, tsc = output(n[:], m[:], 0)
        i, r, tsc, c = outputrand(n, m, sTime)
        if not i:
            i, r = randi(m, past)
        past = i
        print('(',tsc,'), Iterations', c, ', Time', round(timer() - sTime, 5), end="")
        sc += updateturn(m, n, i, r)
    print(sc)


def randi(m, past):
    opt = []
    for x in range(1,5):
        if m[x][1] == '.':
            opt.append(x)
    if len(opt) > 1:
        I = random.choice(opt)
        while I == past:
            I = random.choice(opt)
    else:
        if opt:
            I = opt.pop()
        else:
            # I'm dead anyway
            I = int(random.random()*4) + 1
    R = int(random.random()*4)
    return I, R


def main():
    past = -1
    # game loop
    while True:
        sTime = timer()
        # n next pieces
        n = []
        # m my map
        m = []
        for i in range(8):
            # color_a: color of the first block
            # color_b: color of the attached block
            piece = ''.join(input().split())
            n.append(piece)
        score_1 = int(input())
        for i in range(12):
            m.append(list(input()))
        score_2 = int(input())
        for i in range(12):
            row = input()  # One line of the map ('.' = empty, '0' = skull block, '1' to '5' = colored block)

        m[:] = list(map(''.join, zip(*m)))
        I, R, SC, c = outputrand(n, m, sTime)
        print([I, R, SC, c], file=sys.stderr)

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # "x": the column in which to drop your blocks
        if I == -1:
            I, R = randi(m, past)
        print(str(I), str(R))
        past = I
        print("Time:", round(timer() - sTime, 5), file=sys.stderr)


if __name__ == "__main__":
    # execute only if run as a script
    main()
    # init()
    # play()
