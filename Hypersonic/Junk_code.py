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
