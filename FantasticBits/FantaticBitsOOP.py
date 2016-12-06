import sys
import math
import random


# Grab Snaffles and try to throw them through the opponent's goal!
# Move towards a Snaffle and use your team id to determine where you need to throw it.
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance2(self, p):
        return (self.x - p.x) * (self.x - p.x) + (self.y - p.y) * (self.y - p.y)

    def distance(self, p):
        return math.sqrt(self.distance2(p))

    def angle(self, p):
        alpha = math.atan2(p.y - self.y, p.x - self.x)
        return alpha

    def closest(self, a, b):
        da = b.y - a.y
        db = a.x - b.y
        c1 = da * a.x + db * a.y
        c2 = -db * self.x + da * self.y
        det = da * da + db * db
        cx = 0
        cy = 0
        if det != 0:
            cx = (da * c1 - db * c2) / det
            cy = (da * c2 + db * c1) / det
        else:
            # the point is already on the line
            cx = self.x
            cy = self.y
        return Point(cx, cy)


class Collision:
    def __init__(self, a, b, t):
        self.a = a
        self.b = b
        self.t = t


class Unit(Point):
    def __init__(self, mid, vx, vy, x, y):
        super().__init__(x, y)
        self.mid = mid
        self.vx = vx
        self.vy = vy

    def collision(self, u):
        # square of the distance
        dist = self.distance2(u)
        # sum of radii squared
        sr = (self.r + u.r) * (self.r + u.r)
        if (type(self) is Wizard and type(u) is Snaffle) or (type(u) is Wizard and type(self) is Snaffle):
            if type(self) is Wizard:
                sr = (self.r - 1 + self.r - 1) * (self.r - 1 + self.r - 1)
            else:
                sr = (u.r - 1 + u.r - 1) * (u.r - 1 + u.r - 1)
        if dist < sr:
            return Collision(self, u, 0.0)
        if self.vx == u.vx and self.vy == u.vy:
            return None
        # change reference. make u stationary
        x = self.x - u.x
        y = self.y - u.y
        myp = Point(x, y)
        vx = self.vx - u.vx
        vy = self.vy - u.vy
        up = Point(0, 0)
        p = up.closest(myp, Point(x + vx, y + vy))
        pdist = up.distance2(p)
        mypdist = myp.distance2(p)
        if pdist < sr:
            length = math.sqrt(vx * vx + vy * vy)
            # find point along the line where the collision occurs?
            backdist = math.sqrt(sr - pdist)
            p.x -= backdist * (vx / length)
            p.y -= backdist * (vy / length)
            # point now further, we're going in wrong way
            if myp.distance2(p) > mypdist:
                return None
            pdist = p.distance(myp)
            if pdist > length:
                return None
            t = pdist / length
            return Collision(self, u, t)
        return None

    def bounce(self, u):
        #print(self.mid, [self.vx,self.vy], file=sys.stderr)
        #print(u.mid, [u.vx,u.vy], file=sys.stderr)
        m1 = self.m
        m2 = u.m
        mcoeff = (m1 + m2) / (m1 * m2)
        nx = self.x - u.x
        ny = self.y - u.y
        # distance between units while colliding squared
        dnxny2 = nx * nx + ny * ny
        dvx = self.vx - u.vx
        dvy = self.vy - u.vy
        # impact factor
        product = nx * dvx + ny * dvy
        fx = (nx * product) / (dnxny2 * mcoeff)
        fy = (ny * product) / (dnxny2 * mcoeff)
        # apply impact factor once
        self.vx -= fx / m1
        self.vy -= fy / m1
        u.vx += fx / m2
        u.vy += fy / m2
        # if impulse is less than 100, normalise it to 100
        impulse = math.sqrt(fx * fx + fy * fy)
        if impulse < 100:
            fx = fx * 100 / impulse
            fy = fy * 100 / impulse
        # apply impact factor once more
        self.vx -= fx / m1
        self.vy -= fy / m1
        u.vx += fx / m2
        u.vy += fy / m2
        #print(self.mid, [self.vx, self.vy], file=sys.stderr)
        #print(u.mid, [u.vx, u.vy], file=sys.stderr)

    def move(self, t):
        self.x += self.vx * t
        self.y += self.vy * t

    def boost(self, p, thrust):
        ra = self.angle(p)
        self.vx += math.cos(ra) * thrust/self.m
        self.vy += math.sin(ra) * thrust/self.m

    def end(self):
        def tround(float):
            if round(float + 1) - round(float) != 1:
                return round(float + abs(float) / float * 0.5)
            return round(float)

        self.x = tround(self.x)
        self.y = tround(self.y)
        self.vx = tround(self.vx * self.f)
        self.vy = tround(self.vy * self.f)


