import sys
import math
import random

DIRS = {'N':(-1,0), 'NE':(-1,1), 'E':(0,1), 'SE':(1,1),
        'S':(1,0), 'SW':(1,-1), 'W':(0,-1), 'NW':(-1,-1)}

class wondelWoman(object):


    def __init__(self, id):
        self.id = id
        self._grid = []

    def update(self, x, y, grid):
        """
        Update unit (wonam position and reset valid commands)
        """
        self.x = x
        self.y = y
        self._grid = grid  # reference to object, do not change
        self.valid_commands = []

    @property
    def action(self):
        if not self.valid_commands:
            return False, (0, 0), 0
        targets = {}
        for act in self.valid_commands:
            my, mx = [a + b for (a,b) in zip((self.y,self.x), DIRS[act[2]])]
            by, bx = [a + b for (a,b) in zip((my,mx), DIRS[act[3]])]
            # not if what not, but score moves. Move that get's point get's a good score
            #  * move that prevents opponent to get point get's good score
            #  * move that moves up get's better score than level and fall loses points
            if (grid.square_value(self.y, self.x) <= grid.square_value(my, mx) and
                (grid.square_value(by,bx) < 3)):
                targets[act] = (grid.square_value(my, mx) - grid.square_value(self.y, self.x),
                                grid.square_value(by,bx))
        if targets:
            sorted_targets = sorted(targets, key=lambda a: targets[a][1])
            sorted_targets = sorted(sorted_targets, key=lambda a: targets[a][0])
            act = sorted_targets.pop()
            return act, targets[act], len(self.valid_commands)
        return (self.valid_commands[int(random.random() * len(self.valid_commands))],
                (-1, -1),
                len(self.valid_commands))

    @property
    def log(self):
        return (self.id, len(self.valid_commands), [self.x, self.y])

class Grid(object):
    def __init__(self, size):
        print(size, file=sys.stderr)
        self._size = size
        self._grid = [[] for i in range(size)]

    def update(self, i, row):
        self._grid[i] = [-1 if s=='.' else int(s) for s in row]

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    def square_value(self, y, x):
        return self._grid[y][x]

class Action(object):
    def __init__(self, act, cx, cy):
        self._act = act
        self._atype, self._wid, self._mdir, self._bdir = act
        if self._atype == 'PUSH&BUILD':
            self._push = [a + b for (a,b) in zip((cy,cx), DIRS[self._mdir])]
            self._build = [a + b for (a,b) in zip(self._push, DIRS[self._bdir])]
        else:  # 'MOVE&BUILD'
            self._move = [a + b for (a,b) in zip((cy,cx), DIRS[self._mdir])]
            self._build = [a + b for (a,b) in zip(self._move, DIRS[self._bdir])]

    def score(self, grid, mteam, oteam):
        #scoring schema
        # I get point 3pt
        # I move up (< 3) 2pt
        # I move on same level 1pt
        # I move down 0pt
        # I have only one place to move 4pt
        # Push opponent off from 2/3 to 0 4pt
        #  * Difference needs to be 2, so opponent can't move back easily
        # Pushed oppeonent does not have moving options 10pt
        #  Block opponent building/moving capacity by moving 2pt
        #  Block opponent building/moving capacity by building 3pt
        #    * should be connected by number of remaining moves by opponent

grid = Grid(int(input()))  # size
units_per_player = int(input())  # units per player
mteam = [wondelWoman(i) for i in range(units_per_player)]  # my team
oteam = [wondelWoman(i) for i in range(units_per_player)]  # opponent team

# game loop
while True:
    for i in range(grid.size):
        grid.update(i , input())

    for i in range(units_per_player):
        unit_x, unit_y = [int(j) for j in input().split()]
        mteam[i].update(unit_x, unit_y, grid)

    for i in range(units_per_player):
        other_x, other_y = [int(j) for j in input().split()]
        oteam[i].update(unit_x, unit_y, grid)

    legal_actions = int(input())
    for i in range(legal_actions):  # valid command for my units
        atype, index, dir_1, dir_2 = input().split()
        mteam[int(index)].valid_commands.append((atype, index, dir_1, dir_2))

    for woman in mteam:
        print(woman.log, file=sys.stderr)

    # Write an action using print
    # get action for both and then evaluate which is better
    # also take into account how many possible moves are still available. if piece is cornered
    # it might make sense to let it out
    # push opponent only if I'm on 3 or can push opponent off to oblivion
    #  * for that it is needed a way to calculate number of valid moves
    for woman in mteam:
        act, attrs, opts = woman.action
        # action, action attributes (move level, build level), how many other options do I have left
        if not act:
            pass
        else:
            print("%s %s %s %s" % act)
        break

    # simulation / GA would be good choice for this bot. But probably not in python?
