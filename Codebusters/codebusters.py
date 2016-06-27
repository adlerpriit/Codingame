import sys
import math
import random

# Send your busters out into the fog to trap ghosts and bring them home!

pcount = int(input())  # the amount of busters you control
gcount = int(input())  # the amount of ghosts on the map
my_tid = int(input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right
base = [0,0] if my_tid == 0 else [16000, 9000]

def getDist(pos_a,pos_b):
    return(math.sqrt(abs(pos_a[0]-pos_b[0])**2 + abs(pos_a[1]-pos_b[1])**2))

def getGostTarget(gost,bid):
    for gid in gost:
        if gost[gid]['t'] == bid:
            return(gid)
    return(-1)

def getOppoTarget(oppo,bid):
    for oid in oppo:
        if oppo[oid]['t'] == bid:
            return(oid)
    return(-1)

def reduceStun(stun):
    for i in list(stun):
        if stun[i] == 0:
            del(stun[i])
        else:
            stun[i] -= 1

#waypoinst to go through
poi = dict()
#stun conter
stun = dict()

# game loop
while True:
    #cound down stun counter
    reduceStun(stun)
    #my busters
    bust = dict()
    #visible ghosts
    gost = dict()
    #opponent busters
    oppo = dict()
    entities = int(input())  # the number of busters and ghosts visible to you
    for i in range(entities):
        # entity_id: buster id or ghost id
        # y: position of this buster / ghost
        # entity_type: the team id if it is a buster, -1 if it is a ghost.
        # state: For busters: 0=idle, 1=carrying a ghost.
        # value: For busters: Ghost id being carried. For ghosts: number of busters attempting to trap this ghost.
        eid, x, y, etype, state, value = [int(j) for j in input().split()]
        if etype == my_tid:
            bust[eid] = dict(pos=[x,y],s=state,v=value)
        elif etype == -1:
            gost[eid] = dict(pos=[x,y],s=state,v=value,t=-1)
        else:
            oppo[eid] = dict(pos=[x,y],s=state,v=value,t=-1)
    for gid in gost:
        #assign closest buster for each gost
        gost[gid]['d'] = math.sqrt(16001**2 + 9001**2)
        for bid in bust:
            dist_from_gost = getDist(gost[gid]['pos'],bust[bid]['pos'])
            if dist_from_gost < gost[gid]['d'] and bust[bid]['s'] == 0:
                gost[gid]['d'] = dist_from_gost
                gost[gid]['t'] = bid
    for oid in oppo:
        #assign closest buster for each gost
        oppo[oid]['d'] = math.sqrt(16001**2 + 9001**2)
        for bid in bust:
            dist_from_oppo = getDist(oppo[oid]['pos'],bust[bid]['pos'])
            if dist_from_oppo < oppo[oid]['d'] and bust[bid]['s'] == 0:
                oppo[oid]['d'] = dist_from_oppo
                oppo[oid]['t'] = bid
    for bid in sorted(bust):
        if bust[bid]['s'] == 1:
            #buster is carrieng a ghost and needs to delived it to base
            dist_from_base = getDist(bust[bid]['pos'],base)
            #print(dist_from_base,file=sys.stderr)
            if dist_from_base < 1600:
                print("RELEASE")
            else:
                print("MOVE " + " ".join([str(x) for x in base]))
        else:
            gid = getGostTarget(gost,bid)
            if gid in gost:
                if gost[gid]['d'] < 1760:
                    print("BUST " + str(gid))
                else:
                    print("MOVE " + " ".join([str(x) for x in gost[gid]['pos']]))
            else:
                oid = getOppoTarget(oppo,bid)
                if oid in oppo and oppo[oid]['s'] != 2 and bid not in stun:
                    if oppo[oid]['d'] < 1760:
                        print("STUN " + str(oid))
                        stun[bid] = 20
                    else:
                        print("MOVE " + " ".join([str(x) for x in oppo[oid]['pos']]))
                else:
                    #not carrieng a gost not running toward one, find random target to go
                    if bid not in poi or getDist(bust[bid]['pos'],poi[bid]) < 150:
                        poi[bid] = [random.randint(0,16000),random.randint(0,9000)]
                    print("MOVE " + " ".join([str(x) for x in poi[bid]]))
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # MOVE x y | BUST id | RELEASE
        #print("MOVE 8000 4500")