class Wizard(Unit):
    m = 1
    r = 400
    f = 0.75

    def __init__(self, tid, mid, vx, vy, x, y, state):
        super().__init__(mid, vx, vy, x, y)
        self.tid = tid
        self.state = state
        self.got = None
        self.catchtimer = 0

    def catch(self, u):
        if not self.catchtimer and not self.state:
            u.x = self.x
            u.y = self.y
            u.vx = self.vx
            u.vy = self.vy
            self.state = 1
            self.got = u
            u.caught = self
            self.catchtimer = 3
            return True
        return False

    def throw(self, p, thrust):
        if not self.got:
            return False
        self.got.boost(p, thrust)
        self.got.caught = None
        self.got = None
        self.state = 0
        return True

    def move(self,t):
        super().move(t)
        if self.got:
            self.got.x = self.x
            self.got.y = self.y
            self.got.vx = self.vx
            self.got.vy = self.vy

    def end(self):
        super().end()
        if self.catchtimer == 2 and self.state:
            self.got.caught = None
            self.got = None
            self.state = 0
        if self.catchtimer:
            self.catchtimer -= 1


class Snaffle(Unit):
    m = 0.5
    r = 150
    f = 0.75

    def __init__(self, mid, vx, vy, x, y):
        super().__init__(mid, vx, vy, x, y)
        self.caught = None

    def move(self, t):
        if not self.caught:
            super().move(t)

    def end(self):
        if self.caught:
            self.x = self.caught.x
            self.y = self.caught.y
            self.vx = self.caught.vx
            self.vy = self.caught.vy
        else:
            super().end()


class Bludger(Unit):
    m = 8
    r = 200
    f = 0.9
    thrust = 1000

    def __init__(self, mid, vx, vy, x, y):
        super().__init__(mid, vx, vy, x, y)
        self.last = None


class Pole(Unit):
    r = 300
    m = 99 ** 9
    vx = 0
    vy = 0
    f = 0

    def __init__(self, mid, vx, vy, x, y):
        super().__init__(mid, vx, vy, x, y)


class Line():
    def __init__(self, mid, a, b):
        self.mid = mid
        self.a = a
        self.b = b

    def collision(self,u):
        r = u.r
        if type(self) is Goal and type(u) is Snaffle:
            r = -1
        #vertical line
        if self.a.x == self.b.x:
            if u.x < self.a.x - r < u.x + u.vx or u.x > self.a.x + r > u.x + u.vx:
                t = (abs(u.x - self.a.x) - r) / abs(u.vx)
                y = u.y + t*u.vy
                if self.a.y + u.r < y < self.b.y - u.r:
                    print("Line collision",u.mid, self.mid,":",u.x,u.y,u.vx,u.vy,t,file=sys.stderr)
                    return Collision(self, u, t)
                else:
                    return None
            else:
                return None
        #horisontal line
        if self.a.y == self.b.y:
            if u.y < self.a.y - r < u.y + u.vy or u.y > self.a.y + r > u.y + u.vy:
                t = (abs(u.y - self.a.y) - r) / abs(u.vy)
                x = u.x + t*u.vx
                if self.a.x + u.r < x < self.b.x - u.r:
                    print("Line collision",u.mid, self.mid,":",u.x,u.y,u.vx,u.vy,t,file=sys.stderr)
                    return Collision(self, u, t)
                else:
                    return None
            else:
                return None

    def bounce(self, u):
        # this is gross oversimplification here. as the lines are only vertical or hoisontal
        # vertical line
        #print(u.mid, u.x, u.y, u.vx, u.vy, file=sys.stderr, end="\t")
        if self.a.x == self.b.x:
            if abs(u.x - self.a.x) != u.r:
                print("OFF",self.mid,u.mid,u.x,self.a.x,file=sys.stderr)
            else:
                print("ON:",self.mid,u.mid,u.x,self.a.x,file=sys.stderr)
            u.vx = -u.vx
        # horisontal line
        if self.a.y == self.b.y:
            if abs(u.y - self.a.y) != u.r:
                print("OFF",self.mid,u.mid,u.y,self.a.y,file=sys.stderr)
            else:
                print("ON:",self.mid,u.mid,u.y,self.a.y,file=sys.stderr)
            u.vy = -u.vy
        #print(u.vx, u.vy, file=sys.stderr)


