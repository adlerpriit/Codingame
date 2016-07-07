import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

def getDist(pos_a,pos_b):
    return(int(math.sqrt(abs(pos_a[0]-pos_b[0])**2 + abs(pos_a[1]-pos_b[1])**2)))


def getDest(pos_a,pos_b,dist):
    d_ab = getDist(pos_a,pos_b)
    d_ab = 1 if d_ab == 0 else d_ab
    x = int(pos_a[0] - dist * (pos_a[0]-pos_b[0])/d_ab)
    y = int(pos_a[1] - dist * (pos_a[1]-pos_b[1])/d_ab)
    return([x,y])

def project(pos_last,pos,dist,target):
    d_speed = getDist(pos_last,pos)
    point_a = getDest(pos_last,pos,dist+d_speed)
    d_dist = getDist(point_a,target)
    point_b = getDest(point_a,target,2*d_dist)
    return(point_b)

def getNextTarget(track,next_key,last_key):
    sorted_track = sorted(track,key=lambda x: track[x]['n'])
    lenght_track = len(sorted_track)
    currentN = track[next_key]['n']
    if currentN == lenght_track:
        currentN = 0
    if sorted_track[currentN] == last_key:
        return(track[next_key]['pos'])
    else:
        return(track[sorted_track[currentN]]['pos'])

prev = dict()
track = dict()

boost = 1
N = 1
last_key = None

# game loop
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod orientation and the direction of the next checkpoint
    x, y, next_x, next_y, next_dist, angle = [int(i) for i in input().split()]
    o_x, o_y = [int(i) for i in input().split()]


    #thrust equals abs(angls)
    print([next_dist,angle],file=sys.stderr)

    if 'dist' in prev:
        print([prev['dist'] - next_dist,prev['a']-angle,prev['key']],file=sys.stderr)

    nX = next_x
    nY = next_y
    angle_limit = 100 if abs(angle) >= 90 else 0


    next_key = ":".join([str(i) for i in [next_x,next_y]])
    if 'key' in prev and prev['key'] != next_key:
        last_key = prev['key']
        print("Cleared checkpoint " + str(track[last_key]['n']),file=sys.stderr)
    if next_key not in track:
        track[next_key] = {'pos':[next_x,next_y],'n':N}
        N+=1
    #else:
        #may start to plot better course as we have explored entire lap
        #there are several aspects, we can speed up getting through checkpoints, by altering target coordinate
        #by same margin to the other side that is projected by heading line.
    if 'pos' in prev:
        speed = getDist(prev['pos'],[x,y])
        if next_dist < speed * 4:
            nX,nY = getNextTarget(track,next_key,last_key)
        if abs(angle) < 90:
            nX,nY = project(prev['pos'],[x,y],getDist([x,y],[nX,nY]),[nX,nY])
            angle_limit = angle**4 * 90 / 90**4


    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)    

    print("speed correction: " + str(angle_limit),file=sys.stderr)

    thrust = 100 - int(angle_limit)
    
    thrust = 0 if thrust < 0 else thrust
    

    if next_dist > 6000 and boost > 0 and angle == 0:
        thrust = "BOOST"
        boost -= 1

    # You have to output the target position
    # followed by the power (0 <= thrust <= 100)
    # i.e.: "x y thrust"
    print(str(nX) + " " + str(nY) + " " + str(thrust))
    prev = {'a':angle,'pos':[x,y],'dist':next_dist,'key':next_key}
