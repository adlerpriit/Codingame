import sys
import math
import random

# Send your busters out into the fog to trap ghosts and bring them home!

pcount = int(input())  # the amount of busters you control
gcount = int(input())  # the amount of ghosts on the map
my_tid = int(input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right
base = [0,0] if my_tid == 0 else [16000,9000]
oase = [0,0] if my_tid == 1 else [16000,9000]

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

def getWeakest(goi,gost,buster):
    dist_from = math.sqrt(16001**2 + 9001**2)
    #sort based on status, then choose the closest one
    if buster['s'] == 3:
        rid = buster['v']
        dist = getDist(goi[rid]['pos'],buster['pos'])
        return(dict(d=dist,id=rid))
    slist = sorted(goi,key=lambda x: goi[x]['s'])
    if len(slist) == 0:
        return(dict(d=dist_from,id=-1))
    else:
        rid = slist.pop()
        state = goi[rid]['s']
        for gid in slist:
            dist_from_entity = getDist(goi[gid]['pos'],buster['pos'])
            if dist_from_entity < 900 and gid not in gost:
                del(goi[gid])
            else:
                if dist_from_entity < dist_from and buster['s'] != 1:
                    dist_from = dist_from_entity
                    rid = gid
                if state + 10 < goi[gid]['s']:
                    return(dict(d=dist_from,id=rid))
                state = goi[gid]['s']
        return(dict(d=dist_from,id=rid))

def reduceStun(stun):
    for i in list(stun):
        if stun[i] == 0:
            del(stun[i])
        else:
            stun[i] -= 1
    print(stun,file=sys.stderr)

def initPoi(poi):
    for x in range(8):
        for y in range(8):
            poi[" ".join([str(i) for i in [x,y]])] = [x*2000+1000,y*1000+1000]

#waypoinst to go through
poi = dict()
initPoi(poi)
#stun conter
stun = dict()
#my busters
bust = dict()
#my gosts of interest
goi = dict()

turnNR = 0
# game loop
while True:
    #cound down stun counter
    reduceStun(stun)
    #opponent busters
    oppo = dict()
    #visible ghosts
    gost = dict()
    #assigned poi
    apoi = dict()
    #escort service
    escort = []
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
            if state == 1:
                escort.append(eid)
        elif etype == -1:
            gost[eid] = dict(pos=[x,y],s=state,v=value)
            goi[eid] = dict(pos=[x,y],s=state,v=value)
        else:
            if state != 2:
                oppo[eid] = dict(pos=[x,y],s=state,v=value)
    for bid in sorted(bust):
        isStun = "W" + str(stun[bid]) if bid in stun else ""
        toPoi = math.sqrt(16001**2 + 9001**2)
        tid = -1
        for pid in list(poi):
            dist_to_poi = getDist(bust[bid]['pos'],poi[pid])
            if dist_to_poi < 1760:
                del(poi[pid])
            else:
                if dist_to_poi < toPoi and pid not in apoi:
                    toPoi = dist_to_poi
                    tid = pid
        apoi[tid] = bid
        #print(poi,file=sys.stderr)
        oid = getClosest(oppo,bust[bid])
        #if possible to stun, then stun. Seems that it could be priority
        if oid['id'] in oppo and bid not in stun and oid['id'] not in stun and oid['d'] <= 1760:
            print("STUN " + str(oid['id']))
            stun[bid] = 20
            stun[oid['id']] = 10
        else:
        #now if I have a ghost delived it to home
            if bust[bid]['s'] == 1:
                if bust[bid]['v'] in goi:
                    del(goi[bust[bid]['v']])
                if bust[bid]['v'] in gost:
                    del(gost[bust[bid]['v']])
                #buster is carrieng a ghost and needs to delived it to base
                dist_from_base = getDist(bust[bid]['pos'],base)
                if dist_from_base < 1600:
                    print("RELEASE")
                else:
                    print("MOVE " + " ".join([str(x) for x in base]) + " B")
            else:
                if len(escort) > 0 and bust[bid]['s'] == 6 and turnNR > 225:
                    tbid = escort.pop()
                    print("MOVE " + " ".join([str(x) for x in bust[tbid]['pos']]) + " SUP " + str(tbid) + " " + isStun)
                else:
                    #now we should try to follow opponent with a ghost
                    if oid['id'] in oppo and oppo[oid['id']]['s'] == 1 and oid['id'] not in stun and (bid not in stun or stun[bid] < getDist(oppo[oid['id']]['pos'],oase)/800):
                        if oid['d'] < 1760 and bid not in stun:
                            print("STUN " + str(oid['id']) + " S " + str(oid['id']))
                            stun[bid] = 20
                            goi[oppo[oid['id']]['v']] = dict(pos=oppo[oid['id']]['pos'],s=0,v=0)
                        else:
                            print("MOVE " + " ".join([str(x) for x in oppo[oid['id']]['pos']]) + " O " + str(oid['id']) + " " + isStun)
                    else:
                        gid = getWeakest(goi,gost,bust[bid])
                        gid['b'] = bid
                        if gid['id'] in goi:
                            gid['s'] = goi[gid['id']]['s']
                        print(gid,file=sys.stderr)
                        if tid in poi and (gid['id'] not in goi or gid['s'] > 10):
                            print("MOVE " + " ".join([str(x) for x in poi[tid]]) + " POI " + str(tid) + " " + isStun)
                        else:
                            if gid['id'] in goi and gid['d'] > 900:
                                if gid['d'] < 1705 and gid['id'] in gost:
                                    # and gostAvail(gid['id'],gost) == 1
                                    print("BUST " + str(gid['id']) + " B " + str(gid['id']) + " " + isStun)
                                else:
                                    print("MOVE " + " ".join([str(x) for x in goi[gid['id']]['pos']]) + " G " + str(gid['id']) + " " + isStun)
                            else:
                                print("MOVE " + " ".join([str(x) for x in base]) + " KILLED ME?" + " " + isStun)
    turnNR += 1
    print(goi,file=sys.stderr)
