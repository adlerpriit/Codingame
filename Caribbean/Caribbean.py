import sys
import math
import random


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


class XY(object):
    offset = [[(+1, 0), (0, -1), (-1, -1), (-1, 0), (-1, +1), (0, +1)],
              [(+1, 0), (+1, -1), (0, -1), (-1, 0), (0, +1), (+1, +1)]]

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
        # find closest point for this point to a line (two points)
        da = b.y - a.y
        db = a.x - b.y
        c1 = da * a.x + db * a.y
        c2 = -db * self.x + da * self.y
        det = da * da + db * db
        if det != 0:
            cx = (da * c1 - db * c2) / det
            cy = (da * c2 + db * c1) / det
        else:
            # the point is already on the line
            cx = self.x
            cy = self.y
        return XY(cx, cy)

    def hex_distance(self, b):
        # print(self, '\n', b, file=sys.stderr)
        return (abs(self.x - b.x)
                + abs(self.x + self.y - b.x - b.y)
                + abs(self.y - b.y)) / 2

    def __str__(self):
        return "%s (x: %d, y: %d)" % (self.__class__.__name__, self.x, self.y)


class Ship(XY):
    def __init__(self, x, y, direction, speed, rum):
        super().__init__(x, y)
        self.direction = direction
        self.speed = speed
        self.rum = rum

    def next_cell(self, n, d=None):
        if d is None:
            d = self.direction
        if self.y % 2 == 0:
            # even row
            return XY(self.x + self.offset[0][d][0] * n,
                      self.y + self.offset[0][d][1] * n)
        else:
            # odd row
            return XY(self.x + self.offset[1][d][0] * n,
                      self.y + self.offset[1][d][1] * n)

    def __str__(self):
        return "%s (x: %d, y: %d) dir: %d speed: %d rum: %d" % (
        self.__class__.__name__, self.x, self.y, self.direction, self.speed, self.rum)


class Barrel(XY):
    def __init__(self, x, y, rum):
        super().__init__(x, y)
        self.rum = rum


class CannonBall(XY):
    def __init__(self, x, y, ship, impact):
        # x and y here represent the target position
        super().__init__(x, y)
        self.ship = ship
        self.impact = impact


class Mine(XY):
    def __init__(self, x, y):
        super().__init__(x, y)


# game loop
while True:
    my_ship_count = int(input())  # the number of remaining ships
    entity_count = int(input())  # the number of entities (e.g. ships, mines or cannonballs)
    barrels = []
    cannon_balls = []
    mines = []
    my_ships = []
    opp_ships = []
    for _ in range(entity_count):
        en_id, en_type, en_x, en_y, arg_1, arg_2, arg_3, arg_4 = input().split()
        if en_type == 'SHIP':
            if arg_4 == '1':
                # my ship
                my_ships.append(Ship(int(en_x), int(en_y), int(arg_1), int(arg_2), int(arg_3)))
            else:
                opp_ships.append(Ship(int(en_x), int(en_y), int(arg_1), int(arg_2), int(arg_3)))
        elif en_type == 'BARREL':
            barrels.append(Barrel(int(en_x), int(en_y), int(arg_1)))
        elif en_type == 'CANNONBALL':
            cannon_balls.append(CannonBall(int(en_x), int(en_y), int(arg_1), int(arg_2)))
        elif en_type == 'MINE':
            mines.append(Mine(int(en_x), int(en_y)))

    for my_ship in my_ships:
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
        target = XY(int(random.random() * 23), int(random.random() * 21))
        action = "MOVE"
        min_dist = 9e9
        for i, barrel in enumerate(barrels):
            # print(i, barrel.distance2(my_ship), file=sys.stderr)
            if barrel.hex_distance(my_ship) < min_dist:
                target = barrel
                min_dist = barrel.hex_distance(my_ship)
        if my_ship.rum > 70 or not barrels:
            for op_ship in opp_ships:
                target = op_ship.next_cell(-5)
        for op_ship in opp_ships:
            # find a cannon solution
            op_dist = op_ship.hex_distance(my_ship.next_cell(1))
            cannon_eta = round(1 + op_dist / 3, 0)
            print(cannon_eta, file=sys.stderr)
            if op_dist <= 10 and cannon_eta <= 3 and (barrels and my_ship.rum > min_dist):
                target = op_ship.next_cell(op_ship.speed * cannon_eta)
                action = "FIRE"
        for mine in mines:
            # print(mine, my_ship, file=sys.stderr)
            mine_on_line = False
            for n in range(3):
                if mine.hex_distance(my_ship.next_cell(1 + n)) == 0:
                    mine_on_line = True
            if mine_on_line:            
                action = "MOVE"
                new_direction = my_ship.direction + 1 if my_ship.direction < 3 else my_ship.direction - 1
                target = my_ship.next_cell(4, new_direction)
        # print(target, barrels[target].distance2(my_ship), file=sys.stderr)
        # Any valid action, such as "WAIT" or "MOVE x y or MINE or FIRE x y"
        if target:
            print("%s %d %d" % (action, target.x, target.y))
        else:
            print("%s %d %d" % (action, target.x, target.y))
