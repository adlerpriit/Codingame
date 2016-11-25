import sys
import math
import random
import copy
from timeit import default_timer as timer

#global variables
width, height, myID = [int(i) for i in input().split()]

def cBoxes(p, m, R, o):
    bC = 0
    x, y = p
    nS = []
    if m[y][x] != '.':
        return (0,nS)
    nS.append(p)
    for u in range(1, R):
        if y - u < 0 or m[y - u][x] in ['X','b'] or (x,y-u) in o:
            break
        if m[y - u][x] != '.':
            bC += 1
            break
        nS.append((x,y-u))
    for d in range(1, R):
        if y + d >= height or m[y + d][x] in ['X','b'] or (x,y+d) in o:
            break
        if m[y + d][x] != '.':
            bC += 1
            break
        nS.append((x,y+d))
    for l in range(1, R):
        if x - l < 0 or m[y][x - l] in ['X','b'] or (x-l,y) in o:
            break
        if m[y][x - l] != '.':
            bC += 1
            break
        nS.append((x-l,y))
    for r in range(1, R):
        if x + r >= width or m[y][x + r] in ['X','b'] or (x+r,y) in o:
            break
        if m[y][x + r] != '.':
            bC += 1
            break
        nS.append((x+r,y))
    return [bC,nS]

def bSafe(c,b,m,R,o,bT):
    X,Y = c
    for x in range(1,R):
        x,y = X+x,Y
        if x < 0 or x>=width or m[y][x] == 'X':
            break
        if m[y][x] == '.':
            if (x,y) not in bT or bT[x,y] > b[c]['t']:
                bT[x,y] = b[c]['t']
        else:
            if m[y][x] == 'b' and b[x,y]['t'] > b[c]['t']:
                b[x,y]['t'] = b[c]['t']
            break
        if (x,y) in o:
            break
    for x in range(1,R):
        x,y = X-x,Y
        if x < 0 or x>=width or m[y][x] == 'X':
            break
        if m[y][x] == '.':
            if (x,y) not in bT or bT[x,y] > b[c]['t']:
                bT[x,y] = b[c]['t']
        else:
            if m[y][x] == 'b' and b[x,y]['t'] > b[c]['t']:
                b[x,y]['t'] = b[c]['t']
            break
        if (x,y) in o:
            break
    for y in range(1,R):
        x,y = X,Y+y
        if y < 0 or y>=height or m[y][x] == 'X':
            break
        if m[y][x] == '.':
            if (x,y) not in bT or bT[x,y] > b[c]['t']:
                bT[x,y] = b[c]['t']
        else:
            if m[y][x] == 'b' and b[x,y]['t'] > b[c]['t']:
                b[x,y]['t'] = b[c]['t']
            break
        if (x,y) in o:
            break
    for y in range(1,R):
        x,y = X,Y-y
        if y < 0 or y>=height or m[y][x] == 'X':
            break
        if m[y][x] == '.':
            if (x,y) not in bT or bT[x,y] > b[c]['t']:
                bT[x,y] = b[c]['t']
        else:
            if m[y][x] == 'b' and b[x,y]['t'] > b[c]['t']:
                b[x,y]['t'] = b[c]['t']
            break
        if (x,y) in o:
            break
    bT[X,Y] = b[c]['t']

def getInput(h):
    m = []
    b = {}
    o = {}
    me = {}
    for i in range(h):
        m.append(list(input()))
    e = int(input())
    for i in range(e):
        etype, owner, x, y, paramA, paramB = [int(j) for j in input().split()]
        if etype == 0 and owner == myID:
            me = {'p': (x, y), 'b': paramA, 'r': paramB}
        if etype == 1:
            m[y][x] = 'b'
            b[x,y] = {'t': paramA, 'r': paramB, 'o':owner}
        if etype == 2:
            o[x,y] = {'id':paramA}
    #[print(" ".join(x), file=sys.stderr) for x in m]
    bT = {}
    for bl in sorted(b,key=lambda k: b[k]['t']):
        bSafe(bl,b,m,b[bl]['r'],o,bT)
    obj = {'b':b,'o':o,'me':me,'bT':bT}
    return(m,obj)

