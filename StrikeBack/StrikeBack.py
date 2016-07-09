import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

def getDist(pos_a,pos_b):
    return(int(math.sqrt(abs(pos_a[0]-pos_b[0])**2 + abs(pos_a[1]-pos_b[1])**2)))


def getDest(pos_a,pos_b,dist):
    d_ab = getDist(pos_a,pos_b)
    if d_ab == 0:
        return(pos_a)
    x = pos_a[0] - dist * (pos_a[0]-pos_b[0])/d_ab
    y = pos_a[1] - dist * (pos_a[1]-pos_b[1])/d_ab
    return([x,y])

def project(pos,next_pos,dist,target):
    point_a = getDest(pos,next_pos,dist)
    d_dist = getDist(point_a,target)
    point_b = getDest(point_a,target,2.5*d_dist)
    return(point_b)

def getNextTarget(track,pod):
    next_cpid = pod['N'] + 1
    if next_cpid >= race_cps:
        next_cpid -= race_cps
    next_cp = track[next_cpid]
    curr_cp = track[pod['N']]
    print("Targeting: ",str(next_cpid),file=sys.stderr)
    #angle between my accelaration direction and next target
    next_angle = deltaAngle(getAngleAbs(pod['pos'],next_cp),pod['angle'])
    return(next_cp,next_angle)

def stillWithInLast(track,pod):
    last_cpid = pod['N'] - 1
    if last_cpid < 0:
        last_cpid = race_cps - 1
    last_dist = getDist(pod['pos'],track[last_cpid])
    return(True if last_dist < 1000 else False)

def getAngle(vec_a,vec_b):
    #get angle between two vectors relative to vector a
    norm_a = [vec_a[1][0]-vec_a[0][0],vec_a[1][1]-vec_a[0][1]]
    norm_a = getDest([0,0],norm_a,1)
    norm_b = [vec_b[1][0]-vec_b[0][0],vec_b[1][1]-vec_b[0][1]]
    norm_b = getDest([0,0],norm_b,1)
    dot_ab = norm_a[0]*norm_b[0] + norm_a[1]*norm_b[1]
    #print([dot_ab],file=sys.stderr)
    dot_ab = 1 if dot_ab > 1 else -1 if dot_ab < -1 else dot_ab
    return(math.degrees(math.acos(dot_ab)))

def getAngleAbs(pos,target):
    alpha = math.degrees(math.atan2(target[1]-pos[1],target[0]-pos[0]))
    if alpha < 0:
        alpha += 360
    return(alpha)

def deltaAngle(alpha,beta):
    phi = abs(beta - alpha) % 360
    return(phi if phi < 180 else 360 - phi)
    

track = dict()
mpods = dict()
opods = dict()

boost = 1

#geme information
race_laps = int(input())
race_cps = int(input())
for cp in range(race_cps):
    cp_x,cp_y = [int(i) for i in input().split()]
    track[cp] = [cp_x,cp_y]

turn = 0
lap = 0
# game loop
while True:
    for pid in range(2):
        x,y,vx,vy,angle,next_cpid = [int(i) for i in input().split()]
        mpods[pid] = {'pos':[x,y],'next_pos':[x+vx,y+vy],'angle':angle,'N':next_cpid,'speed':getDist([0,0],[vx,vy])}
        #print(mpods[pid],file=sys.stderr)
    for oid in range(2):
        x,y,vx,vy,angle,next_cpid = [int(i) for i in input().split()]
        opods[oid] = {'pos':[x,y],'next_pos':[x+vx,y+vy],'angle':angle,'N':next_cpid,'speed':getDist([0,0],[vx,vy])}

    thrust = 100
    for pid in range(2):
        pod = mpods[pid]
        current_cp = track[pod['N']]
        nX,nY = current_cp
        angle = deltaAngle(getAngleAbs(pod['pos'],current_cp),pod['angle'])
        current_dist = getDist(pod['pos'],current_cp)
        next_cp,next_angle = getNextTarget(track,pod)
        print([current_cp,current_dist,angle,":",next_cp,next_angle],file=sys.stderr)
        if current_dist < pod['speed'] * 4.5 and getDist(getDest(pod['pos'],pod['next_pos'],current_dist),current_cp) < 555:
            #if I'm close enough to checkpoint
            nX,nY = next_cp
            angle = next_angle
            print("Close enough to CP",file=sys.stderr)
        
        if angle < 105 or turn < 3:
            nX,nY = project(pod['pos'],pod['next_pos'],current_dist,[nX,nY])
            thrust = 100
        else:
            thrust = 0
        
        delta_op = 999999
        angle_op = 0
        which_op = -1
        for oid in range(2):
            opod = opods[oid]
            delta_op_tmp = getDist(pod['next_pos'],opod['next_pos'])
            if delta_op_tmp < delta_op:
                delta_op = delta_op_tmp
                angle_op = getAngle([pod['next_pos'],pod['pos']],[opod['next_pos'],opod['pos']])
                which_op = oid
        print("Collision info: " + str(which_op) + " - " + str(int(delta_op)) + ":" + str(int(angle_op)),file=sys.stderr)
        if delta_op < 800:
            if angle_op > 90 or current_dist < pod['speed'] * 4.5 or stillWithInLast(track,pod):
                thrust = "SHIELD"
        if pid == 0 and turn == 1:
            thrust = "BOOST"
        if pid == 1 and angle < 2 and isinstance(thrust, int) and current_dist > 6000 and boost == 1:
            thrust = "BOOST"
            boost -= 1
        
        print(str(int(nX)) + " " + str(int(nY)) + " " + str(thrust))
    turn += 1
    #     if delta_me_op < 800 and op_angle > 160 and boost > 0:
    #         thrust = "BOOST"
    #         boost -= 1

