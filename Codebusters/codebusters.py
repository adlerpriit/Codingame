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

def getClosest(pool,buster):
    dist_from = math.sqrt(16001**2 + 9001**2)
    rid = -1
    for myid in pool:
        dist_from_entity = getDist(pool[myid]['pos'],buster['pos'])
        if dist_from_entity < dist_from and buster['s'] != 1:
            dist_from = dist_from_entity
            rid = myid
    return(dict(d=dist_from,id=rid))

def gostAvail(gid,gost):
    #this is potential conflict that can just consume time, should try to stun instead
    if gost[gid]['s'] == 0 and gost[gid]['v'] > 0:
        return(0)
    else:
        return(1)

def reduceStun(stun):
    for i in list(stun):
        if stun[i] == 0:
            del(stun[i])
        else:
            stun[i] -= 1

def initPoi(poi):
    for x in range(16):
        for y in range(9):
            poi[" ".join([str(i) for i in [x,y]])] = [x*1000,y*1000]

#waypoinst to go through
poi = dict()
initPoi(poi)
#stun conter
stun = dict()
#my busters
bust = dict()

# game loop
while True:
    #cound down stun counter
    reduceStun(stun)
    #opponent busters
    oppo = dict()
    #visible ghosts
    gost = dict()
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
            gost[eid] = dict(pos=[x,y],s=state,v=value)
        else:
            oppo[eid] = dict(pos=[x,y],s=state,v=value)
    print(gost,file=sys.stderr)
    print(oppo,file=sys.stderr)
    for bid in sorted(bust):
        if bust[bid]['s'] == 1:
            if bust[bid]['v'] in gost:
                del(gost[bust[bid]['v']])
            #buster is carrieng a ghost and needs to delived it to base
            dist_from_base = getDist(bust[bid]['pos'],base)
            #print(dist_from_base,file=sys.stderr)
            if dist_from_base < 1600:
                print("RELEASE")
            else:
                print("MOVE " + " ".join([str(x) for x in base]) + " opt to base")
        else:
            gid = getClosest(gost,bust[bid])
            oid = getClosest(oppo,bust[bid])
            if gid['id'] in gost and gid['d'] > 900:
                if gid['d'] < 1705 and gostAvail(gid['id'],gost) == 1:
                    print("BUST " + str(gid['id']))
                else:
                    if oid['id'] in oppo and oppo[oid['id']]['s'] != 2 and bid not in stun:
                        if oid['d'] < 1760:
                            print("STUN " + str(oid['id']))
                            stun[bid] = 20
                        else:
                            print("MOVE " + " ".join([str(x) for x in oppo[oid['id']]['pos']]) + " opt toward oppo " + str(oid['id']))
                    else:
                        print("MOVE " + " ".join([str(x) for x in gost[gid['id']]['pos']]) + " opt toward gost " + str(gid['id']))
            else:
                if oid['id'] in oppo and oppo[oid['id']]['s'] != 2:
                    if oid['d'] < 1760 and bid not in stun:
                        print("STUN " + str(oid['id']))
                        stun[bid] = 20
                    else:
                        print("MOVE " + " ".join([str(x) for x in oppo[oid['id']]['pos']]) + " opt toward oppo " + str(oid['id']))
                else:
                    #not carrieng a gost not running toward one, find random target to go
                    #sort pois by distance
                    toPoi = math.sqrt(16001**2 + 9001**2)
                    tid = -1
                    for pid in list(poi):
                        dist_to_poi = getDist(bust[bid]['pos'],poi[pid])
                        if dist_to_poi < 1760:
                            del(poi[pid])
                        else:
                            if dist_to_poi < toPoi:
                                toPoi = dist_to_poi
                                tid = pid
                    if tid in poi:
                        print("MOVE " + " ".join([str(x) for x in poi[tid]]) + " opt toward poi " + str(tid))
                    else:
                        print("MOVE " + " ".join([str(x) for x in base]) + " opt to final base")
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # MOVE x y | BUST id | RELEASE
        #print("MOVE 8000 4500")
