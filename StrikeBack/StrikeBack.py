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
    point_b = getDest(point_a,target,2*d_dist)
    return(point_b)

def getNextTarget(track,pod):
    next_cpid = pod['N'] + 1
    if next_cpid >= race_cps:
        next_cpid -= race_cps
    next_cp = track[next_cpid]
    curr_cp = track[pod['N']]
    #print("Targeting: ",str(next_cpid),file=sys.stderr)
    #angle between my accelaration direction and next target
    next_angle = deltaAngle(getAngleAbs(pod['pos'],next_cp),pod['angle'])
    cps_angle = deltaAngle(getAngleAbs(pod['pos'],curr_cp),getAngleAbs(curr_cp,next_cp))
    return(next_cp,next_angle,cps_angle)

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
    sign = 1 if ((alpha - beta >= 0 and alpha - beta <= 180) or (alpha - beta <= -180 and alpha - beta >= -360)) else -1
    return(sign * (phi if phi < 180 else 360 - phi))
    
def parsePods(line,lid,prev):
    x,y,vx,vy,angle,next_cpid = [int(i) for i in line.split()]
    if next_cpid == 1 and next_cpid != prev[lid]['N']:
        #we are on new lap
        prev[lid]['lap'] += 1
    prev[lid]['N'] = next_cpid
    #prev[lid]['next_pos'] = [x+vx,y+vy]
    return({'pos':[x,y],
            'sp_vec':[vx,vy],
            'angle':angle,
            'N':next_cpid,
            'lap':prev[lid]['lap']
            })

def getRank(mpods,opods,track):
    rank = []
    for i in range(2):
        rank.append({'id':'m','nr':i,'dist':getDist(mpods[i]['pos'],track[mpods[i]['N']]),'N':mpods[i]['N'],'lap':mpods[i]['lap']})
        rank.append({'id':'o','nr':i,'dist':getDist(opods[i]['pos'],track[opods[i]['N']]),'N':opods[i]['N'],'lap':opods[i]['lap']})
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
            x,y = opod['pos']
            vx,vy = opod['sp_vec']
            angle = opod['angle']
            angle_op = deltaAngle(angle,pod['angle'])
            dist_op = rank[i]['dist']
            x = x + vx + int(math.cos(math.radians(angle)) * 750)
            y = y + vy + int(math.sin(math.radians(angle)) * 750)
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
        mpods[pid] = parsePods(input(),pid,mprev)
        #print(mpods[pid],file=sys.stderr)
    for oid in range(2):
        opods[oid] = parsePods(input(),oid,oprev)
        #print(opods[oid],file=sys.stderr)
    
    rank = getRank(mpods,opods,track)
    for pid in range(2):
        thrust = 200
        pod = mpods[pid]

        next_cp,next_angle,cvsn_angle = getNextTarget(track,pod)

        cp = track[pod['N']]
        #cp = getDest(next_cp,cp,getDist(next_cp,cp)+abs(cvsn_angle)*10)
        sp_len = getDist([0,0],pod['sp_vec']) or 1
        dist_in_turns = getDist(pod['pos'],cp) / sp_len
        sp_vec_pos = [pod['pos'][0] + pod['sp_vec'][0],pod['pos'][1] + pod['sp_vec'][1]]
        if dist_in_turns < 5 and getDist(getDest(pod['pos'],sp_vec_pos,getDist(pod['pos'],cp)),cp) < 500:
            cp = next_cp
            angle = next_angle
        if doBlock(pid,rank):
            print(str(pid) + " blocking",file=sys.stderr)
            cp = getLeadOpp(pod,rank,opods,track)

        angle = deltaAngle(getAngleAbs(pod['pos'],cp),pod['angle'])
        dist = getDist(pod['pos'],cp)

        if turn==0:
            pod['angle'] = angle
            angle = 0

        print({'angle':int(angle),'pod vs next':int(next_angle),'current vs next':int(cvsn_angle)},file=sys.stderr)
        # if pod['cp_dist'] < pod['speed'] * prox_constant and getDist(getDest(pod['pos'],pod['next_pos'],pod['cp_dist']),pod['cp_pos']) < 450:
        #     #if I'm close enough to checkpoint
        #     nX,nY = next_cp
        #     angle = next_angle
            #print("Close enough to CP",file=sys.stderr)
        
        if abs(angle) > 105:
            thrust = 0

        angle *= 1.5
        if abs(angle) > 18:
            angle = 18 if angle > 0 else -18
        angle = pod['angle']+angle
        #predict next position
        vx = pod['sp_vec'][0] + int(math.cos(math.radians(angle)) * thrust)
        vy = pod['sp_vec'][1] + int(math.sin(math.radians(angle)) * thrust)
        next_pos = [pod['pos'][0] + vx,pod['pos'][1] + vy]
        speed = getDist(pod['pos'],next_pos)
        #print("Pod dist error: " + str(int(getDist(pod['pos'],mprev[pid]['next_pos']))),file=sys.stderr)
        mprev[pid]['next_pos'] = next_pos
        
        nX = pod['pos'][0] + math.cos(math.radians(angle)) * 2000
        nY = pod['pos'][1] + math.sin(math.radians(angle)) * 2000
        #if abs(angle) > 105:
        #    thrust = 0
        #nX,nY = project(pod['pos'],pod['next_pos'],pod['cp_dist']*(1+angle/180),[nX,nY])
        #thrust = 100 - int(angle**3 * 100 / 180**3)
        #else:
        #    thrust = "SHIELD"
        
        #check my other pod and if collision (in two) the one who is further behind will drop throttle
        
        delta_op = 999999
        angle_op = 0
        which_op = -1
        colli_op = [8000,4500]
        for oid in range(2):
            opod = opods[oid]
            x,y = opod['pos']
            vx,vy = opod['sp_vec']
            angle_op = opod['angle']
            x = x + vx + int(math.cos(math.radians(angle_op)) * 200)
            y = y + vy + int(math.sin(math.radians(angle_op)) * 200)
            opod_next_pos = [x,y]
            delta_op_tmp = getDist(next_pos,opod_next_pos)
            if delta_op_tmp < delta_op:
                delta_op = delta_op_tmp
                angle_op = getAngle([next_pos,pod['pos']],[opod_next_pos,opod['pos']])
                which_op = oid
                colli_op = opod_next_pos
        print("Collision info: " + str(which_op) + " - " + str(int(delta_op)) + ":" + str(int(angle_op)),file=sys.stderr)
        if delta_op < 800:
            if angle_op < 90:
                nX,nY = colli_op
                thrust = 200
            elif angle_op > 90 and speed > 300:
                thrust = "SHIELD"
        if turn < 1:
            thrust = 100
        if pid == 0 and turn == 0:
            thrust = "BOOST"
        if angle < 2 and isinstance(thrust, int) and mprev[pid]['lap'] == race_laps and pod['N'] == 0:
            thrust = "BOOST"
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