import sys
import math
import random

my_team_id = int(input())  # if 0 you need to score on the right of the map, if 1 you need to score on the left

opGoalX = 0 if my_team_id == 1 else 16000
myGoalX = 300 if my_team_id == 0 else 15700
myMagic = [0]

def angleDest(ref,angle):
    x,y = ref
    delta = 1000
    x = x + int(math.cos(math.radians(angle)) * delta)
    y = y + int(math.sin(math.radians(angle)) * delta)
    return([x,y])

def getAngleDest(pos_a,ref,alpha):
    opt_a = angleDest(pos_a,alpha+75)
    opt_b = angleDest(pos_a,alpha-75)
    if getDist(opt_a,ref) <= getDist(opt_b,ref):
        return(opt_a)
    else:
        return(opt_b)

def getDist(pos_a,pos_b):
    return(int(math.sqrt(abs(pos_a[0]-pos_b[0])**2 + abs(pos_a[1]-pos_b[1])**2)))

def getDest(pos_a,pos_b,dist):
    d_ab = getDist(pos_a,pos_b)
    if d_ab == 0:
        return(pos_a)
    x = pos_a[0] - dist * (pos_a[0]-pos_b[0])/d_ab
    y = pos_a[1] - dist * (pos_a[1]-pos_b[1])/d_ab
    return([x,y])

def getAngleAbs(pos,target):
    alpha = math.degrees(math.atan2(target[1]-pos[1],target[0]-pos[0]))
    if alpha < 0:
        alpha += 360
    return(alpha)

def deltaAngle(alpha,beta):
    phi = abs(beta - alpha) % 360
    return(phi if phi < 180 else 360 - phi)

def getOutput(wid,mteam,oteam,snaff,bludg,defend):
    W = mteam[wid]
    T = [opGoalX,3750+random.randint(-750,750)]
    if W['S'] == 1:
        for oid in oteam:
            m2oA = deltaAngle(getAngleAbs(W['n'],oteam[oid]['n']),getAngleAbs(W['n'],T))
            m2o = getDist(oteam[oid]['n'],W['n'])
            if m2oA < 12.5 and m2o < 3500:
                T = getAngleDest(W['n'],T,getAngleAbs(W['n'],oteam[oid]['n']))
        for bid in bludg:
            m2bA = deltaAngle(getAngleAbs(W['n'],bludg[bid]['n']),getAngleAbs(W['n'],T))
            m2b = getDist(bludg[bid]['n'],W['n'])
            if m2bA < 12.5 and m2b < 5000:
                T = getAngleDest(W['n'],T,getAngleAbs(W['n'],bludg[bid]['n']))
        return("THROW " + " ".join([str(s) for s in T]) + " 500")
    Dx = {}
    Dm = {}
    for sid in snaff:
        Dx[sid] = getDist([myGoalX,3750],snaff[sid]['n'])
        Dm[sid] = getDist(W['n'],snaff[sid]['n'])
    if myMagic[0] > 10:
        for sid in sorted(Dx,key=Dx.get):
            sD = getDest(snaff[sid]['p'],snaff[sid]['n'],getDist(snaff[sid]['p'],snaff[sid]['n'])*3)
            if (((sD[0] < 0 and my_team_id == 0) or (sD[0] > 16000 and my_team_id == 1)) and
                (sD[1] > 2100 and sD[1] < 5400)):
                myMagic[0] -= 10
                del snaff[sid]
                return("PETRIFICUS " + sid)
    if myMagic[0] > 20:
        for sid in sorted(Dm,key=Dm.get):
            m2s = getDist(W['n'],snaff[sid]['n'])
            A = deltaAngle(getAngleAbs(W['n'],T),getAngleAbs(W['n'],snaff[sid]['n']))
            print("Aim A:",A,abs(W['n'][0]-opGoalX),m2s,file=sys.stderr)
            if m2s < 3000 and A < 5 and abs(W['n'][0]-opGoalX) > 3000:
                myMagic[0] -= 20
                return("FLIPENDO " + sid)
        for sid in sorted(Dx,key=Dx.get):
            m2s = getDist(W['n'],snaff[sid]['n'])
            if getDist([myGoalX,3750],W['n']) > Dx[sid] + 2000 and m2s < 4000 and snaff[sid]['sv'][0] < 1000:
                myMagic[0] -= 20
                return("ACCIO " + sid)
    Thrust = "150"
    DmP = {}
    TO = sorted(Dm,key=Dm.get)
    if defend:
        TO = sorted(Dx,key=lambda k:Dx[k]+Dm[k])
        mids = sorted(mteam)
        mid = mids[0] if mids[0] != wid else mids[1]
        for sid in snaff:
            DmP[sid] = getDist(mteam[mid]['n'],snaff[sid]['n'])
        DmP = sorted(DmP,key=DmP.get)
    for sid in TO:
        if defend and len(TO) > 1 and sid == DmP[0]:
            continue
        T = snaff[sid]['n']
        A = deltaAngle(getAngleAbs(W['n'],T),getAngleAbs([0,0],W['sv']))
        if A > 108:
            Thrust = str(150 - (int(A)-108))
        #print(A,file=sys.stderr)
        #if len(Dm) > 1:
        #    del snaff[sid]
        return("MOVE " + " ".join([str(s) for s in T]) + " " + Thrust)
    return("MOVE " + str(myGoalX) + " " + str(3750+random.randint(-1500,1500)) + " 150")
# Grab Snaffles and try to throw them through the opponent's goal!
# Move towards a Snaffle and use your team id to determine where you need to throw it.


# game loop
while True:
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
        if entity_type == 'GLUDGER':
            bludg[entity_ID] = {'p':entity_properties[0:2],'sv':entity_properties[2:4]}
    for mid in mteam:
        mteam[mid]['n'] = [mteam[mid]['p'][i] + mteam[mid]['sv'][i] for i in range(2)]
    for sid in snaff:
        snaff[sid]['n'] = [snaff[sid]['p'][i] + snaff[sid]['sv'][i] for i in range(2)]
    for oid in oteam:
        oteam[oid]['n'] = [oteam[oid]['p'][i] + oteam[oid]['sv'][i] for i in range(2)]

    defend = 1

    for wid in sorted(mteam):

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
        command = getOutput(wid,mteam,oteam,snaff,bludg,defend)

        defend = 0
        # Edit this line to indicate the action for each wizard (0 ≤ thrust ≤ 150, 0 ≤ power ≤ 500)
        # i.e.: "MOVE x y thrust" or "THROW x y power"
        print(command)
