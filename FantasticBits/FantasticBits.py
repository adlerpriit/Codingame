import sys
import math
import random
import re
from timeit import default_timer as timer

my_team_id = int(input())  # if 0 you need to score on the right of the map, if 1 you need to score on the left

opGoalX = 0 if my_team_id == 1 else 16000
myGoalX = 300 if my_team_id == 0 else 15700
myMagic = [0]
myTurn = 0
PETR = {}

def angleDest(ref,angle):
    x,y = ref
    delta = 1200
    x = x + int(math.cos(math.radians(angle)) * delta)
    y = y + int(math.sin(math.radians(angle)) * delta)
    return [x, y]

def aimTarget(pos,sv,target):
    dist_a = getDist(pos,target)
    point_a = getDest(pos,sv,dist_a)
    dist_b = getDist(point_a,target)
    point_b = getDest(point_a,target,1.1*dist_b)
    return point_b

def getAngleDest(pos_a,ref,alpha):
    opt_a = angleDest(pos_a,alpha+75)
    opt_b = angleDest(pos_a,alpha-75)
    if getDist(opt_a,ref) > getDist(opt_b,ref):
        return(opt_a)
    else:
        return(opt_b)

def getDist(pos_a,pos_b):
    return round(math.sqrt(abs(pos_a[0] - pos_b[0]) ** 2 + abs(pos_a[1] - pos_b[1]) ** 2), 4)

def getDest(pos_a,pos_b,d):
    d_ab = getDist(pos_a,pos_b)
    if d_ab == 0:
        return(pos_a)
    x = int(pos_a[0] - d * (pos_a[0]-pos_b[0])/d_ab)
    y = int(pos_a[1] - d * (pos_a[1]-pos_b[1])/d_ab)
    print(pos_a,pos_b,d,[x,y],file=sys.stderr)
    # if x < 0:
    #     Y = pos_a[1] - (pos_a[1]-y) * pos_a[0]/(pos_a[0]-x)
    #     x,y = getDest(pos_a,pos_b,getDist(pos_a,[0,Y]))
    # if x > 16000:
    #     Y = pos_a[1] - (pos_a[1]-y) * (16000-pos_a[0])/(x-pos_a[0])
    #     x,y = getDest(pos_a,pos_b,getDist(pos_a,[16000,Y]))
    # if y < 0:
    #     X = pos_a[0] - (pos_a[0]-x) * pos_a[1]/(pos_a[1]-y)
    #     x,y = getDest(pos_a,pos_b,getDist(pos_a,[X,0]))
    # if y > 7500:
    #     X = pos_a[0] - (pos_a[0]-x) * (7500-pos_a[1])/(y-pos_a[1])
    #     x,y = getDest(pos_a,pos_b,getDist(pos_a,[X,7500]))
    return([x,y])

def getDestPounce(pos_a,pos_b,d):
    d_ab = getDist(pos_a,pos_b)
    if d_ab == 0:
        return(pos_a)
    x = int(pos_a[0] - d * (pos_a[0]-pos_b[0])/d_ab)
    y = int(pos_a[1] - d * (pos_a[1]-pos_b[1])/d_ab)
    print("P",x,y,d,file=sys.stderr)
    if x < 0:
        Y = pos_a[1] - (pos_a[1]-y) * pos_a[0]/(pos_a[0]-x)
        x,y = getDest(pos_a,pos_b,getDist(pos_a,[0,Y]))
    if x > 16000:
        Y = pos_a[1] - (pos_a[1]-y) * (16000-pos_a[0])/(x-pos_a[0])
        x,y = getDest(pos_a,pos_b,getDist(pos_a,[16000,Y]))
    if y < 75:
        X = pos_a[0] - (pos_a[0]-x) * (pos_a[1]-75)/(pos_a[1]-y)
        x,y = getDestPounce([X,75],[x,75 - (y-75)],d-getDist(pos_a,[X,75]))
    if y > 7425:
        X = pos_a[0] - (pos_a[0]-x) * (7425-pos_a[1])/(y-pos_a[1])
        x,y = getDestPounce([X,7425],[x,7425 - (y-7425)],d-getDist(pos_a,[X,7425]))
    return([x,y])


def getAngleAbs(pos,target):
    alpha = math.degrees(math.atan2(target[1]-pos[1],target[0]-pos[0]))
    return(alpha)

def deltaAngle(alpha,beta):
    phi = abs(beta - alpha) % 360
    return(phi if phi < 180 else 360 - phi)

