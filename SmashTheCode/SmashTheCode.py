import sys
# import math
import random
# import copy
from timeit import default_timer as timer


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


def place(n, m, t, x, r):
    if r == 0:
        if x == 5 or t[x] < 0 or t[x + 1] < 0:
            return None
        m[x] = m[x][:t[x]] + n[0] + m[x][t[x] + 1:]
        t[x] -= 1
        m[x + 1] = m[x + 1][:t[x + 1]] + n[1] + m[x + 1][t[x + 1] + 1:]
        t[x + 1] -= 1
        return [x, x + 1]
    if r == 2:
        if x == 0 or t[x] < 0 or t[x - 1] < 0:
            return None
        m[x] = m[x][:t[x]] + n[0] + m[x][t[x] + 1:]
        t[x] -= 1
        m[x - 1] = m[x - 1][:t[x - 1]] + n[1] + m[x - 1][t[x - 1] + 1:]
        t[x - 1] -= 1
        return [x - 1, x]
    if r == 1:
        n = n[::-1]
    if t[x] > 0:
        m[x] = m[x][:t[x] - 1] + n + m[x][t[x] + 1:]
        t[x] -= 2
        return [x]
    return None


def crawl(m, x, y, c, M, MC, n):
    if x < 0 or x > 5 or y < 0 or y > 11:
        return n
    # check if we have a match in the grid
    if m[x][y] == c and (x, y) not in M and (x, y) not in MC:
        M[x, y] = True
        n += 1
        n = crawl(m, x, y - 1, c, M, MC, n)
        n = crawl(m, x, y + 1, c, M, MC, n)
        n = crawl(m, x - 1, y, c, M, MC, n)
        n = crawl(m, x + 1, y, c, M, MC, n)
    elif m[x][y] == '0':
        M[x, y] = True
    return n


def crawl2(m, x, y, c, M, MC, n):
    for d in [-1,1]:
        X = x + d
        if 0 <= X <= 5:
            if m[X][y] == c and (X, y) not in M:
                M[X, y] = True
                n += 1
                n = crawl2(m, X, y, c, M, MC, n)
            if m[X][y] == '0':
                M[X, y] = True
        Y = y + d
        if 0 <= Y <= 11:
            if m[x][Y] == c and (x, Y) not in M:
                M[x, Y] = True
                n += 1
                n = crawl2(m, x, Y, c, M, MC, n)
            if m[x][Y] == '0':
                M[x, Y] = True
    return n

def collapse(m, M, t):
    # [print(m[i],file=sys.stderr) for i in range(len(m))]
    X, Y = None, None
    re = []
    for x, y in sorted(M, reverse=True):
        if x != X:
            re.append(x)
            if Y:
                m[X] = ''.join(['.' for i in range(Ymax - Y + 1)]) + m[X][:Y] + m[X][Ymax + 1:]
                t[X] += Ymax - Y
                # new line
            X = x
            Ymax = y
        Y = y
        # print([x,y],[X,Y,Ymin,Ymax],file=sys.stderr)
    m[X] = ''.join(['.' for i in range(Ymax - Y + 1)]) + m[X][:Y] + m[X][Ymax + 1:]
    t[X] += Ymax - Y
    # [print(m[i],file=sys.stderr) for i in range(len(m))]
    return re


def meval(m, t, re, cp):
    # [print(m[i],file=sys.stderr) for i in range(len(m))]
    M = {}
    MC = {}
    sc = 0
    if not re:
        return sc
    for x in re:
        for y in range(11, -1, -1):
            if m[x][y] == '.':
                break
            if m[x][y] != '0' and (x, y) not in MC:
                n = 0
                n = crawl2(m, x, y, m[x][y], M, MC, n)
                if n >= 4:
                    sc += n
                    MC.update(M)
                    M = {}
                else:
                    M = {}
    if sc >= 4:
        re = collapse(m, MC, t)
        if re:
            p = 1 if cp == 0 else (2 ** (cp - 1)) * 8
            p = 999 if p > 999 else p
            sc += meval(m, t, re, cp + 1) * p

    return sc


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
                tm = place(N, m[:], x, r)
                if not tm:
                    continue
                tsc = meval(tm, x)
                if d < 2:
                    tmx, tr, ttsc = output(n[:], tm, d + 1)
                    tsc += ttsc / 2
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


