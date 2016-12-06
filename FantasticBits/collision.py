import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance2(self, p):
        return (self.x - p.x) * (self.x - p.x) + (self.y - p.y) * (self.y - p.y)

    def distance(self, p):
        return math.sqrt(self.distance2(p))

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
    def __init__(self, myid, r, m, vx, vy, x, y):
        super().__init__(x, y)
        self.id = myid
        self.r = r
        self.m = m
        self.vx = vx
        self.vy = vy

    def collision(self, u):
        # square of the distance
        dist = self.distance2(u)
        # sum of radii squared
        sr = (self.r + u.r) * (self.r + u.r)
        if dist < sr:
            return Collision(self, u, 0)
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

    def move(self, t):
        self.x += self.vx * t
        self.y += self.vy * t

    def end(self, f):
        def tround(float):
            if round(float + 1) - round(float) != 1:
                return round(float + abs(float) / float * 0.5)
            return round(float)

        self.x = tround(self.x)
        self.y = tround(self.y)
        self.vx = tround(self.vx * f)
        self.vy = tround(self.vy * f)