def getOutput(wid,mteam,oteam,snaff,bludg,defend):
    W = mteam[wid]
    owid = sorted(mteam)
    owid = owid[1] if owid[0] == wid else owid[0]
    W['n'] = [W['p'][i] + W['sv'][i] for i in range(2)]
    if abs(W['p'][0] - opGoalX) < 10000:
        Y = W['n'][1] if (2600 < W['n'][1] < 4900) else (2600 if W['n'][1] < 2600 else 4900)
        T = [opGoalX,Y]
    else:
        myDa = getDist(W['p'],[abs(opGoalX - 10000),500])
        myDb = getDist(W['p'],[abs(opGoalX - 10000),7000])
        if myDa < myDb:
            T = [abs(opGoalX - W['p'][0] - 2000),500]
        else:
            T = [abs(opGoalX - W['p'][0] - 2000),7000]
    T = [T[i]-W['sv'][i] for i in range(2)]
    if W['S'] == 1:
        for bid in bludg:
            m2o = getDist(bludg[bid]['n'],W['n'])
            m2oD = getDest(W['n'],T,m2o)
            if getDist(bludg[bid]['n'],m2oD) < 601:
                T = getAngleDest(bludg[bid]['n'],bludg[bid]['n'],getAngleAbs(bludg[bid]['n'],W['n']))
                T = [T[i]-W['sv'][i] for i in range(2)]
                #T[1]-=W['sv'][1]
        for oid in oteam:
            m2o = getDist(oteam[oid]['n'],W['n'])
            m2oD = getDest(W['n'],T,m2o)
            if getDist(oteam[oid]['n'],m2oD) < 601:
                T = getAngleDest(oteam[oid]['n'],oteam[oid]['n'],getAngleAbs(oteam[oid]['n'],W['n']))
                T = [T[i]-W['sv'][i] for i in range(2)]
        return("THROW " + " ".join([str(s) for s in T]) + " 500")
    Dx = {}
    #DX = {}
    Dm = {}
    De = {}
    for sid in snaff:
        #DX[sid] = getDist([opGoalX,3750],snaff[sid]['n'])
        Dx[sid] = getDist([myGoalX,3750],snaff[sid]['n'])
        Dm[sid] = getDist(W['n'],snaff[sid]['n'])
        for oid in oteam:
            dist = getDist(oteam[oid]['n'],snaff[sid]['n'])
            if (sid in De and De[sid] > dist) or sid not in De:
                De[sid] = dist
    if myMagic[0] > 10:
        for sid in sorted(Dx,key=Dx.get):
            sD = getDest(snaff[sid]['p'],snaff[sid]['n'],getDist(snaff[sid]['p'],snaff[sid]['n'])*3)
            if (((sD[0] < 2 and my_team_id == 0) or (sD[0] > 15998 and my_team_id == 1)) and
                (2100 < sD[1] < 5400) and
                sid not in PETR and
                snaff[sid]['p']!=mteam[owid]['p']):
                myMagic[0] -= 10
                #del snaff[sid]
                PETR[sid] = myTurn
                return("PETRIFICUS " + sid)
            m2sD = getDist(snaff[sid]['p'], W['p'])
            m2sDA = deltaAngle(getAngleAbs(W['p'],W['n']),getAngleAbs(W['p'],snaff[sid]['n']))
            msv = getDist(W['p'], W['n'])
            for oid in oteam:
                o2sD = getDist(snaff[sid]['p'],oteam[oid]['p'])
                o2sDn = getDist(snaff[sid]['n'],oteam[oid]['n'])
                osv = getDist(oteam[oid]['p'],oteam[oid]['n'])
                if o2sD > 400 and o2sDn < 400 and osv > 110 and sid not in PETR and ((m2sDA < 60 and m2sD / msv < 6) or getDist([myGoalX,3750],snaff[sid]['p']) < 3000):
                    myMagic[0] -= 10
                    PETR[sid] = myTurn
                    return("PETRIFICUS " + sid)

    if myMagic[0] > 20:
        #need to better calculate flippendo path. and angles.. need to use sides to bypass opponents (also use that for aiming throws)
        for sid in sorted(Dm,key=Dm.get):
            # get new speed vector for snaff
            m2sA = getAngleAbs(W['n'],snaff[sid]['n'])
            Fspeed = min(6000/(Dm[sid]/1000)**2,1000)
            vx,vy = snaff[sid]['sv']
            vx = snaff[sid]['n'][0] + round(vx*0.75 + math.cos(math.radians(m2sA)) * Fspeed*0.75,0)
            vy = snaff[sid]['n'][1] + round(vy*0.75 + math.sin(math.radians(m2sA)) * Fspeed*0.75,0)
            print(wid,sid,[vx,vy],end=" ",file=sys.stderr)
            sD = getDestPounce(snaff[sid]['p'],[vx,vy],(Fspeed+getDist([0,0],snaff[sid]['sv']))*14)
            m2s = getDist(W['n'],snaff[sid]['n'])
            A = deltaAngle(getAngleAbs(W['n'],T),m2sA)
            print(wid,sid,"Aim A:",A,"T:",sD,abs(W['n'][0]-opGoalX),m2s,file=sys.stderr)
            if (m2s < 3500 and
                A < 85 and
                abs(opGoalX-sD[0] < 3) and
                abs(W['n'][0]-opGoalX) > 3000 and
                (2300 < sD[1] < 5200)):
                myMagic[0] -= 20
                return("FLIPENDO " + sid)
        for sid in sorted(Dx,key=Dx.get):
            #make sure there is no opponent between you and snaff, calculate that snaff vector would not end up in opp grasp
            m2s = getDist(W['n'],snaff[sid]['n'])
            if getDist([myGoalX,3750],W['n']) > Dx[sid] + 2500 and m2s < 4000 and snaff[sid]['sv'][0] < 750:
                myMagic[0] -= 20
                return("ACCIO " + sid)
    # if myMagic[0] > 5:
    #     for bid in bludg:
    #         B = bludg[bid]
    #         m2bD = getDist(B['p'],W['p'])
    #         m2bDest = getDest(B['p'],B['n'],m2bD)
    #         if getDist(m2bDest,W['p']) < 400 and m2bD < 3*getDist([0,0],B['sv']):
    #             print("BLUDGER",m2bDest,m2bD,file=sys.stderr)
    #             myMagic[0] -= 5
    #             return("OBLIVIATE " + bid)
    Thrust = "150"
    Dord = sorted(Dm,key=lambda k:Dm[k])
    if defend:
        Dord = sorted(Dx,key=lambda k:Dm[k]*2+Dx[k]+De[k])
    for sid in Dord:
        T = getDest(T,snaff[sid]['n'],getDist(snaff[sid]['n'],T) + getDist(W['n'],snaff[sid]['n'])/4)
        T = [int(i) for i in aimTarget(W['p'],W['n'],T)]
        #A = deltaAngle(getAngleAbs(W['n'],T),getAngleAbs([0,0],W['sv']))
        # if A > 108:
        #     Thrust = str(150 - (int(A)-108))
        #print(A,file=sys.stderr)
        if len(Dm) > 1:
            del snaff[sid]
        return("MOVE " + " ".join([str(s) for s in T]) + " " + Thrust)
    return("MOVE " + str(myGoalX) + " " + str(3750+random.randint(-1500,1500)) + " 150")