def eXplore(m,pos,R,d,G,o):
    for x,y in [(-1,0),(1,0),(0,-1),(0,1)]:
        X = pos[0] + x
        Y = pos[1] + y
        tdz = 0 if (X,Y) not in o['bT'] else G[pos]['dz']+1
        if X < 0 or X >= width or Y < 0 or Y >= height or m[Y][X] != '.' or ((X,Y) in G and G[X,Y]['d'] < d) or ((X,Y) in o['bT'] and (tdz - o['bT'][X,Y] >= 0 or o['bT'][X,Y] <= 2)):
            continue
        if (X,Y) not in G:
            b = cBoxes((X,Y),m,R,o['o'])
            if (X,Y) in o['o'] and o['me']['b'] < 6:
                b[0]+=o['o'][X,Y]['id']+2
        else:
            b = G[X,Y]['b']
        G[X,Y] = {'d':d,'s':pos,'b':b,'dz':tdz}

def getGraph(m,obj):
    me = obj['me']
    dz = 1 if me['p'] in obj['bT'] else 0
    G = {me['p']:{'d':0,'b':cBoxes(me['p'],m,me['r'],obj['o']),'dz':dz}}
    for d in range(1,15):
        for pos in list(G.keys()):
            eXplore(m,pos,me['r'],d,G,obj)
    return G
    #print(len(G),G,file=sys.stderr)


#meLast = None
# game loop
while True:
    sTime = timer()
    m,obj = getInput(height)
    G = getGraph(m,obj)
    AvailMoves = set(G.keys())
    Opt = sorted(G,key=lambda c:G[c]['d'])
    Opt = sorted(Opt,key=lambda c:G[c]['b'][0],reverse=True)
    Opt = sorted(Opt,key=lambda c:G[c]['dz'])
    #[print(c,"d:",G[c]['d'],"nrS:",len(AvailMoves - set(G[c]['b'][1])),"bC:",G[c]['b'][0],"dz:",G[c]['dz'],(0 if c not in obj['bT'] else obj['bT'][c]),file=sys.stderr) for c in Opt]
    Coords = Opt[0]
    c = obj['me']['p']
    print(c,"d:",G[c]['d'],"nrS:",len(AvailMoves - set(G[c]['b'][1])),"bC:",G[c]['b'][0],"dz:",G[c]['dz'],(0 if c not in obj['bT'] else obj['bT'][c]),file=sys.stderr)
    #print(Coords,file=sys.stderr)
    for c in Opt:
        if len(AvailMoves - set(G[c]['b'][1])) == 0:
            continue
        Coords = c
        break
    Target = Coords
    c = Target
    print(c,"d:",G[c]['d'],"nrS:",len(AvailMoves - set(G[c]['b'][1])),"bC:",G[c]['b'][0],"dz:",G[c]['dz'],(0 if c not in obj['bT'] else obj['bT'][c]),file=sys.stderr)
    while 's' in G[Coords] and G[Coords]['s'] != obj['me']['p']:
        Coords = G[Coords]['s']
    c = Coords
    print(c,"d:",G[Target]['d'],"nrS:",len(AvailMoves - set(G[c]['b'][1])),"bC:",G[c]['b'][0],"dz:",G[c]['dz'],(0 if c not in obj['bT'] else obj['bT'][c]),file=sys.stderr)
    #print(Coords,file=sys.stderr)
    act = "MOVE" 
    if (((G[obj['me']['p']]['b'][0] > 0 and obj['me']['b'] > 0 and G[Target]['d'] == 0) or
         (G[obj['me']['p']]['b'][0] > 0 and obj['me']['b'] > 1 and G[Target]['d'] >= 4) or
         (G[obj['me']['p']]['b'][0] > 1 and obj['me']['b'] > 0 and G[Target]['d'] >= 4))
        and
         (obj['me']['p'] not in obj['bT'] or obj['bT'][obj['me']['p']] > 4)):
        act = "BOMB"

    print(act,Coords[0],Coords[1],round(timer() - sTime, 4))