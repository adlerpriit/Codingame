import sys
import math

# Save humans, destroy zombies!
# 63,610

def dist(a,b):
    i,j = a
    k,l = b
    return( round(math.sqrt((i - k)**2 + (j - l)**2),3) )

def dest(pos_a,pos_b,d):
    d_ab = dist(pos_a,pos_b)
    if d_ab == 0:
        return(pos_a)
    x = int(pos_a[0] - d * (pos_a[0]-pos_b[0])/d_ab)
    y = int(pos_a[1] - d * (pos_a[1]-pos_b[1])/d_ab)
    #print([x,y],file=sys.stderr)
    if x < 0:
        Y = pos_a[1] - (pos_a[1]-y) * pos_a[0]/(pos_a[0]-x)
        x,y = dest(pos_a,pos_b,dist(pos_a,[0,Y]))
    if x > 16000:
        Y = pos_a[1] - (pos_a[1]-y) * (16000-pos_a[0])/(x-pos_a[0])
        x,y = dest(pos_a,pos_b,dist(pos_a,[16000,Y]))
    if y < 0:
        X = pos_a[0] - (pos_a[0]-x) * pos_a[1]/(pos_a[1]-y)
        x,y = dest(pos_a,pos_b,dist(pos_a,[X,0]))
    if y > 9000:
        X = pos_a[0] - (pos_a[0]-x) * (9000-pos_a[1])/(y-pos_a[1])
        x,y = dest(pos_a,pos_b,dist(pos_a,[X,9000]))
    return([x,y])

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

def z2hdist(hs,zs,pos):
    htoz = dict()
    ztoh = dict()
    for zid in zs:
        m2zd = dist(pos,zs[zid]['next_pos'])
        ztoh[zid] = {'h':-1,'d':m2zd}
        for hid in hs:
            z2hd = dist(hs[hid],zs[zid]['next_pos'])
            m2hd = dist(pos,hs[hid])
            safe = math.ceil(z2hd/400) - math.ceil(m2hd/1000) + 3
            if (hid not in htoz or htoz[hid]['s'] > safe) and m2zd > z2hd and safe >= 0:
                htoz[hid] = {'s':safe,'z':zid,'mz':m2zd,'mh':m2hd,'zh':z2hd}
                ztoh[zid] = {'h':hid,'d':z2hd}
    return(htoz,ztoh)

def m2zdist(pos,zs):
    mtoz = dict()
    for zid in zs:
        m2zd = dist(pos,zs[zid]['next_pos'])
        m2za = angle(pos,zs[zid]['next_pos'])
        mtoz[zid] = {'d':m2zd,'a':m2za}
    return(mtoz)

def getMySafeDest(me,ref,zs,zID,margin,depth):
    if depth > len(zs):
        return(avz(zs,zID))
    for zid in zs:
        if dist(me,zs[zid]['next_pos']) < margin:
            myD = dest(zs[zid]['next_pos'],me, 2040)
            if dist(ref,myD) > 1000:
                myD = dest(ref,myD,1000)
            return(getMySafeDest(myD,ref,zs,zID,margin,depth+1))
    return(me)

def avz(zs,zID):
    X=Y=0
    for zid in zID:
       X+=zs[zid]['next_pos'][0]
       Y+=zs[zid]['next_pos'][1]
    X/=len(zID)
    Y/=len(zID)
    return(int(X),int(Y))

def parseInput():
    rData = dict()
    rData['hs'] = dict()
    rData['zs'] = dict()
    rData['me'] = [int(i) for i in input().split()]
    human_count = int(input())
    for i in range(human_count):
        human_id, human_x, human_y = [int(j) for j in input().split()]
        rData['hs'][human_id] = [human_x, human_y]
    zombie_count = int(input())
    for i in range(zombie_count):
        zombie_id, zombie_x, zombie_y, zombie_xnext, zombie_ynext = [int(j) for j in input().split()]
        rData['zs'][zombie_id] = {'pos':[zombie_x,zombie_y],'next_pos':[zombie_xnext,zombie_ynext]}
    return(rData)

def botResponse(rData):
    me = rData['me']
    hs = rData['hs']
    zs = rData['zs']
    # for zid in sorted(zs):
    #     print(zid,zs[zid]['pos'],zs[zid]['next_pos'],file=sys.stderr)
    tX,tY = me
    i = 0
    htoz,ztoh = z2hdist(hs,zs,me)
    hID = sorted(htoz, key=lambda h: htoz[h]['s']*rData['s'] + htoz[h]['mz']*rData['mz'] + htoz[h]['zh']*rData['zh'])
    mtoz = m2zdist(me,zs)
    zID = sorted(ztoh, key=lambda z: ztoh[z]['d'])
    #print(htoz,file=sys.stderr)
    #print(mtoz,file=sys.stderr)
    #print(hID[i],htoz[hID[i]],file=sys.stderr)
    #while htoz[hID[0]]['s'] < 0:
    #    hID.pop(0)
    if hID:
        while htoz[hID[i]]['s'] < 10:
            print(hID[i],htoz[hID[i]],file=sys.stderr)
            i+=1
            if i == len(hID):
                break
        myD = dest(zs[htoz[hID[0]]['z']]['next_pos'],me,1999)
        if dist(zs[htoz[hID[0]]['z']]['next_pos'],me) <= 2998:
            zC = 0
            for d in range(1998,1000,-99):
                tX,tY = dest(zs[htoz[hID[0]]['z']]['next_pos'],me,d)
                ztC = 0
                for zid in zs:
                    if dist([tX,tY],zs[zid]['next_pos']) <= 2000:
                        ztC += 1
                if ztC > zC:
                    zC = ztC
                    myD = [tX,tY]
                if zC == len(zs):
                    break
    else:
        myD = dest(me,avz(zs,zID),1000)
        myD = getMySafeDest(myD,me,zs,zID,2000,0)
    # Your destination coordinates
    return(" ".join([str(s) for s in myD]))


# game loop
while 1:
    rData = parseInput()
    rData['s'] = 1
    rData['mz'] = 1
    rData['zh'] = 3
    AgentOutput = botResponse(rData)
    print(AgentOutput)