# Grab Snaffles and try to throw them through the opponent's goal!
# Move towards a Snaffle and use your team id to determine where you need to throw it.


# game loop
while True:
    sTime = timer()
    myTurn += 1
    myMagic[0] += 1
    mteam = dict()
    oteam = dict()
    snaff = dict()
    bludg = dict()
    entities = int(input())  # number of entities still in game
    for i in range(entities):
        # entity_id: entity identifier
        # entity_type: "WIZARD", "OPPONENT_WIZARD" or "SNAFFLE" (or "BLUDGER" after first league)
        # x: position
        # y: position
        # vx: velocity
        # vy: velocity
        # state: 1 if the wizard is holding a Snaffle, 0 otherwise
        entity_ID,entity_type,x,y,vx,vy,state = input().split()
        print(entity_ID,entity_type,x,y,vx,vy,state,file=sys.stderr)
        entity_properties = [int(x) for x in [x,y,vx,vy,state]]
        if entity_type == 'WIZARD':
            mteam[entity_ID] = {'p':entity_properties[0:2],'sv':entity_properties[2:4],'S':entity_properties[4]}
        if entity_type == 'OPPONENT_WIZARD':
            oteam[entity_ID] = {'p': entity_properties[0:2], 'sv': entity_properties[2:4],'S': entity_properties[4]}
        if entity_type == 'SNAFFLE':
            snaff[entity_ID] = {'p':entity_properties[0:2],'sv':entity_properties[2:4]}
        if entity_type == 'BLUDGER':
            bludg[entity_ID] = {'p':entity_properties[0:2],'sv':entity_properties[2:4]}
    for sid in snaff:
        snaff[sid]['n'] = [snaff[sid]['p'][i] + snaff[sid]['sv'][i] for i in range(2)]
        #snaff[sid]['a'] = getAngleAbs([0,0],snaff[sid]['sv'])
    for oid in oteam:
        oteam[oid]['n'] = [oteam[oid]['p'][i] + oteam[oid]['sv'][i] for i in range(2)]
    for bid in bludg:
        bludg[bid]['n'] = [bludg[bid]['p'][i] + bludg[bid]['sv'][i] for i in range(2)]

    defend = 0

    for wid in sorted(mteam):

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
        command = getOutput(wid,mteam,oteam,snaff,bludg,defend)

        defend = 1
        # Edit this line to indicate the action for each wizard (0 ≤ thrust ≤ 150, 0 ≤ power ≤ 500)
        # i.e.: "MOVE x y thrust" or "THROW x y power"
        print(command)
        # if re.match("PETRIFICUS",command):
        #     com,sid = command.split()
        #     PETR[sid] = myTurn
    for sid in sorted(PETR):
        if myTurn - PETR[sid] > 1:
            del PETR[sid]
    print("Timing:", round(timer() - sTime, 5), file=sys.stderr)
