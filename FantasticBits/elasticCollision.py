import sys
# import math
import random
import FantaticBitsOOP as oop
# import turtle
from timeit import default_timer as timer


def end(sTime, score):
    elapsedTime = round(timer() - sTime, 4)
    avgTime = round(elapsedTime / N, 4)
    print("Score:",score,"\tTime:", elapsedTime, "( average per turn:", avgTime, ")")


wizards = []
snaffles = []
bludgers = []

TeamID = random.randint(0,1)


wizards.append(oop.Wizard(0,'0',0,0,1000,2250,0))
wizards.append(oop.Wizard(0,'1',0,0,1000,5250,0))
wizards.append(oop.Wizard(1,'2',0,0,15000,2250,0))
wizards.append(oop.Wizard(1,'3',0,0,15000,5250,0))
snaffles.append(oop.Snaffle('4',0,0,8000,3750))
I = 5
for i in range(random.choice([4,6])):
    if i % 2 == 0:
        x,y = random.randint(1500,6500),random.randint(500,3500)
    else:
        x,y = -x,-y
    snaffles.append(oop.Snaffle(str(I),0,0,x+8000,y+3750))
    I+=1
bludgers.append(oop.Bludger(str(I),0,0,7450,3750))
bludgers.append(oop.Bludger(str(I+1),0,0,8550,3750))

units = []
for w in wizards:
    units.append(w)
for s in snaffles:
    units.append(s)
for b in bludgers:
    units.append(b)

sTime = timer()
N = 200
for i in range(N):
    for u in units:
        print(u.mid, u.x, u.y, u.vx, u.vy, sep="\t", file=sys.stderr)
    for w in wizards:
        dist = 9**9
        T = None
        if w.state:
            if w.tid == 0:
                T = oop.Point(16000,3750)
            else:
                T = oop.Point(0,3750)
            print(w.mid, "THROW", T.x, T.y,file=sys.stderr)
            w.throw(T,500)
        else:
            score = 0
            remain = 0
            for s in snaffles:
                if not s.mid:
                    if s.x == -1000:
                        score -= 1
                    else:
                        score += 1
                else:
                    remain += 1
                    if s.distance2(w) < dist:
                        dist = s.distance2(w)
                        T = oop.Point(s.x,s.y)
            if not T or abs(score) > remain:
                end(sTime,score)
                exit(15)
            print(w.mid, "MOVE", T.x, T.y,file=sys.stderr)
            w.boost(T,150)
    for b in bludgers:
        dist = 9**9
        T = None
        for w in wizards:
            if b.distance2(w) < dist and (not b.last or w.mid != b.last.mid):
                dist = b.distance2(w)
                T = w
        b.boost(oop.Point(T.x,T.y),1000)
    oop.play(units)
end(sTime,score)

#mycollision = C.collision(A)
#print(mycollision.t)
#A.move(mycollision.t)
#B.move(mycollision.t)
#C.bounce(A)
#A.move(1.0 - mycollision.t)
#B.move(1.0 - mycollision.t)
#A.end()
#B.end()
#print(A.__dict__)
#print(B.__dict__)
#print(C.__dict__)