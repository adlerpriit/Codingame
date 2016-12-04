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


def angleDest(ref, angle, delta):
    x, y = ref
    x = x + int(math.cos(math.radians(angle)) * delta)
    y = y + int(math.sin(math.radians(angle)) * delta)
    return [x, y]


def aimTarget(pos, sv, target):
    dist_a = getDist(pos, target)
    point_a = getDest(pos, sv, dist_a)
    dist_b = getDist(point_a, target)
    point_b = getDest(point_a, target, 1.1 * dist_b)
    return point_b


def getAngleDest(pos_a, ref, alpha, delta):
    opt_a = angleDest(pos_a, alpha + 85, delta)
    opt_b = angleDest(pos_a, alpha - 85, delta)
    if getDist(opt_a, ref) < getDist(opt_b, ref) and random.randint(1,10) <= 6:
        return (opt_a)
    else:
        return (opt_b)


def getDist(pos_a, pos_b):
    return round(math.sqrt(abs(pos_a[0] - pos_b[0]) ** 2 + abs(pos_a[1] - pos_b[1]) ** 2), 4)


def getDest(pos_a, pos_b, d):
    d_ab = getDist(pos_a, pos_b)
    if d_ab == 0:
        return (pos_a)
    x = int(pos_a[0] - d * (pos_a[0] - pos_b[0]) / d_ab)
    y = int(pos_a[1] - d * (pos_a[1] - pos_b[1]) / d_ab)
    return ([x, y])


def getDestPounce(pos_a, pos_b, d):
    d_ab = getDist(pos_a, pos_b)
    if d_ab == 0:
        return (pos_a)
    x = int(pos_a[0] - d * (pos_a[0] - pos_b[0]) / d_ab)
    y = int(pos_a[1] - d * (pos_a[1] - pos_b[1]) / d_ab)
    #print("P", x, y, d, file=sys.stderr)
    if x < 0:
        Y = pos_a[1] - (pos_a[1] - y) * pos_a[0] / (pos_a[0] - x)
        x, y = getDest(pos_a, pos_b, getDist(pos_a, [0, Y]))
    if x > 16000:
        Y = pos_a[1] - (pos_a[1] - y) * (16000 - pos_a[0]) / (x - pos_a[0])
        x, y = getDest(pos_a, pos_b, getDist(pos_a, [16000, Y]))
    if y < 150:
        X = pos_a[0] - (pos_a[0] - x) * (pos_a[1] - 150) / (pos_a[1] - y)
        x, y = getDestPounce([X, 150], [x, 150 - (y - 150)], d - getDist(pos_a, [X, 150]))
    if y > 7350:
        X = pos_a[0] - (pos_a[0] - x) * (7350 - pos_a[1]) / (y - pos_a[1])
        x, y = getDestPounce([X, 7350], [x, 7350 - (y - 7350)], d - getDist(pos_a, [X, 7350]))
    return ([x, y])


def getAngleAbs(pos, target):
    alpha = math.degrees(math.atan2(target[1] - pos[1], target[0] - pos[0]))
    return (alpha)


def deltaAngle(alpha, beta):
    phi = abs(beta - alpha) % 360
    return (phi if phi < 180 else 360 - phi)


def correctTarget(W, T):
    myD = getDist(W['n'], T)
    spcoef = myD / (getDist([0, 0], W['sv']) + 500)
    T = [T[i] - int(W['sv'][i] * spcoef) for i in range(2)]
    print("Corrected:", T, file=sys.stderr)
    return T


def obstacleTarget(T, oteam, bludg, W, depth):
    if depth >= 40:
        print(T, depth, end="\t", file=sys.stderr)
        return T
    for bid in bludg:
        m2o = getDist(bludg[bid]['n'], W['n'])
        m2oD = getDest(W['n'], T, m2o)
        if getDist(bludg[bid]['n'], m2oD) < 800:
            T = getAngleDest(bludg[bid]['n'], [opGoalX, 3750], getAngleAbs(bludg[bid]['n'], W['n']),2400)
            return obstacleTarget(T, oteam, bludg, W, depth + 1)
    for oid in oteam:
        m2o = getDist(oteam[oid]['n'], W['n'])
        m2oD = getDest(W['n'], T, m2o)
        if getDist(oteam[oid]['n'], m2oD) < 1000:
            T = getAngleDest(oteam[oid]['n'], [opGoalX, 3750], getAngleAbs(oteam[oid]['n'], W['n']),3000)
            return obstacleTarget(T, oteam, bludg, W, depth + 1)
    print(T, depth, end="\t", file=sys.stderr)
    return T


