import sys
# import math
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

    def troop_delta(self, local_troops):
        owner = self.owner
        cyborgs = self.cyborgs if self.owner == 1 else -self.cyborgs
        balance = [cyborgs]
        targeting_factory = [t for t in local_troops if t.factory_to == self.eid]
        for i in range(20):
            for t in targeting_factory:
                if t.eta == i + 1:
                    if t.owner == 1:
                        cyborgs += t.size
                    else:
                        cyborgs -= t.size
            if cyborgs < 0 and owner != 0:
                owner = -1
                cyborgs -= self.production
            if cyborgs > 0:
                owner = 1
                cyborgs += self.production
            balance.append(cyborgs)
        return balance


class Troop(Entity):
    def __init__(self, eid, owner, factory_from, factory_to, size, eta):
        super().__init__(eid, owner)
        self.factory_from = factory_from
        self.factory_to = factory_to
        self.size = size
        self.eta = eta


class Bomb(Entity):
    def __init__(self, eid, owner, factory_from, factory_to, eta, arg5):
        super().__init__(eid, owner)
        self.factory_from = factory_from
        self.factory_to = factory_to
        self.eta = eta


def nr_opp_factory_links(f):
    return len([1 for f2 in factor if f2.eid in distances[f.eid] and f2.owner == -1])


def get_dests(f1):
    dests = []
    for f in factor:
        if f == f1 or f.eid not in distances[f1.eid]:
            continue
        f_links = nr_opp_factory_links(f)
        balance = f.troop_delta(troops)
        delta = balance[-1]
        if delta < 0:
            delta = 2
        else:
            delta = 0
        for _ in range((f.production * (3 - f.owner) * delta * int(4 / distances[f1.eid][f.eid])) + int(f_links/2) + delta):
            dests.append(f.eid)
    return dests


def order_dests(f1):
    dests = {}
    for f in factor:
        if f == f1 or f.eid not in distances[f1.eid]:
            continue
        f_links = nr_opp_factory_links(f)
        balance = f.troop_delta(troops)
        delta = balance[distances[f1.eid][f.eid]]
        if delta < 0:
            delta = 2
        else:
            delta = 0
        dests[f.eid] = f.production * (3 - f.owner) * delta + int(f_links/2) + delta
    return sorted(sorted(dests, key=lambda k:dests[k], reverse=True), key=lambda k: distances[f1.eid][k])


def assess_factory_2(f1):
    dests = get_dests(f1)
    if not dests:
        return None
    send_to = dests[int(random()*len(dests))]
    f2 = [f for f in factor if f.eid == send_to][0]
    dist = distances[f1.eid][f2.eid]
    f1_balance = f1.troop_delta(troops)
    f2_balance = f2.troop_delta(troops)
    print(f2_balance, file=sys.stderr)

    if (f2.production > 2 and bomb_count[0] < 2 and dist < 10 and f2.owner != 0
        and f2_balance[dist - 1] < -5 and f2.eid not in [b.factory_to for b in bombs]):
        bomb_count[0] += 1
        bombs.append(Bomb(1, 1, f1.eid, f2.eid, dist, -1))
        return ' '.join(str(s) for s in ["BOMB", f1.eid, send_to])

    if f2.owner == 0 and f1.cyborgs > -f2_balance[dist] and f2_balance[dist] < 0:
        f1.cyborgs -= (f2.cyborgs + 1)
        return ' '.join(str(s) for s in ["MOVE", f1.eid, send_to, f2.cyborgs + 1])

    if f1_balance:
        if f1_balance[1] < 0:
            return None
        if f1_balance[5] > 10 and f1.production < 2:
            return ' '.join(str(s) for s in ["INC", f1.eid])
        if f1_balance[5] > 20 and f1.production < 3:
            return ' '.join(str(s) for s in ["INC", f1.eid])

    for t, balance in enumerate(f2_balance):
        if balance < 0 and f1.cyborgs > -balance and dist <= t + 1:
            f1.cyborgs -= (1 - balance)
            return ' '.join(str(s) for s in ["MOVE", f1.eid, send_to, 1 - balance])

    if f1.production > 0 and f1.cyborgs > 3 * f2.production and f2.owner != 0:
        send = 3 * f2.production + int(f1.cyborgs/10)
        f1.cyborgs -= send if send < f1.cyborgs else f1.cyborgs
        return ' '.join(str(s) for s in ["MOVE", f1.eid, send_to, send])

    if f1.production > 0 and f1.cyborgs > 2 * f2.production and f2.owner != 0:
        send = 2 * f2.production + int(f1.cyborgs/10)
        f1.cyborgs -= send if send < f1.cyborgs else f1.cyborgs
        return ' '.join(str(s) for s in ["MOVE", f1.eid, send_to, send])

    if f1.production > 0 and f1.cyborgs > f2.production and f2.owner != 0:
        send = f2.production + int(f1.cyborgs/10)
        f1.cyborgs -= send if send < f1.cyborgs else f1.cyborgs
        return ' '.join(str(s) for s in ["MOVE", f1.eid, send_to, send])

    return None


