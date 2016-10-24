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
    point_b = getDest(point_a,target,1.75*d_dist)
    return(point_b)

def getNextTarget(track,pod):
    next_cpid = pod['N'] + 1
    if next_cpid >= race_cps:
        next_cpid -= race_cps
    next_cp = track[next_cpid]
    #print("Targeting: ",str(next_cpid),file=sys.stderr)
    #angle between my accelaration direction and next target
    next_angle = deltaAngle(getAngleAbs(pod['pos'],next_cp),pod['angle'])
    return(next_cp,next_angle)

def stillWithInLast(track,pod):
    last_cpid = pod['N'] - 1
    if last_cpid < 0:
        last_cpid = race_cps - 1
    last_dist = getDist(pod['pos'],track[last_cpid])
    return(True if last_dist < 666 else False)

def getAngle(vec_a,vec_b):
    #get angle between two vectors relative to vector a
    norm_a = getDest([0,0], [vec_a[1][0]-vec_a[0][0],vec_a[1][1]-vec_a[0][1]], 1)
    norm_b = getDest([0,0], [vec_b[1][0]-vec_b[0][0],vec_b[1][1]-vec_b[0][1]], 1)
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
    
def parsePods(line,lid,track,prev):
    x,y,vx,vy,angle,next_cpid = [int(i) for i in line.split()]
    vx = vx + int(math.cos(math.radians(angle)) * 195)
    vy = vy + int(math.sin(math.radians(angle)) * 195)
    current_cp = track[next_cpid]
    current_angle = deltaAngle(getAngleAbs([x,y],current_cp),angle)
    current_dist = getDist([x,y],current_cp)
    #print("Pod dist error: " + str(int(getDist([x,y],prev[lid]['next_pos']))),file=sys.stderr)
    if next_cpid == 1 and next_cpid != prev[lid]['N']:
        #we are on new lap
        prev[lid]['lap'] += 1
    prev[lid]['N'] = next_cpid
    prev[lid]['next_pos'] = [x+vx,y+vy]
    #print(mprev,file=sys.stderr)
    return({'pos':[x,y],
            'next_pos':[x+vx,y+vy],
            'angle':angle,
            'N':next_cpid,
            'speed':getDist([0,0],[vx,vy]),
            'cp_pos':current_cp,
            'cp_angle':int(current_angle),
            'cp_dist':current_dist,
            'lap':prev[lid]['lap']
            })

def getRank(mpods,opods):
    rank = []
    for i in range(2):
        rank.append({'id':'m','nr':i,'dist':mpods[i]['cp_dist'],'N':mpods[i]['N'],'lap':mpods[i]['lap']})
        rank.append({'id':'o','nr':i,'dist':opods[i]['cp_dist'],'N':opods[i]['N'],'lap':opods[i]['lap']})
    rank = sorted(rank,key=lambda x: x['dist'])
    rank = sorted(rank,key=lambda x: race_cps if x['N'] == 0 else x['N'],reverse=True)
    rank = sorted(rank,key=lambda x: x['lap'],reverse=True)
    #for i in range(len(rank)):
        #print("Rank " + str(i+1) + ":" + rank[i]['id'] + str(rank[i]['nr']),file=sys.stderr)
    return(rank)

def getLeadOpp(pod,rank,opods,track):
    for i in range(len(rank)):
        if rank[i]['id'] == 'o':
            opod = opods[rank[i]['nr']]
            vx,vy = opod['next_pos']
            angle = opod['angle']
            angle_op = deltaAngle(angle,pod['angle'])
            dist_op = rank[i]['dist']
            dist_me_op = getDist(opod['pos'],pod['pos'])
            x = vx + int(math.cos(math.radians(angle)) * (dist_me_op/4))
            y = vy + int(math.sin(math.radians(angle)) * (dist_me_op/4))
            dist_me = getDist(pod['pos'],track[opod['N']])
            if dist_me > dist_op and abs(angle_op) < 90:
                #go to next target
                next_cpid = opod['N'] + 1
                if next_cpid >= race_cps:
                    next_cpid -= race_cps
                x,y = track[next_cpid]
            return([x,y])

def doBlock(pid,rank):
    if rank[0]['id'] == "o":
        for i in range(1,4):
            if rank[i]['id'] == "m":
                return(False if rank[i]['nr'] == pid else True)
    return(False)


track = dict()
mpods = dict()
opods = dict()

#geme information
race_laps = int(input())
race_cps = int(input())
for cp in range(race_cps):
    cp_x,cp_y = [int(i) for i in input().split()]
    track[cp] = [cp_x,cp_y]
mprev = {0:{'lap':1,'N':1,'next_pos':track[0]},1:{'lap':1,'N':1,'next_pos':track[0]}}
oprev = {0:{'lap':1,'N':1,'next_pos':track[0]},1:{'lap':1,'N':1,'next_pos':track[0]}}

