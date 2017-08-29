import sys
import math
import random
from functools import lru_cache

DIRS = {'N':(-1,0), 'NE':(-1,1), 'E':(0,1), 'SE':(1,1),
        'S':(1,0), 'SW':(1,-1), 'W':(0,-1), 'NW':(-1,-1)}

class wondelWoman(object):


    def __init__(self, id):
        self.id = id
        self._grid = []
        self._pos = (-1, -1)

    def update(self, x, y, grid):
        """
        Update unit (wonam position and reset valid commands)
        """
        if x != -1 and y != -1:
            self._pos = (y, x)
        self._grid = grid  # reference to object, do not change

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, pos):
        self._pos = pos

    @property
    def log(self):
        return (self.id, self._pos)

class Grid(object):
    def __init__(self, size):
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

    @lru_cache(maxsize=None)
    def tile_value(self, pos, turn):
        if not pos:
            return -1
        y, x = pos
        if 0 < y < self._size and 0 < x < self._size:
            return self._grid[y][x]
        else:
            return -1

    @lru_cache(maxsize=None)
    def tile_diff(self, pos, target, turn):
        """ Return difference between two tile values (always target - current)
        """
        return (self.tile_value(target, turn) -
                self.tile_value(pos, turn))

class Action(object):
    def __init__(self, act, pos, grid, turn):
        self._act = act
        self._pos = pos
        self._grid = grid
        self._turn = turn
        self._atype, self._wid, self._mdir, self._adir = act
        if self._atype == 'PUSH&BUILD':
            self._move = False
            self._push = tuple([a + b for (a,b) in zip(self._pos, DIRS[self._mdir])])
            self._build = self._push
            self._pushto = tuple([a + b for (a,b) in zip(self._push, DIRS[self._adir])])
        else:  # 'MOVE&BUILD'
            self._push = False
            self._move = tuple([a + b for (a,b) in zip(self._pos, DIRS[self._mdir])])
            self._build = tuple([a + b for (a,b) in zip(self._move, DIRS[self._adir])])

    def score(self, mteam=None, oteam=None):
        # print(self._move, self._build, self._pos, file=sys.stderr)
        # for woman in mteam + oteam:
        #     if ((self._move and woman.position == self._build) or
        #         (self._push and woman.position == self._pushto)):
        #         return -10
        #scoring schema
        self._score = 0
        # I get point 3pt
        # I move up (< 3) 2pt
        # I move on same level 1pt
        # I move down 0pt
        self._score += self._grid.tile_value(self._build, self._turn)
        if self._grid.tile_value(self._build, self._turn) == 3:
            self._score -= 6

        if self._move:
            self._score += self._grid.tile_diff(self._pos, self._move, self._turn)
            self._score += self._grid.tile_value(self._move, self._turn)
            if self._grid.tile_value(self._move, self._turn) == 3:
                self._score += 3
            self._score += self._exits(self._move) / 2
        else:
            if self._grid.tile_diff(self._push, self._pushto, self._turn) < -1:
                self._score += 6
            self._score -= self._grid.tile_diff(self._push, self._pushto, self._turn) * 3
            # self._score += (self._exits(self._push) - self._exits(self._pushto))
        # Push opponent off from 2/3 to 0 4pt
        #  * Difference needs to be 2, so opponent can't move back easily
        # Pushed oppeonent does not have moving options 10pt
        #  Block opponent building/moving capacity by moving 2pt
        #  Block opponent building/moving capacity by building 3pt
        #    * should be connected by number of remaining moves by opponent
        # Try to avoid places oppoenent can push you off (visible opponents, last known position)
        return self._score

    def update(self, oteam):
        if self._push:
            for woman in oteam:
                if woman.position == self._push:
                    woman.position = self._pushto

    def _exits(self, pos):
        # calculates number of valid exists for position
        tile_val = self._grid.tile_value(pos, self._turn)
        exits = 0
        for exit in DIRS:
            exit_val = self._grid.tile_value(tuple([a + b for (a,b) in zip(pos, DIRS[exit])]), self._turn)
            if 0 <= exit_val <= 3 and exit_val - tile_val <= 1:
                exits += 1
        return exits

    def __str__(self):
        return "%s %s %s %s" % self._act

grid = Grid(int(input()))  # size
units_per_player = int(input())  # units per player
mteam = [wondelWoman(i) for i in range(units_per_player)]  # my team
oteam = [wondelWoman(i) for i in range(units_per_player)]  # opponent team
turn = 0
# game loop
while True:
    for i in range(grid.size):
        grid.update(i , input())

    for i in range(units_per_player):
        unit_x, unit_y = [int(j) for j in input().split()]
        mteam[i].update(unit_x, unit_y, grid)

    for i in range(units_per_player):
        # some of them should be invisible? coords -1, -1? then don't update?
        other_x, other_y = [int(j) for j in input().split()]
        oteam[i].update(other_x, other_y, grid)
        print("OPPONENTs", oteam[i].log, (other_y, other_x), file=sys.stderr)

    legal_actions = int(input())
    valid_commands = []
    for i in range(legal_actions):  # valid command for my units
        atype, index, dir_1, dir_2 = input().split()
        valid_commands.append(Action((atype, index, dir_1, dir_2),
                                     mteam[int(index)].position, grid, turn))

    for woman in mteam:
        print(woman.log, file=sys.stderr)

    # Write an action using print
    # get action for both and then evaluate which is better
    # also take into account how many possible moves are still available. if piece is cornered
    # it might make sense to let it out
    # push opponent only if I'm on 3 or can push opponent off to oblivion
    #  * for that it is needed a way to calculate number of valid moves
    if valid_commands:
        current_act = valid_commands[0]
        current_sco = -99
        for act in valid_commands:
            score = act.score(mteam, oteam)
            # print(score, act, file=sys.stderr)
            if score > current_sco:
                current_act = act
                current_sco = score
        current_act.update(oteam)
        print("%s %d" % (current_act, current_sco))
    else:
        print("Seems that I have lost?")
    turn += 1
    # simulation / GA would be good choice for this bot. But probably not in python?
