import sys
import math
from collections import defaultdict
from random import random


class Entity(object):
    def __init__(self, eid, owner):
        self.eid = eid
        self.owner = owner


class Factory(Entity):
    def __init__(self, eid, owner, cyborgs, production, arg4, arg5):
        super().__init__(eid, owner)
        self.cyborgs = cyborgs
        self.production = production


class Troop(Entity):
    def __init__(self, eid, owner, factory_from, factory_to, size, eta):
        super().__init__(eid, owner)
        self.factory_from = factory_from
        self.factory_to = factory_to
        self.size = size
        self.eta = eta


def assess_factory_1(f1):
    f1_troops_delta = sum([t.size for t in troops if t.owner != 1 and t.factory_to == f1.eid]) - \
                      sum([t.size for t in troops if t.owner == 1 and t.factory_to == f1.eid])
    for f2 in sorted(factor, key=lambda k: k.production * 10 / distances[f1.eid][k.eid]):
        f2_troops_delta = sum([t.size for t in troops if t.owner != 1 and t.factory_to == f2.eid]) - \
                          sum([t.size for t in troops if t.owner == 1 and t.factory_to == f2.eid])
        if f1 != f2 and f2.owner != 1:
            if (f2.cyborgs + f2_troops_delta < f1.cyborgs - f1_troops_delta
                and f2.production > 0
                and f1.cyborgs > 10
                and f2.cyborgs > f2_troops_delta
                and f1.cyborgs > f1_troops_delta):
                print(f1.cyborgs, f2.cyborgs, file=sys.stderr)
                f1_cyborgs_send = f1.cyborgs - f1_troops_delta - 1
                f1.cyborgs -= f1_cyborgs_send
                return ' '.join(["MOVE", str(f1.eid), str(f2.eid), str(f1_cyborgs_send)])
        elif f2.owner == 1 and f2_troops_delta < 0 < f1_troops_delta:
            f1_cyborgs_send = -f2_troops_delta + 1
            f1.cyborgs -= f1_cyborgs_send
            return ' '.join(["MOVE", str(f1.eid), str(f2.eid), str(f1_cyborgs_send)])
    return None


def get_dests(f1, factor):
    dests = []
    for f in factor:
        if f == f1 or f.eid not in distances[f1.eid]:
            continue
        for _ in range((f.production * f.production * (3 - f.owner)) +
                        int(len(distances[f.eid]) / 4) + int(3 / distances[f1.eid][f.eid])):
            dests.append(f.eid)
    return dests


def assess_factory_2(f1):
    dests = get_dests(f1, factor)
    if not dests:
        return None
    send_to = dests[int(random()*len(dests))]
    f2 = [f for f in factor if f.eid == send_to][0]
    if f2.owner == -1 and f2.production > 1 and f2.cyborgs > 10 and bomb_count[0] < 2:
        bomb_count[0] += 1
        return ' '.join(str(s) for s in ["BOMB", f1.eid, send_to])
    if f2.owner == 0 and f1.cyborgs > f2.cyborgs + 1:
        return ' '.join(str(s) for s in ["MOVE", f1.eid, send_to, f2.cyborgs + 1])
    if f1.production > 0 and f1.cyborgs > f2.production:
        # send out all produced cyborgs to random target
        return ' '.join(str(s) for s in ["MOVE", f1.eid, send_to, f2.production + int(f1.cyborgs/10)])
    if f1.production == 0:
        return ' '.join(str(s) for s in ["MOVE", f1.eid, send_to, f1.cyborgs])
    return None

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


factory_count = int(input())  # the number of factories
link_count = int(input())  # the number of links between factories
distances = defaultdict(dict)
for _ in range(link_count):
    factory_1, factory_2, distance = [int(j) for j in input().split()]
    distances[factory_1][factory_2] = distance
    distances[factory_2][factory_1] = distance
    print(factory_1, factory_2, distance, file=sys.stderr)

# game loop
bomb_count = [0]
while True:
    factor = []
    troops = []
    entity_count = int(input())  # the number of entities (e.g. factories and troops)
    for _ in range(entity_count):
        eid, etype, arg_1, arg_2, arg_3, arg_4, arg_5 = input().split()
        if etype == 'FACTORY':
            factor.append(Factory(int(eid), int(arg_1), int(arg_2), int(arg_3), int(arg_4), int(arg_5)))
        if etype == 'TROOP':
            troops.append(Troop(int(eid), int(arg_1), int(arg_2), int(arg_3), int(arg_4), int(arg_5)))

    orders = []
    for f1 in factor:
        if f1.owner == 1:
            order = assess_factory_2(f1)
            if order:
                orders.append(order)
            # osort = sorted(order, key=lambda k: order[k]['value'] + order[k]['cost'])
            # print([(fid, order[fid]) for fid in osort], file=sys.stderr)
            # print("MOVE", f1.eid, osort[0],  f1.cyborgs + order[osort[0]]['cost'])
    if orders:
        print('; '.join(orders))
    else:
        print('WAIT')
