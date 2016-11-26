import sys
import math
import random

my_team_id = int(input())  # if 0 you need to score on the right of the map, if 1 you need to score on the left

opGoalX = 0 if my_team_id == 1 else 16000
myGoalX = 300 if my_team_id == 0 else 15700
myMagic = [0]

def getDist(pos_a,pos_b):
    return(int(math.sqrt(abs(pos_a[0]-pos_b[0])**2 + abs(pos_a[1]-pos_b[1])**2)))

def getAngleAbs(pos,target):
    alpha = math.degrees(math.atan2(target[1]-pos[1],target[0]-pos[0]))
    if alpha < 0:
        alpha += 360
    return(alpha)

def deltaAngle(alpha,beta):
    phi = abs(beta - alpha) % 360
    return(phi if phi < 180 else 360 - phi)

def getOutput(W,oteam,snaff,bludg):
    if W['S'] == 1:
        T = [opGoalX,3750+random.randint(-1500,1500)]
        for oid in oteam:
            m2o = getDist(oteam[oid]['p'],W['p'])
            o2t = getDist(oteam[oid]['p'],T)
            m2t = getDist(W['p'],T)
            #print(m2o + o2t - m2t,file=sys.stderr)
            if m2o + o2t - m2t < 400:
                T[1] = 0 if W['p'][1] > 3750 else 7500
        return("THROW " + " ".join([str(s) for s in T]) + " 500")
    D = {}
    if myMagic[0] > 20:
        for sid in snaff:
            D[sid] = getDist([myGoalX,3750],snaff[sid]['p'])
        for sid in sorted(D,key=D.get):
            m2s = getDist(W['p'],snaff[sid]['p'])
            if getDist([myGoalX,3750],W['p']) > D[sid] + 750 and m2s < 4000:
                myMagic[0] -= 20
                return("ACCIO " + sid)
    Thrust = "150"
    for sid in snaff:
        D[sid] = getDist(W['p'],snaff[sid]['p'])
    for sid in sorted(D,key=D.get):
        T = snaff[sid]['p']
        A = deltaAngle(getAngleAbs(W['p'],T),getAngleAbs([0,0],W['sv']))
        if A > 108:
            Thrust = str(150 - (int(A)-108))
        print(A,file=sys.stderr)
        if len(D) > 1:
            del snaff[sid]
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
        #print(entity_ID,entity_type,x,y,vx,vy,state,file=sys.stderr)
        entity_properties = [int(x) for x in [x,y,vx,vy,state]]
        if entity_type == 'WIZARD':
            mteam[entity_ID] = {'p':entity_properties[0:2],'sv':entity_properties[2:4],'S':entity_properties[4]}
        if entity_type == 'OPPONENT_WIZARD':
            oteam[entity_ID] = {'p': entity_properties[0:2], 'sv': entity_properties[2:4],'S': entity_properties[4]}
        if entity_type == 'SNAFFLE':
            snaff[entity_ID] = {'p':entity_properties[0:2],'sv':entity_properties[2:4]}
        if entity_type == 'GLUDGER':
            bludg[entity_ID] = {'p':entity_properties[0:2],'sv':entity_properties[2:4]}


    for wid in sorted(mteam):

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
        command = getOutput(mteam[wid],oteam,snaff,bludg)

        # Edit this line to indicate the action for each wizard (0 ≤ thrust ≤ 150, 0 ≤ power ≤ 500)
        # i.e.: "MOVE x y thrust" or "THROW x y power"
        print(command)