def getOutput(wid, mteam, oteam, snaff, bludg, defend):
    W = mteam[wid]
    owid = sorted(mteam)
    owid = owid[1] if owid[0] == wid else owid[0]
    OW = mteam[owid]
    W['n2'] = [W['p'][i] + 2 * W['sv'][i] for i in range(2)]
    OW['n2'] = [OW['p'][i] + 3 * OW['sv'][i] for i in range(2)]
    T = [opGoalX, 3750]
    Dx,Dx2,Dm,Dm2,De = {},{},{},{},{}
    for sid in snaff:
        Dx[sid] = getDist([myGoalX, 3750], snaff[sid]['n'])
        Dx2[sid] = getDist([opGoalX, 3750], snaff[sid]['n'])
        Dm[sid] = getDist(W['n2'], snaff[sid]['n'])
        Dm2[sid] = getDist(OW['n'], snaff[sid]['n'])
        for oid in oteam:
            dist = getDist(oteam[oid]['n'], snaff[sid]['n'])
            if (sid in De and De[sid] > dist) or sid not in De:
                De[sid] = dist
    Dord = sorted(Dm, key=lambda k: Dm[k] * 6 + Dx[k]/3 + De[k] / 6)
    # Dord2 = sorted(Dx,key=lambda k:Dm2[k]*2+Dx[k]+De[k])
    Dord2 = sorted(Dx, key=lambda k: Dm2[k] * 3 + Dx[k] + De[k] / 6)
    if defend:
        Dord = sorted(Dx, key=lambda k: Dm[k] * 3 + Dx[k] + De[k] / 6)
        if score >= 0 and Dx[Dord[int(len(Dord)/2)]] > getDist(W['n'],[myGoalX,3750]):
            Dord = sorted(Dm, key=lambda k: Dm[k] * 3 + Dx[k]/3 + De[k] / 3)
        Dord2 = sorted(Dm2, key=lambda k: Dm2[k] * 6 + Dx[k]/3 + De[k] / 6)
    if W['S'] == 1:
        power = "500"
        myWD = getDist(W['p'], T)
        myOWD = getDist(OW['n2'], T)
        dW2OW = getDist(W['p'], OW['n2'])
        AW2OW = deltaAngle(getAngleAbs(W['n'],T),getAngleAbs(W['n'],OW['n2']))
        if AW2OW < 55 and dW2OW < 3000:
            T = OW['n2']
            print("Pass:", myWD, myOWD, dW2OW, file=sys.stderr)
        elif (len(Dord) > 1 and
              deltaAngle(getAngleAbs(W['n'],T),getAngleAbs(W['n'],snaff[Dord[1]]['n'])) < 45 and
              getDist(W['n'], snaff[Dord[1]]['n']) < 3000 and
              De[Dord[0]] > 5000):
            power = "250"
            T = getAngleDest(snaff[Dord[1]]['n'], W['n2'], getAngleAbs(snaff[Dord[1]]['n'], W['n']), 400)
        else:
            if abs(W['p'][0] - opGoalX) < 10000 or myMagic[0] >= 18:
                Y = W['p'][1] if (2600 < W['p'][1] < 4900) else (2600 if W['p'][1] < 2600 else 4900)
                T = [opGoalX, Y]
            else:
                myDa = getDist(W['p'], [abs(opGoalX - 10000), 0])
                myDb = getDist(W['p'], [abs(opGoalX - 10000), 7500])
                print(myDa, myDb, end="\t", file=sys.stderr)
                if myDa < myDb:
                    T = [abs(myGoalX - W['p'][0] - 6000), 0]
                else:
                    T = [abs(myGoalX - W['p'][0] - 6000), 7500]
        # print(myD,T,file=sys.stderr)
        T = obstacleTarget(T, oteam, bludg, W, 0)
        T = correctTarget(W, T)
        return ("THROW " + " ".join([str(s) for s in T]) + " " + power)
    if myMagic[0] > 10:
        for sid in sorted(Dx, key=Dx.get):
            sD = getDest(snaff[sid]['p'], snaff[sid]['n'], getDist(snaff[sid]['p'], snaff[sid]['n']) * 5)
            if (((sD[0] < 2 and my_team_id == 0) or (sD[0] > 15998 and my_team_id == 1)) and
                    (2100 < sD[1] < 5400) and
                        sid not in PETR and
                        snaff[sid]['p'] != mteam[owid]['p']):
                myMagic[0] -= 10
                # del snaff[sid]
                PETR[sid] = myTurn
                return ("PETRIFICUS " + sid)
            m2sD = getDist(snaff[sid]['p'], W['p'])
            m2sDA = deltaAngle(getAngleAbs(W['p'], W['n']), getAngleAbs(W['p'], snaff[sid]['n']))
            msv = getDist(W['p'], W['n']) or 1
            for oid in oteam:
                o2sD = getDist(snaff[sid]['p'], oteam[oid]['p'])
                o2sDn = getDist(snaff[sid]['n'], oteam[oid]['n'])
                osv = getDist(oteam[oid]['p'], oteam[oid]['n'])
                if o2sD > 400 and o2sDn < 400 and osv > 110 and sid not in PETR and (
                    (m2sDA < 60 and m2sD / msv < 6) or getDist([myGoalX, 3750], snaff[sid]['p']) < 4000):
                    myMagic[0] -= 10
                    PETR[sid] = myTurn
                    return ("PETRIFICUS " + sid)

    if myMagic[0] > 20:
        # need to better calculate flippendo path. and angles.. need to use sides to bypass opponents (also use that for aiming throws)
        for sid in sorted(Dm, key=Dm.get):
            # get new speed vector for snaff
            m2sA = getAngleAbs(W['n'], snaff[sid]['n'])
            m2s = getDist(W['n'], snaff[sid]['n'])
            A = deltaAngle(getAngleAbs(W['n'], T), m2sA)
            Fspeed = min(6000 / (Dm[sid] / 1000) ** 2, 1000)
            vx, vy = [snaff[sid]['sv'][i] + W['sv'][i] / 3 for i in range(2)]
            vx = snaff[sid]['n'][0] + round((vx + math.cos(math.radians(m2sA)) * Fspeed) * 0.75, 0)
            vy = snaff[sid]['n'][1] + round((vy + math.sin(math.radians(m2sA)) * Fspeed) * 0.75, 0)
            print(wid, sid, [vx, vy], end=" ", file=sys.stderr)
            sD = getDestPounce(snaff[sid]['p'], [vx, vy], (Fspeed + getDist([0, 0], snaff[sid]['sv'])) * 6)
            print(wid, sid, "Aim A:", A, "T:", sD, abs(W['n'][0] - opGoalX), m2s, file=sys.stderr)
            if len(Dm) <= 2 and A < 65 and abs(W['n'][0] - opGoalX) > 6000 and m2s < 3500:
                myMagic[0] -= 20
                return ("FLIPENDO " + sid)
            if (m2s < 3500 and A < 75 and
                abs(opGoalX - sD[0] < 3) and
                abs(W['n'][0] - opGoalX) > 3000 and
                (2300 < sD[1] < 5200)):
                myMagic[0] -= 20
                return ("FLIPENDO " + sid)
        for sid in sorted(Dx, key=Dx.get):
            # make sure there is no opponent between you and snaff, calculate that snaff vector would not end up in opp grasp
            m2s = getDist(W['n'], snaff[sid]['n'])
            if getDist([myGoalX, 3750], W['n']) > Dx[sid] + 1500 and m2s < 4000 and snaff[sid]['sv'][0] < 950:
                myMagic[0] -= 20
                return ("ACCIO " + sid)
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
    for i in range(len(Dord)):
        sid = Dord[i]
        if Dord2 and sid == Dord2[i] and Dm2[sid] < Dm[sid] and len(Dord2) > i + 1:
            continue
        if myMagic[0] > 18:
            T = getDest(T, snaff[sid]['n'], getDist(snaff[sid]['n'], T) + getDist(W['n'], snaff[sid]['n']) / 1.5)
            #Thrust = int(getDist(W['n'],T) / 4)
            #Thrust = "150" if Thrust > 150 else str(Thrust)
        else :
            T = getDest(T, snaff[sid]['n'], getDist(snaff[sid]['n'], T) + getDist(W['n'], snaff[sid]['n']) / 4)
            #Thrust = int(getDist(W['n'],T) / 3)
            #Thrust = "150" if Thrust > 150 else str(Thrust)
        T = [int(i) for i in aimTarget(W['p'], W['n'], T)]
        # A = deltaAngle(getAngleAbs(W['n'],T),getAngleAbs([0,0],W['sv']))
        # if A > 108:
        #     Thrust = str(150 - (int(A)-108))
        # print(A,file=sys.stderr)
        # if len(Dm) > 1:
        #    del snaff[sid]
        return ("MOVE " + " ".join([str(s) for s in T]) + " " + Thrust)
    return ("MOVE " + str(myGoalX) + " " + str(3750 + random.randint(-1500, 1500)) + " 150")


