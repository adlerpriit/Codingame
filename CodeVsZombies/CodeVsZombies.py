import sys
import math
import random

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

def angleDest(ref,angle):
    x,y = ref
    delta = 1000
    x = x + int(math.cos(math.radians(angle)) * delta)
    y = y + int(math.sin(math.radians(angle)) * delta)
    return([x,y])

def z2hdist(hs,zs,pos):
    htoz = dict()
    ztoh = dict()
    for zid in zs:
        ztoh[zid] = {'h':-1,'d':dist(pos,zs[zid]['next_pos'])}
    for hid in hs:
        m2hd = round(dist(pos,hs[hid])/1000-2,2)
        h2zC = 0
        for zid in zs:
            m2zd = round(dist(pos,zs[zid]['next_pos'])/1000-1,3)
            z2hd = round(dist(hs[hid],zs[zid]['next_pos'])/400,3)
            deltaZ2HD = round(dist(hs[hid],zs[zid]['pos']) - z2hd*400 - dist(zs[zid]['pos'],zs[zid]['next_pos']),2)
            safe = math.ceil(z2hd) - math.ceil(m2hd) + 1
            if deltaZ2HD > -1 and m2zd*1000+1000 > z2hd*400:
                h2zC+=1
                if zid in ztoh:
                    del(ztoh[zid])
            else:
                continue
            #print("Calc:",hid,":",{'s':safe,'z':zid,'mz':m2zd,'mh':m2hd,'zh':z2hd,'zD':deltaZ2HD},file=sys.stderr)
            if (hid not in htoz or htoz[hid]['s'] > safe):
                htoz[hid] = {'s':safe,'z':zid,'mz':m2zd,'mh':m2hd,'zh':z2hd,'zD':deltaZ2HD}
        if hid in htoz:
            htoz[hid]['c'] = h2zC
    return(htoz,ztoh)

def m2zdist(pos,zs):
    mtoz = dict()
    for zid in zs:
        m2zd = dist(pos,zs[zid]['next_pos'])
        m2za = angle(pos,zs[zid]['next_pos'])
        mtoz[zid] = {'d':m2zd,'a':m2za}
    return(mtoz)

def getMySafeDest(me,ref,zs,hs,zID,margin,depth):
    if depth > len(zs):
        return(False)
    for zid in zID:
        z2md = dist(zs[zid]['next_pos'],me)
        z2hd = 50000
        for hid in hs:
            td = dist(zs[zid]['next_pos'],hs[hid])
            z2hd = td if td < z2hd else z2hd
        if z2md < margin or z2hd < z2md:
            myD = dest(zs[zid]['next_pos'],me, 2040)
            if dist(ref,myD) > 1000:
                myD = dest(ref,myD,1000)
            return(getMySafeDest(myD,ref,zs,hs,zID,margin,depth+1))
    return(me)

def getOptDest(myD,me,zs,hs,zID):
    z2md = 0
    for zid in zs:
        td = dist(myD,zs[zid]['next_pos'])
        z2md = td if td > z2md else z2md
    if z2md > 2001:
        myD = getMySafeDest(myD,me,zs,hs,zID,2001,0)
    return(myD)

def avz(zs,zID):
    X=Y=0
    for zid in zID:
       X+=zs[zid]['next_pos'][0]
       Y+=zs[zid]['next_pos'][1]
    X/=len(zID)
    Y/=len(zID)
    return(int(X),int(Y))

def getIntercept(me,H,Z):
    zPos = Z['pos']
    mPos = me
    N = 1
    while dist(mPos,zPos) > 2000:
        mPos = dest(me,zPos,1000*N)
        zPos = dest(Z['pos'],H,400*N)
        N+=1
    return(mPos)

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

def getOrder(H,rData):
    return( H['mh']*rData['mh'] +
            H['mz']*rData['mz'] +
            H['zh']*rData['zh'] +
            H['c']*rData['c']
        )

def botResponse(rData):
    me = rData['me']
    hs = rData['hs']
    zs = rData['zs']
    htoz,ztoh = z2hdist(hs,zs,me)
    hID = sorted(htoz, key=lambda h: getOrder(htoz[h],rData))
    #mtoz = m2zdist(me,zs)
    zID = sorted(ztoh, key=lambda z: ztoh[z]['d'], reverse=True)
    while hID and htoz[hID[0]]['s'] < 0:
        hID.pop(0)
    print(hID,zID,file=sys.stderr)
    if hID and len(hID) > 0:
        #print(len(hID))
        # i = 0
        # while htoz[hID[i]]['s'] < 0:
        #     print(hID[i],htoz[hID[i]],file=sys.stderr)
        #     i+=1
        #     if i == len(hID):
        #         break
        myD = getIntercept(me,hs[hID[0]],zs[htoz[hID[0]]['z']])
        if dist(me,myD) > 1000:
            myD = dest(me,myD,1000)
            if zID and len(zID) > 0:
                mytD = getMySafeDest(myD,me,zs,hs,zID,2001,0)
                if mytD:
                    myD = mytD
                    return(" ".join([str(s) for s in myD]) + " :" + str(dist(me,myD)) + ":save+safe")
                else:
                    return(" ".join([str(s) for s in myD]) + " :" + str(dist(me,myD)) + ":save+fail")
            else:
                return(" ".join([str(s) for s in myD]) + " :" + str(dist(me,myD)) + ":save+cut")

        else:
            return(" ".join([str(s) for s in myD]) + " :" + str(dist(me,myD)) + ":save+close")
    elif zID and len(zID) > 0:
        #print("zID:",zID,file=sys.stderr)
        angleArray = [a for a in range(90)]
        random.shuffle(angleArray)
        myD = avz(zs,zID)
        myD = dest(me,myD,1000) if dist(me,myD) > 1000 else myD
        myD = getOptDest(myD,me,zs,hs,zID)
        while not myD and angleArray:
            myD = dest(me,angleDest(me,angleArray.pop()*4),900)
            myD = getOptDest(myD,me,zs,hs,zID)
        if not myD:
            myD = avz(zs,zID)
            return(" ".join([str(s) for s in myD]) + " :" + str(dist(me,myD)) + ":avoid failed")
        else:
            return(" ".join([str(s) for s in myD]) + " :" + str(dist(me,myD)) + ":avoid")
    else:
        return(" ".join([str(s) for s in me]) + " :justme:")

def main():
    while 1:
        rData = parseInput()
        rData['mh'] = 1
        rData['mz'] = 2
        rData['zh'] = 2
        rData['c'] = 2
        AgentOutput = botResponse(rData)
        print(AgentOutput)

# game loop
if __name__ == '__main__':
    main()
