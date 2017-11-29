import sys
import math
from collections import defaultdict


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


def assess_factory(f1):
    f1_troops_delta = sum([t.size for t in troops if t.owner != 1 and t.factory_to == f1.eid]) - \
                      sum([t.size for t in troops if t.owner == 1 and t.factory_to == f1.eid])
    for f2 in factor:
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


# def assess_factory(f1):
#     score = defaultdict(dict)
#     for f2 in factor:
#         if f2 == f1 or f2.eid == 1:
#             continue
#         average_dist = sum([distances[f2.eid][mid] for mid in distances[f2.eid]]) / len(distances[f2.eid])
#         score[f2.eid]['value'] = int(f2.production * 200 / average_dist)
#         score[f2.eid]['cost'] = f2.production * distances[f1.eid][f2.eid] + f2.cyborgs + \
#                                sum([t.size for t in troops if t.owner != 1]) - \
#                                sum([t.size for t in troops if t.owner == 1])
#         score[f2.eid]['cost'] -= (f1.cyborgs - 1)
#
#     return score

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


factory_count = int(input())  # the number of factories
link_count = int(input())  # the number of links between factories
distances = defaultdict(dict)
for _ in range(link_count):
    factory_1, factory_2, distance = [int(j) for j in input().split()]
    distances[factory_1][factory_2] = distance

# game loop
game_turn = 0
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
            order = assess_factory(f1)
            if order:
                orders.append(order)
            # osort = sorted(order, key=lambda k: order[k]['value'] + order[k]['cost'])
            # print([(fid, order[fid]) for fid in osort], file=sys.stderr)
            # print("MOVE", f1.eid, osort[0],  f1.cyborgs + order[osort[0]]['cost'])
    if orders and game_turn > 0:
        print('; '.join(orders))
    else:
        print('WAIT')
    game_turn += 1