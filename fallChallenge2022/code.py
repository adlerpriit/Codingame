import sys
from collections import namedtuple

P = namedtuple('Point', 'x y')

class Square:
    def __init__(self, scrap, owner, units, recycler, can_build, can_spawn, in_range):
        self.scrap = scrap
        self.owner = owner
        self.units = units # owner units
        self.recycler = recycler
        self.build = can_build
        self.spawn = can_spawn
        self.in_range = in_range

def build(base, gameMap):
    pos, SC = None, 0
    for p in base:
        if gameMap[p].build:
            in_range = [P(p.x + x, p.y + y) for x, y in [(0, 0), (1, 0), (-1, 0), (0, -1), (0, 1)]]
            try:
                sc = sum(gameMap[sq].scrap for sq in in_range if not gameMap[sq].in_range)
                if sc > SC and sc > 30:
                    SC = sc
                    pos = p
            except:
                pass
    return pos

def move(base, gameMap):
    mp = []
    U = [p for p in base if gameMap[p].units]
    T = [p for p in gameMap if gameMap[p].owner < 1 and gameMap[p].scrap and not gameMap[p].recycler]
    for u in U:
        if len(mp) > 2 and mp[-1][-1] in T:
            T.pop(T.index(mp[-1][-1]))
        D = {t: abs(t.x - u.x) + abs(t.y - u.y) - gameMap[t].units*2 for t in T}
        if D := sorted(D, key=lambda d: D[d]):
            for _ in range(gameMap[u].units):
                try:
                    mp.append((u, D.pop(0)))
                except:
                    return mp
    return mp

def spawn(base, gameMap):
    def _adj(p):
        for x, y in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
            T = P(p.x + x, p.y + y)
            try:
                if gameMap[T].scrap and gameMap[T].owner < 1 and not gameMap[T].recycler:
                    return True
            except:
                pass
        return False
    O = [p for p in gameMap if gameMap[p].owner == 0]
    def _dist(p):
        if O:
            return min([abs(o.x - p.x) + abs(o.y - p.y) - gameMap[o].units*2 for o in O])
        return 1
    sp = [p for p in base if gameMap[p].spawn and _adj(p)]
    sp = sorted(sp, key=lambda p: _dist(p))
    return sp


width, height = [int(i) for i in input().split()]

gameMap = {}
# game loop
while True:
    cmd = []
    my_matter, opp_matter = [int(i) for i in input().split()]
    for y in range(height):
        for x in range(width):
            # owner: 1 = me, 0 = foe, -1 = neutral
            gameMap[P(x, y)] = Square(*[int(k) for k in input().split()])

    base = [p for p in gameMap if gameMap[p].owner == 1]
    # find best recycler position in my base and build it
    if bp := build(base, gameMap):
        cmd.append('BUILD ' + str(bp.x) + ' ' + str(bp.y))

    # order some possible moves and excecute
    if mp := move(base, gameMap):
        cmd.extend(['MOVE 1 ' + ' '.join(str(i) for i in list(f) + list(t)) for (f, t) in mp])

    # spawn as many new robots as you can
    if sp := spawn(base, gameMap):
        cmd.extend(['SPAWN 1 ' + str(p.x) + ' ' + str(p.y) for p in sp])

    if not cmd:
        cmd.append('WAIT')

    print(';'.join(cmd))

