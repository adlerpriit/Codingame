import sys
import math
import copy

def dist(a,b):
    i,j = a
    k,l = b
    return( int(math.sqrt((i - k)**2 + (j - l)**2)) )

def dest(pos_a,pos_b,d):
    d_ab = dist(pos_a,pos_b)
    if d_ab == 0:
        return(pos_a)
    x = int(pos_a[0] - d * (pos_a[0]-pos_b[0])/d_ab)
    y = int(pos_a[1] - d * (pos_a[1]-pos_b[1])/d_ab)
    if x < 0:
        x,y = 0, (y - x if pos_a[1] < y else y + x)
    if x > 16000:
        x,y = 16000, (y - (16000 - x) if pos_a[1] < y else y + (16000 - x))
    if y < 0:
        x,y = (x - y if pos_a[0] < x else x + y),0
    if y > 9000:
        x,y = (x - (9000 - y) if pos_a[0] < x else x + (9000 - y)),9000
    return([x,y])

def getDamDist(d):
    d -= 0.4999
    return( int(pow(125000 / d, 1/1.2)) )

def getDam(dist):
    return( round(125000 / pow(dist,1.2)) )

def angle(a,b):
    i,j = a
    k,l = b
    alpha = math.degrees(math.atan2(l-j,k-i))
    if alpha < 0:
        alpha += 360
    return(alpha)

def deltaAngle(alpha,beta):
    phi = abs(beta - alpha) % 360
    sign = 1 if ((alpha - beta >= 0 and alpha - beta <= 180) or (alpha - beta <= -180 and alpha - beta >= -360)) else -1
    return(sign * (phi if phi < 180 else 360 - phi))

def getNextDP(data,pos):
    mD = 18358
    mID = None
    for dID in data:
        tD = dist(data[dID]['pos'],pos)
        if tD < mD:
            mD = tD
            mID = dID
    if mID in data:
        data[mID]['w'] += mD/500
    return(mID,mD)

def getMySafeDest(me,ref,oppo,data,margin):
    for oid in oppo:
        if dist(me,oppo[oid]['pos']) < margin:
            #opA2nD = angle(oppo[oid]['pos'],data[oppo[oid]['nD']]['pos'])
            #myD = getAngleDest(oppo[oid]['pos'],me,opA2nD)
            myD = dest(oppo[oid]['pos'],me, 2680)
            if dist(ref,myD) > 1001:
                myD = dest(ref,myD,1001)
            return(getMySafeDest(myD,ref,oppo,data,margin))
    return(me)

def angleDest(ref,angle):
    x,y = ref
    delta = 2680
    x = x + int(math.cos(math.radians(angle)) * delta)
    y = y + int(math.sin(math.radians(angle)) * delta)
    return([x,y])

def getAngleDest(pos_a,ref,alpha):
    opt_a = angleDest(pos_a,alpha+50)
    opt_b = angleDest(pos_a,alpha-50)
    if dist(opt_a,ref) <= dist(opt_b,ref):
        return(opt_a)
    else:
        return(opt_b)

def getIntercept(me,dat,DP,pos,N,Cost,T):
    #print([dist(me,pos),N],file=sys.stderr)
    mDist = dist(me,pos)
    if mDist < 2180 or N >= 120 / oppo_count or DP == None:
        return(N,Cost,T)
    else:
        opA2nD = angle(pos,dat[DP]['pos'])
        myD = getAngleDest(pos,me,opA2nD)
        if int(dist(me,myD)/1000) == N:
            T = myD
        tD = dist(dat[DP]['pos'],pos)
        tD = 500 if tD > 500 else tD
        nextPos = dest(pos,dat[DP]['pos'],tD)
        if tD < 500:
            del(dat[DP])
            Cost+=1
        nextDP, d2nextDP = getNextDP(dat,nextPos)
        return(getIntercept(me,dat,nextDP,nextPos,N+1,Cost,T))

