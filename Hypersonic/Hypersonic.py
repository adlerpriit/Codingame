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

def bSafe(c,b,m,R,bT):
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
        bSafe(bl,b,m,b[bl]['r'],bT)
    obj = {'b':b,'o':o,'me':me,'bT':bT}
    return(m,obj)

def evalRound(m,obj,G):
    # 10 options to make a move.
    # place a bomb and stay + 4 moves (at most)
    # don't place a bomb and stay + 4 moves (at most)
    #print("current:",obj['me'],file=sys.stderr)
    mx,my = obj['me']['p']
    for act in ['MOVE','BOMB']:
        if (obj['me']['b'] == 0 or (mx,my) in obj['b']) and act == 'BOMB':
            continue
        for x,y in [(-1,0),(1,0),(0,0),(0,-1),(0,1)]:
            X = obj['me']['p'][0] + x
            Y = obj['me']['p'][1] + y
            if X < 0 or X >= width or Y < 0 or Y >= height or m[Y][X] != '.':
                continue
            #print(" ".join([str(s) for s in [act,X,Y]]),file=sys.stderr)
            G[" ".join([str(s) for s in [act,X,Y]])] = 0

def prCell(x,y,c,obj,boxes,objects):
    if (x,y) in obj['o']:
        objects[x,y] = 1
        return 1
    if m[y][x] == 'b':
        if (x,y) in obj['b']:
            obj['b'][x,y]['t'] = 0
        return 1
    if m[y][x] != '.':
        try:
            boxes[x,y].append(obj['b'][c]['o'])
        except:
            boxes[x,y] = [obj['b'][c]['o']]
        return 1
    return 0

def bExplode(c,m,obj,boxes,objects):
    x,y = c
    R = obj['b'][c]['r']
    if c == obj['me']['p']:
        return None
    for u in range(1,R):
        if y - u < 0 or m[y-u][x] == 'X':
            break
        if [x,y-u] == obj['me']['p']:
            return None
        if prCell(x, y-u, c, obj, boxes, objects):
            break
    for d in range(1,R):
        if y + d >= height or m[y+d][x] == 'X':
            break
        if [x,y+d] == obj['me']['p']:
            return None
        if prCell(x, y+d, c, obj, boxes, objects):
            break
    for l in range(1,R):
        if x - l < 0 or m[y][x-l] == 'X':
            break
        if [x-l,y] == obj['me']['p']:
            return None
        if prCell(x-l, y, c, obj, boxes, objects):
            break
    for r in range(1,R):
        if x + r >= width or m[y][x+r] == 'X':
            break
        if [x+r,y] == obj['me']['p']:
            return None
        if prCell(x+r, y, c, obj, boxes, objects):
            break
    if obj['b'][c]['o'] == myID:
        obj['me']['b']+=1
    del obj['b'][c]
    return 1

def updateMap(m,obj,command):
    sc = 0
    #bombs countdown reduce
    for c in obj['b']:
        obj['b'][c]['t'] -= 1
    #bombs explode if countdown 0 (initiates also other bombs in range) does not go through items either (so should add them to map) (mark boxes)
    boxes = {}
    objects = {}
    bombs = {}
    t = sorted(obj['b'],key=lambda c: obj['b'][c]['t'])
    while t and obj['b'][t[0]]['t'] == 0:
        status = bExplode(t[0],m,obj,boxes,objects)
        if not status:
            #I'm dead and game over. this is dead end and should not be scored
            return -10
        bombs[t[0]] = 1
        t = sorted(obj['b'],key=lambda c: obj['b'][c]['t'])
    #boxes destoried get points to all players whos bomb reached them - remove destroyed boxes
    for c in objects:
        del obj['o'][c]
    for (x,y) in bombs:
        m[y][x] = '.'
    for (x,y) in boxes:
        # new items appear
        if myID in boxes[x,y]:
            sc+=1
        obj['o'][x,y] = {'id':int(m[y][x])}
        m[y][x] = '.'
    #players move (place bomb, move -- only me, currently)
    (act,X,Y) = command.split()
    #bombs appear, bombs appear as they were placed before movement
    mx,my = obj['me']['p']
    if act == 'BOMB' and m[my][mx] == '.':
        obj['b'][mx,my] = {'t':8,'r':obj['me']['r'],'o':myID}
        obj['me']['b']-=1
        # sc+=0.1
        m[my][mx] = 'b'
    obj['me']['p'] = [int(X),int(Y)]
    return sc

def runRound(m,obj,meLast):
    me = obj['me']
    scM = {}
    for y in range(height):
        for x in range(width):
            scM[" ".join(str(i) for i in [x, y])] = (
            cBoxes([x, y], m, width, height, me['r']), (abs(me['p'][0] - x) + abs(me['p'][1] - y)))

    sortedscM = sorted(scM, key=lambda d: scM[d][1])
    sortedscM = sorted(sortedscM, key=lambda c: scM[c][0], reverse=True)

    coord = sortedscM[0]
    act = "BOMB" if (scM[sortedscM[0]][1] == 0 and me['b'] != 0) or meLast == me else "MOVE"

    return(act, coord)

def simulate(m,obj,cmd,depth,C):
    C[depth] += 1
    sc = updateMap(m,obj,cmd)
    if depth == 8 or sc < 0:
        #print(sc,file=sys.stderr)
        return sc
    G = {}
    evalRound(m,obj,G)
    for CMD in G:
        sc += simulate(copy.deepcopy(m),copy.deepcopy(obj),CMD,depth+1,C)
    return(sc)

def eXplore(m,pos,R,d,G,o):
    for x,y in [(-1,0),(1,0),(0,-1),(0,1)]:
        X = pos[0] + x
        Y = pos[1] + y
        tdz = 0 if (X,Y) not in o['bT'] else G[pos]['dz']+1
        if X < 0 or X >= width or Y < 0 or Y >= height or m[Y][X] != '.' or ((X,Y) in G and G[X,Y]['d'] < d) or ((X,Y) in o['bT'] and tdz - o['bT'][X,Y] >= 0 and o['bT'][X,Y] < 3):
            continue
        if (X,Y) not in G:
            b = cBoxes((X,Y),m,R,o['o'])
            if (X,Y) in o['o']:
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
    #g = {}
    m,obj = getInput(height)
    #meP = obj['me']['p']
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
         (G[obj['me']['p']]['b'][0] > 1 and obj['me']['b'] > 0 and G[Target]['d'] >= 4) or
         (G[obj['me']['p']]['b'][0] > 0 and obj['me']['b'] > 1 and G[Target]['d'] >= 4)) and (obj['me']['p'] not in obj['bT'] or obj['bT'][obj['me']['p']] > 3)):
        act = "BOMB"

    print(act,Coords[0],Coords[1],round(timer() - sTime, 4))
    #evalRound(m,obj,g)
    # C = {}
    # for i in range(16): C[i] = 0
    # for CMD in g:
    #     M = copy.deepcopy(m)
    #     OBJ = copy.deepcopy(obj)
    #     g[CMD] = simulate(M,OBJ,CMD,0,C)
    
    #print(g,file=sys.stderr)
    # print(sum(C.values()),C,file=sys.stderr)
    #act,coord = runRound(m,obj,meLast)
    #cmd = list(g.keys())
    #random.shuffle(cmd)
    #cmd = sorted(cmd,key=lambda c:g[c],reverse=True)
    #print(cmd[0])
    #meLast = obj['me']
    #print("time:", , file=sys.stderr)