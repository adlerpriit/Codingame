import sys
import math

# Save humans, destroy zombies!
# 63,610

def dist(i,j,k,l):
    return( math.sqrt((i - k)**2 + (j - l)**2) )

def z2hdist(hs,zs,x,y):
    dists = dict()
    for zid in zs:
        m2zd = dist(x,y,zs[zid][0],zs[zid][1])
        for hid in hs:
            z2hd = dist(hs[hid][0],hs[hid][1],zs[zid][0],zs[zid][1])
            m2hd = dist(x,y,hs[hid][0],hs[hid][1])
            safe = math.ceil(z2hd/400) - math.ceil(m2hd/1000 - 2)
            if hid in dists:
                if dists[hid]['s'] > safe:
                    dists[hid]['s'] = safe
                    dists[hid]['z'] = zid
                    dists[hid]['mz'] = math.ceil(m2zd/1000 - 2)
                    dists[hid]['mh'] = math.ceil(m2hd/1000 - 2)
                    dists[hid]['zh'] = math.ceil(z2hd/400)
            else:
                dists[hid] = dict()
                dists[hid]['s'] = safe
                dists[hid]['z'] = zid
                dists[hid]['mz'] = math.ceil(m2zd/1000 - 2)
                dists[hid]['mh'] = math.ceil(m2hd/1000 - 2)
                dists[hid]['zh'] = math.ceil(z2hd/400)
    return(dists)

def m2zdist(x,y,zs):
    mtoz = dict()
    for zid in zs:
        mtoz[zid] = dist(x,y,zs[zid][0],zs[zid][1])
    return(mtoz)

def avz(zs):
    X=Y=0
    for zid in zs:
       X+=zs[zid][0]
       Y+=zs[zid][1]
    X/=len(zs)
    Y/=len(zs)
    return(int(X),int(Y))

# game loop
while 1:
    x, y = [int(i) for i in input().split()]
    hs = dict()
    zs = dict()
    human_count = int(input())
    for i in range(human_count):
        human_id, human_x, human_y = [int(j) for j in input().split()]
        hs[human_id] = (human_x, human_y)
    zombie_count = int(input())
    for i in range(zombie_count):
        zombie_id, zombie_x, zombie_y, zombie_xnext, zombie_ynext = [int(j) for j in input().split()]
        zs[zombie_id] = (zombie_x,zombie_y,zombie_xnext,zombie_ynext)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    X, Y = x, y
    i = 0
    dists = z2hdist(hs,zs,x,y)
    hid = sorted(dists, key=lambda h: dists[h]['zh'])
    mtoz = m2zdist(x,y,zs)
    zid = sorted(mtoz, key=mtoz.get)
    print(" ".join([str(s) for s in [hid[i],dists[hid[i]]['z'],dists[hid[i]]['s'],dists[hid[i]]['mz']] ]),file=sys.stderr)
    while dists[hid[i]]['s'] < 0:
        if i == len(hid)-1:
            break
        i+=1
        print(" ".join([str(s) for s in [hid[i],dists[hid[i]]['z'],dists[hid[i]]['s'],dists[hid[i]]['mz']] ]),file=sys.stderr)
    
    if dists[hid[i]]['s'] > 6:
        X,Y = avz(zs)
        print("opt 1: average", file=sys.stderr)
    elif dists[hid[i]]['s'] > 3:
        X,Y = avz(zs)
        X = int((2*X + zs[zid[0]][2]) / 3)
        Y = int((2*Y + zs[zid[0]][3]) / 3)
        print("opt 1: biased average", file=sys.stderr)
    elif dists[hid[i]]['s'] > 0:
        #go for zombie
        X = int(zs[dists[hid[i]]['z']][2])
        Y = int(zs[dists[hid[i]]['z']][3])
        print("opt 2: go for zombi dangering human", file=sys.stderr)
    else:
        X = int((2*hs[hid[i]][0] + zs[dists[hid[i]]['z']][2]) / 3)
        Y = int((2*hs[hid[i]][1] + zs[dists[hid[i]]['z']][3]) / 3)
        print("opt 3: go for the human in danger", file=sys.stderr)

    # Your destination coordinates
    print(str(X)+" "+str(Y))
