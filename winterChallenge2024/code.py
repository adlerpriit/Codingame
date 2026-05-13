import sys
import math
import random
from collections import namedtuple, defaultdict

# Grow and multiply your organisms to end up larger than your opponent.

Prot = namedtuple("Prot", ["A", "B", "C", "D"])

Dir = namedtuple("Dir", ["x", "y", "d"])

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __eq__(self, other):
        # this should work also for comparison with tuples, any object with x and y attributes
        return self.x == other.x and self.y == other.y

    @property
    def coord(self):
        return tuple([self.x, self.y])

class Protein(Tile):
    def __init__(self, x, y, protein_type):
        super().__init__(x, y)
        self.type = protein_type

class Organ(Tile):
    def __init__(self, x, y, organ_type, organ_id, organ_dir, organ_parent_id, organ_root_id):
        super().__init__(x, y)
        self.type = organ_type  # ROOT, BASIC, TENTACLE, SPORER, HARVESTER
        self.id = organ_id      # ID
        self.dir = organ_dir    # Direction
        self.pid = organ_parent_id  # Parent ID
        self.rid = organ_root_id    # Root ID

class Target(Tile):
    def __init__(self, x, y, parent_id, dir="X", command="BASIC"):
        super().__init__(x, y)
        self.id = 0 # only needed to place sporer
        self.pid = parent_id
        self.command = command
        self.dir = dir
        self.score = 9e9

    def eval(self, myProt, gradient, oppOrg, proteins, obstacles, dirs, cost):
        # self.x and self.y and self.pid are set
        # first evaluate sporer
        if all([a-b for a,b in zip(myProt,cost["TENTACLE"])]) >= 0:
            targets = []
            for d in dirs:
                # if there is opponent cell nearby, try to eat it
                t = Dir(self.x + d.x, self.y + d.y, d.d)
                if t in oppOrg:
                    oo = [o for o in oppOrg if o.x == t.x and o.y == t.y].pop()
                    target = Target(t.x, t.y, self.pid, d.d, "TENTACLE")
                    target.score = oo.id
                    targets.append(target)
            if targets:
                targets.sort(key=lambda x: x.score)
                target = targets[0]
                self.command = "TENTACLE"
                self.dir = target.dir
                self.score = target.score
                return
        if all([a-(b+c) for a,b,c in zip(myProt,cost["ROOT"],cost["SPORER"])]) >= 0:
            targets = []
            for d in dirs:
                targets.extend(get_spore_path(self, d, gradient, obstacles))
            if targets:
                targets.sort(key=lambda x: x.score)
                target = targets[0]
                # update self with best target so far
                self.command = "SPORER"
                self.dir = target.dir
                self.score = target.score
        elif all([a-b for a,b in zip(myProt,cost["HARVESTER"])]) >= 0:
            for d in dirs:
                t = Dir(self.x + d.x, self.y + d.y, d.d)
                if t in proteins:
                    if gradient[t.coord] < self.score:
                        self.command = "HARVESTER"
                        self.dir = d.d
                        self.score = gradient[t.coord]
        elif all([a-b for a,b in zip(myProt,cost["BASIC"])]) >= 0:
            for d in dirs:
                t = Dir(self.x + d.x, self.y + d.y, d.d)
                if t not in obstacles:
                    if gradient[t.coord] < self.score:
                        self.command = "BASIC"
                        self.dir = d.d
                        self.score = gradient[t.coord]


def bfs(proteins, wall, dirs):
    # myOrg is start positions
    v = set([t.coord for t in proteins])
    q = [t for t in proteins]
    D = {t.coord: 0 for t in proteins}
    while q:
        cC = q.pop(0)
        for d in dirs:
            nC = Tile(cC.x + d.x, cC.y + d.y)
            if nC in wall:
                continue
            if nC.coord not in v:
                D[nC.coord] = D[cC.coord] + 1
                v.add(nC.coord)
                q.append(nC)

    return D

def get_spore_path(sporer, dir, gradient, obstacles):
    t = Target(sporer.x + dir.x, sporer.y + dir.y, dir.d, sporer.id)
    while t.coord in gradient:
        if t in obstacles:
            continue
        if gradient[t.coord] < 2:
            continue
        t = Target(t.x + dir.x, t.y + dir.y, sporer.id, dir.d, "SPORE")
        t.score = gradient[t.coord] - 2
        yield t

# width: columns in the game grid
# height: rows in the game grid
width, height = [int(i) for i in input().split()]

dirs = [Dir(0, 1, "S"), Dir(0, -1, "N"), Dir(1, 0, "E"), Dir(-1, 0, "W")]

cost = {"BASIC": Prot(1, 0, 0, 0), 
        "HARVESTER": Prot(0, 0, 1, 1), 
        "TENTACLE": Prot(0, 1, 1, 0), 
        "SPORER": Prot(0, 1, 0, 1),
        "ROOT": Prot(1, 1, 1, 1)}

