import sys
import math
from collections import defaultdict

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

class Cell():
    def __init__(self, id, _type, initial_resources, *kwargs):
        self.id = id
        self.t = _type
        self.r = initial_resources
        self.n = kwargs
        self.my_ants = 0
        self.opp_ants = 0
        self.my_base = False
        self.opp_base = False

    @property
    def res(self):
        return self.r

    @res.setter
    def res(self, value):
        self.r = value

    @property
    def ma(self):
        return self.my_ants
    
    @ma.setter
    def ma(self, value):
        self.my_ants = value

    @property
    def oa(self):
        return self.opp_ants
    
    @oa.setter
    def oa(self, value):
        self.opp_ants = value

def bfs(G,s):
    # breath first search to find the shortest path between two points in graph
    v = set([s.id])
    q = [s.id]
    d = defaultdict(list)
    while q:
        cId = q.pop(0)
        if cId == s.id:
            d[cId] = [cId]
        for nId in G[cId].n:
            if nId == -1:
                continue
            if nId not in v:
                if d[nId] == [] or (len(d[nId]) != 0 and len(d[nId]) > len(d[cId]) + 1):
                    d[nId] = d[cId] + [nId]
                v.add(nId)
                q.append(nId)
    return d

def b2c(c, bases):
    # find the distance between a cell and the nearest base
    c2b = [len(DISTANCES[b.id][c.id]) for b in bases]
    return min(c2b), c2b.index(min(c2b))

cells = []

number_of_cells = int(input())  # amount of hexagonal cells in this map
for i in range(number_of_cells):
    # _type: 0 for empty, 1 for eggs, 2 for crystal
    # initial_resources: the initial amount of eggs/crystals on this cell
    # neigh_0: the index of the neighbouring cell for each direction
    cells.append(Cell(i, *[int(j) for j in input().split()]))

number_of_bases = int(input())
for i in input().split():
    cells[int(i)].my_base = True
for i in input().split():
    cells[int(i)].opp_base = True

# before the first game loop, need to calculate
# 1. the distance between each cell and the nearest base
# 2. amount of total crystals on the map
# 3. number of ants in the beginning
# 4. amount of total eggs on the map

CRYSTALS = sum([c.res for c in cells if c.t == 2])
EGGS = sum([c.res for c in cells if c.t == 1])

# need to figure out which are the half of crystals closest to my bases and only go after those
myBases = [c for c in cells if c.my_base]
oppBases = [c for c in cells if c.opp_base]


DISTANCES = {c.id: bfs(cells, c) for c in myBases + [c for c in cells if c.t != 0]}

# game loop
while True:
    my_score, opp_score = [int(j) for j in input().split()]
    for i in range(number_of_cells):
        # resources: the current amount of eggs/crystals on this cell
        # my_ants: the amount of your ants on this cell
        # opp_ants: the amount of opponent ants on this cell
        resources, my_ants, opp_ants = [int(j) for j in input().split()]
        cells[i].res = resources
        cells[i].ma = my_ants
        cells[i].oa = opp_ants

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # need to take into account the difference in ants between teams, if opponent has more ants need up the priority.

    ants = sum([c.ma for c in cells if c.ma > 0])
    myBases = [c for c in cells if c.my_base]
    eggs = [c for c in cells if c.t == 1]
    crystals = [c for c in cells if c.t == 2]

    CMD = []
    N = 0
    if ants < EGGS * 0.6 + (10 * number_of_bases):
        for cell in sorted(eggs, key=lambda c: min([len(DISTANCES[b.id][c.id]) for b in myBases])):
            if ants < len(CMD) * 2:
                break
            if cell.res > 0:
                N += 1
                c2b = [len(DISTANCES[b.id][cell.id]) for b in myBases]
                bId = myBases[c2b.index(min(c2b))].id
                priority = 4 + int(8 / len(DISTANCES[bId][cell.id]))
                for cId in DISTANCES[bId][cell.id]:
                    CMD.append(f"BEACON {cId} {priority}")
                myBases.append(cell)
            if N >= len(eggs) / 1.75:
                break
    N = 0
    for cell in sorted(crystals, key=lambda c: min([len(DISTANCES[b.id][c.id]) for b in myBases])):
        if ants < len(CMD) * 3:
            break
        if cell.res > 0:
            N += 1
            c2b = [len(DISTANCES[b.id][cell.id]) for b in myBases]
            bId = myBases[c2b.index(min(c2b))].id
            priority = 2 + int(8 / len(DISTANCES[bId][cell.id]))
            for cId in DISTANCES[bId][cell.id]:
                CMD.append(f"BEACON {cId} {priority}")
            myBases.append(cell)
        if N >= len(crystals) / 1.75:
            break
    
    print(';'.join(CMD))
    # WAIT | LINE <sourceIdx> <targetIdx> <strength> | BEACON <cellIdx> <strength> | MESSAGE <text>
    # print("WAIT")
