import sys
#import os
#import math
#from collections import deque

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

l, c, n = [int(i) for i in input().split()]
print([l,c,n],file=sys.stderr)
g = map(int,sys.stdin.readlines())
#print(g,file=sys.stderr)
#for i in range(n):
#     g.append(int(input()))
g = list(g)
qp = sum(g)
print(str(len(g)) + ':' + str(qp),file=sys.stderr)

# Write an action using print
# To debug: print("Debug messages...", file=sys.stderr)


d = 0

i = 0

rC = {}

for j in range(c):
    rc = 0
    ri = 0
    while ri < n and rc+g[i] <= l:
        rc+=g[i]
        ri+=1
        i+=1
        if i==len(g):
            i=0
    d+=rc
    if i in rC:
        rC[i]+=1
    else:
        rC[i]=1
    if j%1000==0:
        j2 = 0
        for k in sorted(rC,key=rC.get,reverse=True):
            if j2 >= 10:
                break
            print(str(k) + ':' + str(rC[k]),file=sys.stderr)
            j2+=1


print(str(d))