# Grab Snaffles and try to throw them through the opponent's goal!
# Move towards a Snaffle and use your team id to determine where you need to throw it.

mteam = dict()
oteam = dict()
snaff = dict()
bludg = dict()

score = 0
# game loop
while True:
    sTime = timer()
    myTurn += 1
    myMagic[0] += 1
    entities = int(input())  # number of entities still in game
    for i in range(entities):
        # entity_id: entity identifier
        # entity_type: "WIZARD", "OPPONENT_WIZARD" or "SNAFFLE" (or "BLUDGER" after first league)
        # x: position
        # y: position
        # vx: velocity
        # vy: velocity
        # state: 1 if the wizard is holding a Snaffle, 0 otherwise
        entity_ID, entity_type, x, y, vx, vy, state = input().split()
        #print(entity_ID, entity_type, x, y, vx, vy, state, file=sys.stderr)
        entity_properties = [int(x) for x in [x, y, vx, vy, state]]
        if entity_type == 'WIZARD':
            mteam[entity_ID] = {'p': entity_properties[0:2], 'sv': entity_properties[2:4], 'S': entity_properties[4]}
        if entity_type == 'OPPONENT_WIZARD':
            oteam[entity_ID] = {'p': entity_properties[0:2], 'sv': entity_properties[2:4], 'S': entity_properties[4]}
        if entity_type == 'SNAFFLE':
            snaff[entity_ID] = {'p': entity_properties[0:2], 'sv': entity_properties[2:4]}
        if entity_type == 'BLUDGER':
            bludg[entity_ID] = {'p': entity_properties[0:2], 'sv': entity_properties[2:4]}
    for sid in sorted(snaff):
        if 'n' in snaff[sid]:
            if abs(opGoalX - snaff[sid]['p'][0]) < 2000:
                score += 1
            else:
                score -= 1
            del snaff[sid]
            continue
        snaff[sid]['n'] = [snaff[sid]['p'][i] + snaff[sid]['sv'][i] for i in range(2)]
        # snaff[sid]['a'] = getAngleAbs([0,0],snaff[sid]['sv'])
    for oid in oteam:
        oteam[oid]['n'] = [oteam[oid]['p'][i] + oteam[oid]['sv'][i] for i in range(2)]
    for mid in mteam:
        mteam[mid]['n'] = [mteam[mid]['p'][i] + mteam[mid]['sv'][i] for i in range(2)]
    for bid in bludg:
        bludg[bid]['n'] = [bludg[bid]['p'][i] + bludg[bid]['sv'][i] for i in range(2)]

    defend = 0

    for wid in sorted(mteam):
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
        command = getOutput(wid, mteam, oteam, snaff, bludg, defend)

        # Edit this line to indicate the action for each wizard (0 ≤ thrust ≤ 150, 0 ≤ power ≤ 500)
        # i.e.: "MOVE x y thrust" or "THROW x y power"
        # if defend:
        #     command = command + " DEF"
        # else:
        #     command = command + " ATT"
        print(command)
        defend = 1
        # if re.match("PETRIFICUS",command):
        #     com,sid = command.split()
        #     PETR[sid] = myTurn
    for sid in sorted(PETR):
        if myTurn - PETR[sid] > 1:
            del PETR[sid]
    print("Score:",score," ---  Timing:", round(timer() - sTime, 5), file=sys.stderr)
