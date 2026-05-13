import sys
import math
import time
from collections import defaultdict

class Point(object):
    def __init__(self, x, y, radius=0):
        self.x = x
        self.y = y
        self.r = radius
    
    def distance2(self, p):
        return (self.x - p.x) ** 2 + (self.y - p.y) ** 2
    
    def distance(self, p):
        return self.distance2(p) ** 0.5
    
    def angle(self, p):
        # this is the angle from point a to point b in radians
        # passing it through math.degrees() will give you the angle in degrees where y = 0, x = 0 is 0 degrees and y = 0 and x = -1 is 180 degrees, 
        # positive y is 0 .. 180, negative y is -0 .. -180, though 0 and 180 are always positive
        return math.atan2(p.y - self.y, p.x - self.x)
    
    def _normalize_angle(self, angle):
        if angle > math.pi:
            angle -= 2 * math.pi
        if angle < -math.pi:
            angle += 2 * math.pi
        return angle
    
    def project(self, d, angle):
        # project a point d units away from this point at angle
        return Point(int(self.x + d * math.cos(angle)), int(self.y + d * math.sin(angle)))


class pod(Point):
    def __init__(self, id, x, y, vx, vy, facing, ncpid):
        super().__init__(x, y, 400)
        self.id = id
        self.vx = vx
        self.vy = vy
        self.facing = facing 
        self.ncpid = ncpid # next check point id

    def next_position(self, thrust, angle, cps):
        # thrust 0 to 200, or BOOST(650)
        # angle is -18 to 18 in degrees (dependent upon current facing angle)
        angle = self.facing + math.radians(angle)
        if angle > math.pi:
            angle -= 2 * math.pi
        if angle < -math.pi:
            angle += 2 * math.pi
        # calculate new velocity vector
        vx = int(math.cos(angle) * thrust)
        vy = int(math.sin(angle) * thrust)
        # calculate next position
        x = self.x + self.vx + vx
        y = self.y + self.vy + vy
        # apply friction
        vx = int(0.85 * (self.vx + vx))
        vy = int(0.85 * (self.vy + vy))
        # check if we're taking the next checkpoint
        ncpid = self.ncpid
        if Point(x, y).distance(cps[self.ncpid]) < 600:
            ncpid = self.ncpid + 1
        if ncpid == len(cps):
            ncpid = 0
        # return f"pos: {x}, {y} speed: {vx}, {vy} ({thrust}, {angle})"
        return pod(self.id, x, y, vx, vy, angle, ncpid)


    def action(self, cps, opps):
        # cps are a list of checkpoints
        # opps are a list of opponents
        # my currenct velocity is expressed by vx and vy
        # my current facing angle is expressed by facing
        # I can change my facing angle by 18 degrees per turn
        # we can do 90 degree turn in 5 turns
        # the combination of current velocity and facing angle after optional turning with trust value will determine my next turn velocity vector

        # we'll start off slow as usual
        # first calculate angle between my current volocity and next checkpoint
        ccp = cps[self.ncpid]
        ncp = cps[(self.ncpid + 1) % len(cps)]


        if self.vx ** 2 + self.vy ** 2 < 10 ** 2:
            # if I'm not moving, I'll just move towards the next checkpoint with max thrust
            return f"{ccp.x} {ccp.y} BOOST"
        
        # calculate angle between current velocity vector and next checkpoint
        angle_v = math.atan2(self.vy, self.vx)
        speed_v = (self.vx ** 2 + self.vy ** 2) ** 0.5

        # calculate angles
        angle_ccp = self.angle(ccp)
        angle_ncp = ncp.angle(ccp)
        angle_ccp_v = self._normalize_angle(angle_v - angle_ccp)
        angle_ccp_f = self._normalize_angle(self.facing - angle_ccp)

        # calculate distances
        dist_ccp = self.distance(ccp)
        dist_ncp = ncp.distance(ccp)

        if dist_ccp / speed_v > 7:
            target = ncp.project(dist_ncp + 500 * (self._normalize_angle(angle_ncp - 2*math.pi - angle_ccp)), angle_ncp)
        else:
            # project potential target position
            target = self.project(dist_ccp * 0.75, angle_ccp - angle_ccp_v / 2)


        thrust = 200 - int(math.log(abs(angle_ccp_f) + 1) * 140)

        return f"{target.x} {target.y} {thrust}"



class checkPoint(Point):
    def __init__(self, x, y):
        super().__init__(x, y, 600)


laps = int(input())
checkpoints = [checkPoint(*[int(j) for j in input().split()]) for _ in range(int(input()))]

# game loop
while True:
    start_time = time.perf_counter()
    mPods = []
    for i in range(2):
        x, y, vx, vy, facing, ncpid = [int(j) for j in input().split()]
        # facing is given in degrees 0 to 360 0 is facing E, 90 is facing S, 180 is facing W, 270 is facing N
        if facing == -1:
            facing = Point(x, y).angle(checkpoints[ncpid])
        else:
            facing = math.radians(facing)
            if facing > math.pi:
                facing -= 2 * math.pi
        mPods.append(pod(i, x, y, vx, vy, facing, ncpid))
    oPods = []
    for i in range(2):
        x, y, vx, vy, facing, ncpid = [int(j) for j in input().split()]
        # facing is given in degrees 0 to 360 0 is facing E, 90 is facing S, 180 is facing W, 270 is facing N
        if facing == -1:
            facing = Point(x, y).angle(checkpoints[ncpid])
        else:
            facing = math.radians(facing)
            if facing > math.pi:
                facing -= 2 * math.pi
        oPods.append(pod(i, x, y, vx, vy, facing, ncpid))
    

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # You have to output the target position
    # followed by the power (0 <= power <= 200)
    # i.e.: "x y power"
    for p in mPods:
        # if p.id == 0:
        #     project = {}
        #     for thrust in range(0, 201, 50):
        #         for angle in range(-18, 19, 9):
        #             project[(thrust, angle)] = p.next_position(thrust, angle, checkpoints)
        #     t2 = defaultdict(list)
        #     for k, v in project.items():
        #         for thrust in range(0, 201, 60):
        #             for angle in range(-18, 19, 18):
        #                 t2[k].append(v.next_position(thrust, angle, checkpoints))
        #     t3 = defaultdict(list)
        #     for k, l in t2.items():
        #         for v in l:
        #             for thrust in range(0, 201, 60):
        #                 for angle in range(-18, 19, 18):
        #                     t3[k].append(v.next_position(thrust, angle, checkpoints))
        #     attr = None
        #     min_dist = 9e9
        #     for k, l in t3.items():
        #         for v in l:
        #             d = int(v.distance(checkpoints[v.ncpid]))
        #             if d < min_dist:
        #                 min_dist = d
        #                 attr = k
        #                 print(f"{k} => {d}", file=sys.stderr, flush=True)
        #     thrust, angle = attr
        #     facing = math.radians(p.facing)
        #     if p.facing == -1:
        #         facing = p.angle(checkpoints[p.ncpid])
        #     if facing > math.pi:
        #         facing -= 2 * math.pi
        #     #assign new facing angle
        #     angle = facing + math.radians(angle)
        #     tx = p.x + int(math.cos(angle) * (thrust + 5))
        #     ty = p.y + int(math.sin(angle) * (thrust + 5))
        #     print(f"{tx} {ty} {thrust}")
        # else:
        print(p.action(checkpoints, oPods))


    end_time = time.perf_counter()
    print(f"Time taken for one iteration: {(end_time - start_time):.6f} seconds", file=sys.stderr, flush=True)
