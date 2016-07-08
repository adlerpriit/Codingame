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

def project(pos_last,pos,dist,target):
    d_speed = getDist(pos_last,pos)
    point_a = getDest(pos_last,pos,dist+d_speed)
    d_dist = getDist(point_a,target)
    point_b = getDest(point_a,target,2*d_dist)
    return(point_b)

def getNextTarget(pos,track,next_key):
    next_cp = [int(i) for i in next_key.split(":")]
    if next_key not in track:
        next_angle = getAngle([pos,next_cp],[[8000,4500],next_cp])
        next_angle = 180 - next_angle
        if next_angle > 85:
            return([8000,4500],next_angle)
        else:
            return(next_cp,next_angle)
    sorted_track = sorted(track,key=lambda x: track[x]['n'])
    lenght_track = len(sorted_track)
    currentN = track[next_key]['n']
    if currentN == lenght_track:
        currentN = 0
    print("Targeting: ",str(currentN+1),file=sys.stderr)
    target_cp = [int(i) for i in sorted_track[currentN].split(":")]
    target_angle = getAngle([pos,next_cp],[target_cp,next_cp])
    return(target_cp,180 - target_angle)

def stillWithInLast(pos,last_key):
    last_cp = [int(i) for i in last_key.split(":")]
    last_dist = getDist(pos,last_cp)
    return(True if last_dist < 600 else False)

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

prev = dict()
track = dict()

boost = 1
N = 1
last_key = dict()

# game loop
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod orientation and the direction of the next checkpoint
    x, y, next_x, next_y, next_dist, angle = [int(i) for i in input().split()]
    o_x, o_y = [int(i) for i in input().split()]

    #thrust equals abs(angls)
    #print([next_dist,angle],file=sys.stderr)

    nX = next_x
    nY = next_y
    thrust = 100

    next_key = ":".join([str(i) for i in [next_x,next_y]])
    if 'key' in prev and prev['key'] not in track and prev['key'] != next_key :
        #learn track and it's checkpoints locations
        track[prev['key']] = {'n':N}
        N+=1
    if 'pos' in prev:
        #my speed
        speed = getDist(prev['pos'],[x,y])
        #opponent speed
        op_speed = getDist(prev['op_pos'],[o_x,o_y])
        #angle between my pod and opponents pod
        op_angle = getAngle([[x,y],prev['pos']],[[o_x,o_y],prev['op_pos']])
        #projection wether we'll be collading in next turn. collision == delta_me_op < 800
        delta_me_op = getDist(getDest(prev['pos'],[x,y],2*speed),getDest(prev['op_pos'],[o_x,o_y],2*op_speed))

        print([delta_me_op,op_speed,op_angle],file=sys.stderr)

        #nextTarget is next checkpoint if known or middle of the map if checkpoint is not known and agle is steep enough
        nextTarget,nextAngle = getNextTarget([x,y],track,next_key)

        #aim for the other side of the checkpoint relative to nextTarget: THIS SEEMS BUGGY
        #nX,nY = getDest(nextTarget,[next_x,next_y],getDist(nextTarget,[next_x,next_y])+200)

        if next_dist / speed < 4.5 and getDist(getDest(prev['pos'],[x,y],next_dist+speed),[next_x,next_y]) < 555:
            #if I'm close enough to checkpoint start plotting course toward next poi already.
            nX,nY = nextTarget
            angle = nextAngle
        
        print([nextTarget,angle,nextAngle],file=sys.stderr)
        
        if abs(angle) < 120:
            nX,nY = project(prev['pos'],[x,y],getDist([x,y],[next_x,next_y]),[nX,nY])
            thrust = 100
        else:
            thrust = 0
        
        if delta_me_op < 800 and (op_angle > 120 or next_dist / speed < 4.5 or stillWithInLast([x,y],prev['key'])):
            thrust = "SHIELD"
        
        if delta_me_op < 1800 and op_angle > 160 and boost > 0:
            thrust = "BOOST"
            boost -= 1

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)    
    
    if next_dist > 7000 and boost > 0 and angle == 0 and isinstance(thrust, int):
        thrust = "BOOST"
        boost -= 1
    # You have to output the target position
    # followed by the power (0 <= thrust <= 100)
    # i.e.: "x y thrust"
    print(str(int(nX)) + " " + str(int(nY)) + " " + str(thrust))
    prev = {'pos':[x,y],'op_pos':[o_x,o_y],'dist':next_dist,'key':next_key}