# Shoot enemies before they collect all the incriminating data!
# The closer you are to an enemy, the more damage you do but don't get too close or you'll get killed.


# game loop
while True:
    data = dict()
    oppo = dict()
    me = [int(i) for i in input().split()]
    data_count = int(input())
    minDfromO = 18358
    for i in range(data_count):
        data_id, data_x, data_y = [int(j) for j in input().split()]
        data[data_id] = {'pos':[data_x,data_y],'d':dist(me,[data_x,data_y]),'w':0,'opd':[]}
    oppo_count = int(input())
    for i in range(oppo_count):
        oppo_id, oppo_x, oppo_y, oppo_life = [int(j) for j in input().split()]
        nextDP, d2nextDP = getNextDP(data,[oppo_x,oppo_y])
        d2nextPos = 500 if d2nextDP > 500 else d2nextDP
        
        nextPos = dest([oppo_x,oppo_y],data[nextDP]['pos'],d2nextPos)
        nextD = dist(me,nextPos)
        dCopy = copy.deepcopy(data)
        danger,cost,myD = getIntercept(me,dCopy,nextDP,nextPos,1,0,None)
        if nextD < minDfromO:
            minDfromO = nextD
        oppo[oppo_id] = {
            'pos':nextPos,
            'hp':oppo_life,
            'd':nextD,
            'nD':nextDP,
            'dd':(nextD - getDamDist(oppo_life))/1000,
            'dd2':(nextD - getDamDist(oppo_life/2 + 0.5))/1000,
            'dd3':(nextD - getDamDist(oppo_life/3 + 0.5))/1000,
            'tnD':d2nextDP/500,
            'danger':danger,
            'cost':round(15 - (cost/data_count) * 15,1),
            'myD':myD}
    
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    #print(oppo,file=sys.stderr)
    for oid in oppo:
        op = oppo[oid]
        op['dd'] = -1 if op['dd'] < -1 else op['dd']
        score = op['dd'] * 2.15 + op['cost'] + op['danger'] + op['tnD']
        op['sc'] = round(score,2)

    for oid in sorted(oppo,key=lambda oid: oppo[oid]['sc']):
        op = oppo[oid]
        print([oid,op['sc'],op['dd'],op['dd2'],op['dd3'],op['cost'],op['danger'],op['tnD']],file=sys.stderr)


    for oid in sorted(oppo,key=lambda oid: oppo[oid]['sc']):
        print([oid,oppo[oid], data[oppo[oid]['nD']]],file=sys.stderr)
        if minDfromO < 2000:
            myD = getMySafeDest(me,me,oppo,data,2000)
            print("MOVE " + " ".join([str(nr) for nr in myD]))
        elif  oppo[oid]['dd'] < 0:
            print("SHOOT " + str(oid))
        elif oppo[oid]['hp'] > 10 and getDam(oppo[oid]['d']) > 8:
            print("SHOOT " + str(oid))
        elif oppo[oid]['dd2'] < 0 and oppo[oid]['tnD'] - oppo[oid]['dd'] < 1 and data[oppo[oid]['nD']]['w'] == oppo[oid]['tnD']:
            print("SHOOT " + str(oid))
        elif oppo[oid]['dd3'] < 0 and oppo[oid]['tnD'] - oppo[oid]['dd2'] < 1 and data[oppo[oid]['nD']]['w'] == oppo[oid]['tnD']:
            print("SHOOT " + str(oid))
        else:
            opA2nD = angle(oppo[oid]['pos'],data[oppo[oid]['nD']]['pos'])
            #need to figure out my dest formula.. atm it's not so good.. also need to think a bit more about movement
            myD = oppo[oid]['myD'] or getAngleDest(oppo[oid]['pos'],me,opA2nD)
            if dist(me,myD) > 1001:
                myD = dest(me,myD,1001)
            myD = getMySafeDest(myD,me,oppo,data,2000)
            print("MOVE " + " ".join([str(nr) for nr in myD]))
        break
