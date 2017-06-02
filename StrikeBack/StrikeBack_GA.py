import numpy as np
import timeit


class Point(object):
    def __init__(self, c):
        assert isinstance(c, list)
        self.c = np.array(c)

    def distance2(self, p):
        return self.c.dot(p.c)

    def distance(self, p):
        return np.sqrt(self.distance2(p))


class Unit(Point):
    def __init__(self, c, sv, a, ncpid):
        super().__init__(c)
        self.sv = np.array(sv)
        self.a = a
        self.ncpid = ncpid

    @property
    def speed(self):
        return np.sqrt(self.speed2)

    @property
    def speed2(self):
        return self.sv.dot(self.sv)

    @property
    def zero(self, tolerance=1e-10):
        return self.speed2 <= tolerance

    @property
    def normalise(self):
        if self.zero:
            return self.sv
        else:
            return self.sv / self.speed

    def angle(self, u, deg=False):
        if deg:
            return np.degrees(np.arccos(np.clip(np.dot(self.normalise, u.normalise), -1.0, 1.0)))
        else:
            return np.arccos(np.clip(np.dot(self.normalise, u.normalise), -1.0, 1.0))

    def move(self, t):
        self.c += self.sv * t