class Goal(Line):
    def __init__(self, mid, a, b):
        super().__init__(mid, a, b)

    def bounce(self, u):
        if type(u) is Snaffle:
            if self.mid == 'gw':
                return 1
            else:
                return 0
        else:
            super().bounce(u)


class Arena:
    el = (
        Pole('nw', 0, 0, 0, 1750),
        Pole('sw', 0, 0, 0, 5750),
        Pole('ne', 0, 0, 16000, 1750),
        Pole('se', 0, 0, 16000, 5750),
        Line('n', Point(0, 0), Point(16000, 0)),
        Line('s', Point(0, 7500), Point(16000, 7500)),
        Line('nw', Point(0, 0), Point(0, 1450)),
        Goal('gw', Point(0, 2050), Point(0, 5450)),
        Line('sw', Point(0, 6050), Point(0, 7500)),
        Line('ne', Point(16000, 0), Point(16000, 1450)),
        Line('se', Point(16000, 6050), Point(16000, 7500)),
        Goal('ge', Point(16000, 2050), Point(16000, 5450))
    )


def delta_angle(alpha, beta):
    phi = abs(beta - alpha) % (2 * math.pi)
    return phi if phi < math.pi else 2 * math.pi - phi


def play(entities):

    eID = range(len(entities))
    # for eid in eID:
    #     S = entities[eid]
    #     print(eid, S.x, S.y, S.vx, S.vy, type(S), sep="\t", file=sys.stderr)
    t = 0.0
    past_collision = {}
    while t < 1.0:
        first_collision = None
        for i in range(len(eID)-1):
            for el in Arena.el:
                col = el.collision(entities[eID[i]])
                if col and col.t == 0.0 and col.b.mid in past_collision and past_collision[col.b.mid] == col.a.mid:
                    continue
                if col and col.t + t < 1.0 and (not first_collision or col.t < first_collision.t):
                    first_collision = col
                    if col.t == 0.0:
                        break
            for j in range(i + 1, len(eID)):
                col = entities[eID[j]].collision(entities[eID[i]])
                if col and col.t == 0.0 and col.b.mid in past_collision and past_collision[col.b.mid] == col.a.mid:
                    continue
                if col and col.t + t < 1.0 and (not first_collision or col.t < first_collision.t):
                    first_collision = col
                    if col.t == 0.0:
                        break
        if not first_collision:
            for eid in eID:
                entities[eid].move(1.0 - t)
            t = 1.0
        else:
            if first_collision.t > 0.0:
                for eid in eID:
                    u = entities[eid]
                    print(u.mid, u.x, u.y, "-->", end=" ", file=sys.stderr)
                    entities[eid].move(first_collision.t)
                    print(u.x, u.y, "[", first_collision.t, "]", file=sys.stderr)
                t += first_collision.t
            past_collision[first_collision.b.mid] = first_collision.a.mid
            if (type(first_collision.a) is Wizard and type(first_collision.b) is Snaffle) or (type(first_collision.b) is Wizard and type(first_collision.a) is Snaffle):
                if type(first_collision.a) is Wizard:
                    if first_collision.a.catch(first_collision.b):
                        print(first_collision.a.mid, "caught",first_collision.b.mid,file=sys.stderr)
                else:
                    if first_collision.b.catch(first_collision.a):
                        print(first_collision.b.mid, "caught",first_collision.a.mid,file=sys.stderr)
            else:
                print("bounce", first_collision.a.mid, first_collision.b.mid, first_collision.t,
                      type(first_collision.a), type(first_collision.b), file=sys.stderr)
                first_collision.a.bounce(first_collision.b)
                if (type(first_collision.a) is Bludger and type(first_collision.b) is Wizard) or (type(first_collision.b) is Bludger and type(first_collision.a) is Wizard):
                    if type(first_collision.a) is Bludger:
                        first_collision.a.last = first_collision.b
                    else:
                        first_collision.b.last = first_collision.a
        print("time in turn:", t, file=sys.stderr)
    for eid in eID:
        entities[eid].end()