def assess_factory_3(f1):
    dests = order_dests(f1)
    for b in bombs:
        if b.eid in bomb_eta and f1.eid in distances[b.factory_from]:
            # print(bomb_eta[b.eid], distances[b.factory_from][f1.eid], file=sys.stderr)
            if bomb_eta[b.eid] == distances[b.factory_from][f1.eid]:
                send = f1.cyborgs + f1.production
                f1.cyborgs = 0
                troops.append(Troop(-1, 1, f1.eid, dests[0], send, distances[b.factory_from][f1.eid]))
                return [' '.join(str(s) for s in ["MOVE", f1.eid, dests[0], send])]
    commands = []
    for dest in dests:
        f2 = [f for f in factor if f.eid == dest][0]
        dist = distances[f1.eid][f2.eid]
        f1_balance = f1.troop_delta(troops)
        f2_balance = f2.troop_delta(troops)
        # print(f1.eid, f2.eid, f2_balance, file=sys.stderr)

        if (f2.production > 1 and 2 > bomb_count[0] and dist < 10 and f2.owner != 0
            and f2_balance[dist] < 0 and f2.eid not in [b.factory_to for b in bombs]):
            bomb_count[0] += 1
            bombs.append(Bomb(1, 1, f1.eid, f2.eid, dist, -1))
            commands.append(' '.join(str(s) for s in ["BOMB", f1.eid, dest]))

        if f1_balance[1] < 0:
            return []
        if f1_balance[0] >= 10 and f1.production < 3:
            f1.cyborgs -= 10
            commands.append(' '.join(str(s) for s in ["INC", f1.eid]))

        if f2.owner == 0 and f2_balance[dist] <= 0:
            if f2.production > 0 and f1.cyborgs > int((1 - f2_balance[dist])/2):
                f1.cyborgs -= int((1 - f2_balance[dist])/2)
                troops.append(Troop(-1, 1, f1.eid, dest, int((1 - f2_balance[dist])/2), dist))
                commands.append(' '.join(str(s) for s in ["MOVE", f1.eid, dest, int((1 - f2_balance[dist])/2)]))
            if f2.production == 0 and f1.cyborgs > 10 - f2_balance[dist]:
                f1.cyborgs -= (10 - f2_balance[dist])
                troops.append(Troop(-1, 1, f1.eid, dest, 10 - f2_balance[dist], dist))
                commands.append(' '.join(str(s) for s in ["MOVE", f1.eid, dest, 10 - f2_balance[dist]]))

        for t, balance in enumerate(f2_balance):
            if balance < 0 and f1.cyborgs > -balance and dist <= t + 1:
                f1.cyborgs -= (1 - balance)
                troops.append(Troop(-1, 1, f1.eid, dest, 1 - balance, dist))
                commands.append(' '.join(str(s) for s in ["MOVE", f1.eid, dest, 1 - balance]))
        
        if (f2.production < 2 and f1.production == 3 and
                    f1.cyborgs > 10 - f2_balance[dist] and 10 > f2_balance[dist] > 0):
            f1.cyborgs -= (10 - f2_balance[dist])
            troops.append(Troop(-1, 1, f1.eid, dest, 10 - f2_balance[dist], dist))
            commands.append(' '.join(str(s) for s in ["MOVE", f1.eid, dest, 10 - f2_balance[dist]]))

    return commands

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
bomb_eta = defaultdict(int)
while True:
    factor = []
    troops = []
    bombs = []
    entity_count = int(input())  # the number of entities (e.g. factories and troops)
    for _ in range(entity_count):
        eid, etype, arg_1, arg_2, arg_3, arg_4, arg_5 = input().split()
        if etype == 'FACTORY':
            factor.append(Factory(int(eid), int(arg_1), int(arg_2), int(arg_3), int(arg_4), int(arg_5)))
        if etype == 'TROOP':
            troops.append(Troop(int(eid), int(arg_1), int(arg_2), int(arg_3), int(arg_4), int(arg_5)))
        if etype == 'BOMB':
            bombs.append(Bomb(int(eid), int(arg_1), int(arg_2), int(arg_3), int(arg_4), int(arg_5)))

    for bomb in [b for b in bombs if b.owner == -1]:
        bomb_eta[bomb.eid] += 1
    for b in list(bomb_eta):
        if not [bomb for bomb in bombs if bomb.eid == b]:
            del bomb_eta[b]
    # print(bomb_eta, file=sys.stderr)
    orders = []
    for f1 in sorted(factor, key=lambda k: k.troop_delta(troops)[5], reverse=True):
        if f1.owner == 1:
            order = assess_factory_3(f1)
            if order:
                orders.extend(order)
            # osort = sorted(order, key=lambda k: order[k]['value'] + order[k]['cost'])
            # print([(fid, order[fid]) for fid in osort], file=sys.stderr)
            # print("MOVE", f1.eid, osort[0],  f1.cyborgs + order[osort[0]]['cost'])
    if orders:
        print('; '.join(orders))
    else:
        print('WAIT')
