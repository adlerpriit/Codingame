import sys
import math
import random
from operator import sub

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# N dimentional dungeon, where each floor (dimention) has it's own directions compared to references..
# tY - arbitary number -- something to do with aim of the game.. goal cooridnate?
# tX - similar to tY
# fN assume number of floors or dimensions. coordinates change in every dimension.
tY = int(input())
tX = int(input())
fN = int(input())


print(tY,tX,file=sys.stderr)

MAP = dict()

lastCoords = None
lastMove = None

moves = ['A','B','C','D','E']

op = {'A':'E','E':'A','C':'D','D':'C'}

coms = dict()

# game loop
while True:
    #cA-D are environment description
    cA = input() # command C moves here
    cB = input() # command A moves here
    cC = input() # command D moves here
    cD = input() # command E moves here
    env = [(cA,2),(cB,0),(cC,3),(cD,4)]
    # Command C,letA - west,
    # Command A,letB - north,
    # Command D,letC - east
    # Command E,letD - south,
    # currently command B is unknown. probably there is special character in environment description or it is enough to be in the correct spot and use to command to move to other floor?

    # here comes the dungeon coordinates
    coords = []
    for i in range(fN):
        coords.append([int(j) for j in input().split()])

    coordsMap = ":".join([str(i) for i in coords[-1]])
    # if lastCoords and lastMove:
    #     moveDiff = [list(map(sub,coords[i],lastCoords[i])) for i in range(len(coords))]
    #     moveDiffI = "-".join([":".join([str(i) for i in x]) for x in moveDiff])
    #     diff = sum([sum([abs(y) for y in x]) for x in moveDiff])
    #     print(diff,lastMove, moveDiff,file=sys.stderr)
    #     if lastMove not in coms:
    #         coms[lastMove] = {moveDiffI:1}
    #     else:
    #         if moveDiffI not in coms[lastMove]:
    #             coms[lastMove][moveDiffI] = 1
    #         else:
    #             coms[lastMove][moveDiffI] += 1
    #
    # [print(x,coms[x],file=sys.stderr) for x in coms]

    print(env,file=sys.stderr)
    print(coordsMap,file=sys.stderr)
    lastCoords = coords[-1]


    move = []
    for t,i in env:
        if t == '_':
            move.append(moves[i])
    print(move,file=sys.stderr)

    if coordsMap not in MAP:
        MAP[coordsMap] = {}
        for m in move:
            MAP[coordsMap][m] = 0

    if lastMove and lastCoords:
        MAP[coordsMap][op[lastMove]] += 1

    random.shuffle(move)
    print(MAP[coordsMap],file=sys.stderr)
    move = sorted(move, key=lambda d: MAP[coordsMap][d])
    
    move = move[0]
    MAP[coordsMap][move] += 1
    lastMove = move
    print(move)

# map is the layout of the entire dungeon
# in every level I need to remap the coordinates again somehow
# essentially start to move and figure out what changes

# so if letter yields a nomove we can map it to '#' character in input. there can be more than one '#'
# if coordinates do change we can attribute the letter to any '_'
# there should be 3 character, which I have not seen yet

#C {3: [[0, 0], [1, 0], [1, 0], [-1, 0], [0, 0]],
#   4: [[0, 0], [0, 1], [1, 0], [-1, 0], [0, -1]]}
#E {3: [[0, 0], [-1, 0], [1, 0], [-1, 0], [0, 0]],
 #  4: [[0, 0], [0, 1], [1, 0], [-1, 0], [-1, 0]]}