# my_team_id = int(input())  # if 0 you need to score on the right of the map, if 1 you need to score on the left
#
# mteam = {}
# oteam = {}
# bludg = {}
# snaff = {}
# entities = {}
#
# # game loop
# while True:
#     sTime = timer()
#     entities = int(input())  # number of entities still in game
#     for i in range(entities):
#         # entity_id: entity identifier
#         # entity_type: "WIZARD", "OPPONENT_WIZARD" or "SNAFFLE" (or "BLUDGER" after first league)
#         # x: position
#         # y: position
#         # vx: velocity
#         # vy: velocity
#         # state: 1 if the wizard is holding a Snaffle, 0 otherwise
#         entity_id, entity_type, x, y, vx, vy, state = input().split()
#         entity_id = int(entity_id)
#         x = int(x)
#         y = int(y)
#         vx = int(vx)
#         vy = int(vy)
#         state = int(state)
#         if entity_type == 'WIZARD':
#             mteam[entity_id] = Wizard(entity_id, vx, vy, x, y, state)
#             entities[entity_id] = mteam[entity_id]
#         if entity_type == 'OPPONENT_WIZARD':
#             oteam[entity_id] = Wizard(entity_id, vx, vy, x, y, state)
#             entities[entity_id] = oteam[entity_id]
#         if entity_type == 'SNAFFLE':
#             snaff[entity_id] = Snaffle(entity_id, vx, vy, x, y)
#             entities[entity_id] = snaff[entity_id]
#         if entity_type == 'BLUDGER':
#             bludg[entity_id] = Bludger(entity_id, vx, vy, x, y)
#             entities[entity_id] = bludg[entity_id]
#
#     eID = sorted(entities)
#     for eid in eID:
#         S = entities[eid]
#         print(eid, S.x, S.y, S.vx, S.vy, type(S), sep="\t", file=sys.stderr)
#     t = 0.0
#     pastCol = {}
#     while t < 1.0:
#         fcol = None
#         for i in range(len(eID)):
#             for j in range(i + 1, len(eID)):
#                 col = entities[eID[i]].collision(entities[eID[j]])
#                 if col and col.t < 0.1 and (col.a.mid, col.b.mid) in pastCol:
#                     continue
#                 if col and col.t + t < 1.0 and (not fcol or col.t < fcol.t):
#                     fcol = col
#         if not fcol:
#             for eid in eID:
#                 entities[eid].move(1.0 - t)
#             t = 1.0
#         else:
#             print("collision", fcol.a.mid, fcol.b.mid, fcol.t, file=sys.stderr)
#             for eid in eID:
#                 entities[eid].move(fcol.t - t)
#             if type(fcol.a) is Wizard and type(fcol.b) is Snaffle:
#                 fcol.a.catch(fcol.b)
#             elif type(fcol.a) is Snaffle and type(fcol.b) is Wizard:
#                 fcol.b.catch(fcol.a)
#             else:
#                 fcol.a.bounce(fcol.b)
#             t += fcol.t
#             pastCol[fcol.a.mid, fcol.b.mid] = t
#         print("time in turn:", t, file=sys.stderr)
#     for eid in eID:
#         entities[eid].end()
#     for eid in sorted(entities):
#         S = entities[eid]
#         print(eid, S.x, S.y, S.vx, S.vy, sep="\t", file=sys.stderr)
#
#     for i in range(2):
#         # Write an action using print
#         # To debug: print("Debug messages...", file=sys.stderr)
#
#
#         # Edit this line to indicate the action for each wizard (0 <= thrust <= 150, 0 <= power <= 500)
#         # i.e.: "MOVE x y thrust" or "THROW x y power"
#         X = str(random.randint(0, 16000))
#         Y = str(random.randint(0, 7500))
#         print("MOVE", X, Y, "100")
#     print("Timing:", round(timer() - sTime, 5), file=sys.stderr)