turn = 0
prox_constant = 4
# game loop
while True:
    for pid in range(2):
        mpods[pid] = parsePods(input(),pid,track,mprev)
        #print(mpods[pid],file=sys.stderr)
    for oid in range(2):
        opods[oid] = parsePods(input(),oid,track,oprev)
        #print(opods[oid],file=sys.stderr)
    
    rank = getRank(mpods,opods)
    thrust = 200
    for pid in range(2):
<<<<<<< HEAD
=======
        thrust = 200
>>>>>>> angle_system
        pod = mpods[pid]
        nX,nY = pod['cp_pos']
        angle = pod['cp_angle']
        next_cp,next_angle = getNextTarget(track,pod)
        #print([current_cp,current_dist,angle,":",next_cp,next_angle],file=sys.stderr)
        if pod['cp_dist'] < pod['speed'] * prox_constant and getDist(getDest(pod['pos'],pod['next_pos'],pod['cp_dist']),pod['cp_pos']) < 500:
            #if I'm close enough to checkpoint
            nX,nY = next_cp
            angle = next_angle
            #print("Close enough to CP",file=sys.stderr)
        
        if doBlock(pid,rank):
            print(str(pid) + " blocking",file=sys.stderr)
            nX,nY = getLeadOpp(pod,rank,opods,track)
            angle = deltaAngle(getAngleAbs(pod['pos'],[nX,nY]),pod['angle'])
        
        if angle < 108:
            nX,nY = project(pod['pos'],pod['next_pos'],pod['cp_dist']*(1+angle/180),[nX,nY])
            if pod['speed']:
                cp_dl = pod['cp_dist']/pod['speed']
                if angle < cp_dl*18:
                    thrust = 200 - int(angle * 150 / 108)
                else:
                    thrust = 0
        
        #check my other pod and if collision (in two) the one who is further behind will drop throttle
        
        delta_op = 999999
        angle_op = 0
        which_op = -1
        for oid in range(2):
            opod = opods[oid]
<<<<<<< HEAD
            delta_op_tmp = getDist(pod['next_pos'],opod['next_pos'])
=======
            x,y = opod['pos']
            vx,vy = opod['sp_vec']
            angle_op = opod['angle']
            x = x + vx + int(math.cos(math.radians(angle_op)) * 200)
            y = y + vy + int(math.sin(math.radians(angle_op)) * 200)
            opod_next_pos = [x,y]
            delta_op_tmp = getDist(next_pos,opod_next_pos)
>>>>>>> angle_system
            if delta_op_tmp < delta_op:
                delta_op = delta_op_tmp
                angle_op = getAngle([pod['next_pos'],pod['pos']],[opod['next_pos'],opod['pos']])
                which_op = oid
                speed_op = opod['speed']
        print("Collision info: " + str(which_op) + " - " + str(int(delta_op)) + ":" + str(int(angle_op)),file=sys.stderr)
        if delta_op < 800 and speed_op + pod['speed'] > 600:
            if angle_op < 90:
<<<<<<< HEAD
                nX,nY = opods[which_op]['next_pos']
                thrust = 200
            elif angle_op > 90 or current_dist < pod['speed'] * prox_constant or stillWithInLast(track,pod):
=======
                nX,nY = colli_op
                thrust = 200
            elif angle_op > 90 and speed > 300:
>>>>>>> angle_system
                thrust = "SHIELD"
        if turn < 1:
            thrust = 200
        if pid == 0 and turn == 0:
            thrust = "BOOST"
        if pid == 1 and angle < 2 and isinstance(thrust, int) and 'lap' in mprev[pid] and mprev[pid]['lap'] == race_laps and pod['N'] == 0:
            thrust = "BOOST"
<<<<<<< HEAD
        print(str(int(nX)) + " " + str(int(nY)) + " " + str(thrust))
    turn += 1
=======
        print(str(int(nX)) + " " + str(int(nY)) + " " + str(thrust) + " " + str(mprev[pid]['lap']) + ":" + str(pod['N']))
    turn += 1


#Some notes here
#First to make some pen and paper action. Also some testing

#test actual speed, this can also be calculated: speed_vector + angle[corrected, max diff 18°]*thust
#max straight speed is 1327 ... takes 36 turns to achieve
#stable turn speed is 1276 ... from max speed it takes 17 turns to get

#from the speed and angle max correction we can calculate circle radius
#half a circle with 10 coordinate points and assuming stable turn speed (1276), the arc diameter at ends is 8054. radius to 90° sector midpoint is 3389. this arc enables to enter 0° and exit at 180°. though as it is so wide, it probably is not worth to try to take the checkpoints at full speed.
#also should check, probably takes less turns and less time to get through checkpoint if lowering speed.

#tricky part is to find the entry and exit points the to the circle.
#but basically if reached entry point, aim for the center point and pod will follow the circle

#calculating the circle is still tricky. It should take into account my speed, distance from checkpoint, angle between me, checkpoint and next checkpoint. dynamically correct the arc entry point, and my speed
>>>>>>> angle_system