# game loop
while True:

    # define my and opponent organisms
    wall = []
    proteins = []
    myOrg = []
    oppOrg = []

    entity_count = int(input())
    for i in range(entity_count):
        inputs = input().split()
        x = int(inputs[0])
        y = int(inputs[1])  # grid coordinate
        _type = inputs[2]  # WALL, ROOT, BASIC, TENTACLE, HARVESTER, SPORER, A, B, C, D
        owner = int(inputs[3])  # 1 if your organ, 0 if enemy organ, -1 if neither
        organ_id = int(inputs[4])  # id of this entity if it's an organ, 0 otherwise
        organ_dir = inputs[5]  # N,E,S,W or X if not an organ
        organ_parent_id = int(inputs[6])
        organ_root_id = int(inputs[7])
        if _type in ["A", "B", "C", "D"]:
            proteins.append(Protein(x, y, _type))
        elif _type == "WALL":
            wall.append(Tile(x, y))
        elif _type in ["ROOT", "BASIC", "TENTACLE", "HARVESTER", "SPORER"]:
            if owner == 1:
                myOrg.append(Organ(x, y, _type, organ_id, organ_dir, organ_parent_id, organ_root_id))
            else:
                oppOrg.append(Organ(x, y, _type, organ_id, organ_dir, organ_parent_id, organ_root_id))

    # my_d: your protein stock
    myProt = Prot(*[int(i) for i in input().split()])
    # opp_d: opponent's protein stock
    oppProt = Prot(*[int(i) for i in input().split()])
    required_actions_count = int(input())  # your number of organisms, output an action for each one in any order          

    # calculate protein gradient for organism guidance
    obstacles = wall + myOrg + oppOrg + proteins
    gradient = bfs(proteins, obstacles, dirs)

    # bfs to be used for protein sources - for each type?
    # create gradient for each protein type across entire map.
    # organism can grow following the gradient. 

    # first should find a place for sporer, given that there is enough resources to grow sporer and one root
    # then try to find place for harvester, if there is protein source nearby and enough resources

    for y in range(height):
        for x in range(width):
            if Tile(x, y).coord in gradient:
                print(gradient[Tile(x, y).coord], end=" ", file=sys.stderr, flush=True)
            else:
                print("X", end=" ", file=sys.stderr, flush=True)
        print(file=sys.stderr, flush=True)

    myOrgs = {r.id: [o for o in myOrg if o.id == r.id or o.rid == r.id] for r in myOrg if r.type == "ROOT"}

    for rid in myOrgs:

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)

        # each organsim needs its own command, if no valid option is found, use WAIT
        # eval all argets of an organism (ROOT and all organs, that have it's ID as root ID)

        targets = []

        for o in myOrgs[rid]:
            # if organ type is "SPORER" evaluate all targets in visible range
            if o.type == "SPORER":
                if all([a-b for a,b in zip(myProt,cost["ROOT"])]) >= 0:
                    # sporer can only shoot in 1 direction
                    d = [d for d in dirs if d.d == o.dir][0]
                    targets.extend(get_spore_path(o, d, gradient, obstacles))
            else:
                # evaluate targets in 4 directions
                for d in dirs:
                    t = Dir(o.x + d.x, o.y + d.y, "X")
                    if t not in obstacles + targets:
                        target = Target(t.x, t.y, o.id)
                        # evaluate targets for each organ type and distance to protein source
                        # evaluate targets for "SPORER", "HARVESTER", "TENTACLE", "BASIC"
                        target.eval(myProt, gradient, oppOrg, proteins, obstacles, dirs, cost)
                        targets.append(target)

        if targets:
            for t in targets:
                print(f"{t.x} {t.y} {t.command} {t.dir} {t.score}", file=sys.stderr, flush=True)
            print("WAIT")
            # if there is no valid target, use WAIT
        else:
            print("WAIT")

        # rd = random.choice(dirs)
        # lo = myOrg[-1]

        # target = Dir(lo.x + rd.x, lo.y + rd.y, "X")

        # while target in wall or target in myOrg or target in proteins:
        #     lo = random.choice(myOrg)
        #     rd = random.choice(dirs)
        #     target = Dir(lo.x + rd.x, lo.y + rd.y, "X")

        # for d in dirs:
        #     scout = Dir(target.x + d.x, target.y + d.y, "X")
        #     if scout in proteins and myProt.C > 0 and myProt.D > 0:
        #         # there is ptotein source, don't grow there, to create harvester we need to see them from further away
        #         print(f"GROW {lo.id} {target.x} {target.y} HARVESTER {d.d}")
        #         break
        #     elif scout in oppOrg and myProt.B > 0 and myProt.C > 0:
        #         # if there is opponent cell nearby, try to eat it
        #         print(f"GROW {lo.id} {target.x} {target.y} TENTACLE {d.d}")
        #         break
        # else:
        #     print(f"GROW {lo.id} {target.x} {target.y} BASIC")