def genrand(n, m, t, x, r):
    sc = 0
    # i = 5
    # if sum(t) < 33:
    #    i = 3
    i = round(sum(t) / 15) + 2
    for i in range(i):
        N = n.pop(0)
        re = place(N, m, t, x, r)
        if not re:
            return sc
        # if 3 < sc < 10:
        #    return 0
        sc += meval(m, t, re, 0) * (0.95 ** (i + 1))
        if sc > 800:
            return sc
        x = int(random.random() * 4) + 1
        r = int(random.random() * 4)
    return sc


def genrand2(n, m, x, r):
    for i in range(5):
        N = n.pop(0)
        tm = place(N, m, x, r)
        if not tm:
            break
        x = int(random.random() * 6)
        r = int(random.random() * 4)
    return meval(m, x)


def outputrand(n, m, t, sTime):
    X = -1
    R = None
    SC = 0
    i = 0
    while timer() - sTime < 0.0975:
        i += 1
        if sum(t) > 33:
            x = int(random.random() * 4) + 1
        else:
            x = int(random.random() * 6)
        r = int(random.random() * 4)
        sc = genrand(n[:], m[:], t[:], x, r)
        if sc > SC:
            SC = sc
            X = x
            R = r
        if SC > 800:
            return X, R, SC, i
    return X, R, SC, i


def init():
    m = [''.join(['.' for y in range(12)]) for x in range(6)]
    [print(m[x]) for x in range(6)]
    n = [''.join([str(random.randint(1, 5)) for c in range(2)]) for i in range(8)]
    print(n)
    return m, n


def updateturn(m, n, t, i, r):
    if not place(n.pop(0), m, t, i, r):
        exit()
    tsc = meval(m, t, [i], 0)
    print(', Score', tsc)
    n.append(''.join([str(int(random.random() * 5) + 1) for c in range(2)]))
    [print(m[x]) for x in range(6)]
    print(n)
    return tsc


def play():
    m, n = init()
    sc = 0
    for turn in range(200):
        sTime = timer()
        print("Turn", turn, end="")
        t = []
        for x in range(6):
            for y in range(11, -1, -1):
                if m[x][y] == '.':
                    t.append(y)
                    break
                if y == 0:
                    t.append(-1)
        # i, r, tsc = output(n[:], m[:], 0)
        i, r, tsc, c = outputrand(n, m, t, sTime)
        if i == -1:
            i, r = randi(m)
        print('(', round(tsc, 1), '), Iterations', c, ', Time', round(timer() - sTime, 5), end="")
        sc += updateturn(m, n, t, i, r)
    print(sc)


def randi(m):
    opt = []
    for x in range(6):
        if m[x][1] == '.':
            opt.append(x)
    if len(opt) > 1:
        I = random.choice(opt)
    else:
        if opt:
            I = opt.pop()
        else:
            # I'm dead anyway
            I = int(random.random() * 4) + 1
    R = random.choice([1, 3])
    return I, R


def main():
    # game loop
    while True:
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
        t = []
        for x in range(6):
            for y in range(11, -1, -1):
                if m[x][y] == '.':
                    t.append(y)
                    break
                if y == 0:
                    t.append(-1)

        # [print(m[i], file=sys.stderr) for i in range(6)]
        sTime = timer()
        I, R, SC, c = outputrand(n, m, t, sTime)
        if I == -1:
            I, R = randi(m)
        N = n.pop(0)
        re = place(N, m, t, I, R)
        # [print(m[i], file=sys.stderr) for i in range(6)]
        sc = meval(m, t, re, 0)
        print(["I:", I, "R:", R, "Sum(t):", sum(t), "mSC:", round(SC, 1), c], file=sys.stderr)
        print("Block:", N, "| Score:", sc, file=sys.stderr)
        # [print(m[i], file=sys.stderr) for i in range(6)]

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # "x": the column in which to drop your blocks
        print(str(I), str(R), str(c))
        print("Time:", round(timer() - sTime, 5), file=sys.stderr)


if __name__ == "__main__":
    # execute only if run as a script
    main()
    # init()
    # play()
