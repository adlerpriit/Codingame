import sys
import math
import copy
from timeit import default_timer as timer
import CodeVsZombies as cvz

#this code should be able to run entire CodinGame games.
#idea is to make a base for simulating CodingGame challenge games. Either optimisation tasks like CodeVSZombies or Accountat or VS plays like CodeBusters.
#the exmample here is CodeVSZombies
def dist(a,b):
    i,j = a
    k,l = b
    return( math.sqrt((i - k)**2 + (j - l)**2) )

def dest(pos_a,pos_b,d):
    d_ab = dist(pos_a,pos_b)
    if d_ab == 0:
        return(pos_a)
    x = int(pos_a[0] - d * (pos_a[0]-pos_b[0])/d_ab)
    y = int(pos_a[1] - d * (pos_a[1]-pos_b[1])/d_ab)
    #print([x,y],file=sys.stderr)
    if x < 0:
        Y = pos_a[1] - (pos_a[1]-y) * pos_a[0]/(pos_a[0]-x)
        x,y = dest(pos_a,pos_b,dist(pos_a,[0,Y]))
    if x > 16000:
        Y = pos_a[1] - (pos_a[1]-y) * (16000-pos_a[0])/(x-pos_a[0])
        x,y = dest(pos_a,pos_b,dist(pos_a,[16000,Y]))
    if y < 0:
        X = pos_a[0] - (pos_a[0]-x) * pos_a[1]/(pos_a[1]-y)
        x,y = dest(pos_a,pos_b,dist(pos_a,[X,0]))
    if y > 9000:
        X = pos_a[0] - (pos_a[0]-x) * (9000-pos_a[1])/(y-pos_a[1])
        x,y = dest(pos_a,pos_b,dist(pos_a,[X,9000]))
    return([x,y])

def loadInit():
    iData = [
    {'me':[0, 0],'hs':{0: [8250, 4500]},'zs':{0: {'next_pos': [8250, 8599], 'pos': [8250, 8999]}},'score':0,'round':1},
    {'me':[5000, 0],'hs':{0: [950, 6000], 1: [8000, 6100]},'zs':{0: {'next_pos': [2737, 6831], 'pos': [3100, 7000]}, 1: {'next_pos': [11115, 6990], 'pos': [11500, 7100]}},'score':0,'round':1},
    {'me':[10999, 0],'hs':{0: [8000, 5500], 1: [4000, 5500]},'zs':{0: {'pos': [1250, 5500], 'next_pos': [1650, 5500]}, 1: {'pos': [15999, 5500], 'next_pos': [15729, 5204]}},'score':0,'round':1},
    {'me':[8000, 2000],'hs':{0: [8000, 4500]},'zs':{0: {'next_pos': [2379, 6373], 'pos': [2000, 6500]}, 1: {'next_pos': [13620, 6373], 'pos': [14000, 6500]}},'score':0,'round':1},
    {'me':[7500, 2000],'hs':{0: [9000, 1200], 1: [400, 6000]},'zs':{0: {'pos': [2000, 1500], 'next_pos': [1865, 1876]}, 1: {'pos': [13900, 6500], 'next_pos': [13628, 6206]}, 2: {'pos': [7000, 7500], 'next_pos': [7036, 7101]}},'score':0,'round':1},
    {'me':[500, 4500],'hs':{0: [100, 4000], 1: [130, 5000], 2: [10, 4500], 3: [500, 3500], 4: [10, 5500], 5: [100, 3000]},'zs':{0: {'next_pos': [7600, 4500], 'pos': [8000, 4500]}, 1: {'next_pos': [8600, 4500], 'pos': [9000, 4500]}, 2: {'next_pos': [9600, 4500], 'pos': [10000, 4500]}, 3: {'next_pos': [10600, 4500], 'pos': [11000, 4500]}, 4: {'next_pos': [11600, 4500], 'pos': [12000, 4500]}, 5: {'next_pos': [12600, 4500], 'pos': [13000, 4500]}, 6: {'next_pos': [13600, 4500], 'pos': [14000, 4500]}, 7: {'next_pos': [14600, 3500], 'pos': [15000, 3500]}, 8: {'next_pos': [14101, 2528], 'pos': [14500, 2500]}, 9: {'next_pos': [15507, 576], 'pos': [15900, 500]}},'score':0,'round':1},
    {'me':[0, 4000],'hs':{0: [0, 1000], 1: [0, 8000]},'zs':{0: {'pos': [5000, 1000], 'next_pos': [4600, 1000]}, 1: {'pos': [5000, 8000], 'next_pos': [4600, 8000]}, 2: {'pos': [7000, 1000], 'next_pos': [6600, 1000]}, 3: {'pos': [7000, 8000], 'next_pos': [6600, 8000]}, 4: {'pos': [9000, 1000], 'next_pos': [8600, 1000]}, 5: {'pos': [9000, 8000], 'next_pos': [8600, 8000]}, 6: {'pos': [11000, 1000], 'next_pos': [10600, 1000]}, 7: {'pos': [11000, 8000], 'next_pos': [10600, 8000]}, 8: {'pos': [13000, 1000], 'next_pos': [12600, 1000]}, 9: {'pos': [13000, 8000], 'next_pos': [12600, 8000]}, 10: {'pos': [14000, 1000], 'next_pos': [13600, 1000]}, 11: {'pos': [14000, 8000], 'next_pos': [13600, 8000]}, 12: {'pos': [14500, 1000], 'next_pos': [14100, 1000]}, 13: {'pos': [14500, 8000], 'next_pos': [14100, 8000]}, 14: {'pos': [15000, 1000], 'next_pos': [14600, 1000]}, 15: {'pos': [15000, 8000], 'next_pos': [14600, 8000]}},'score':0,'round':1},
    {'me':[0, 4000],'hs':{0: [0, 1000], 1: [0, 8000]},'zs':{0: {'pos': [3000, 1000], 'next_pos': [2600, 1000]}, 1: {'pos': [3000, 8000], 'next_pos': [2600, 8000]}, 2: {'pos': [4000, 1000], 'next_pos': [3600, 1000]}, 3: {'pos': [4000, 8000], 'next_pos': [3600, 8000]}, 4: {'pos': [5000, 1000], 'next_pos': [4600, 1000]}, 5: {'pos': [5000, 8000], 'next_pos': [4600, 8000]}, 6: {'pos': [7000, 1000], 'next_pos': [6600, 1000]}, 7: {'pos': [7000, 8000], 'next_pos': [6600, 8000]}, 8: {'pos': [9000, 1000], 'next_pos': [8600, 1000]}, 9: {'pos': [9000, 8000], 'next_pos': [8600, 8000]}, 10: {'pos': [11000, 1000], 'next_pos': [10600, 1000]}, 11: {'pos': [11000, 8000], 'next_pos': [10600, 8000]}, 12: {'pos': [13000, 1000], 'next_pos': [12600, 1000]}, 13: {'pos': [13000, 8000], 'next_pos': [12600, 8000]}, 14: {'pos': [14000, 1000], 'next_pos': [13600, 1000]}, 15: {'pos': [14000, 8000], 'next_pos': [13600, 8000]}, 16: {'pos': [14500, 1000], 'next_pos': [14100, 1000]}, 17: {'pos': [14500, 8000], 'next_pos': [14100, 8000]}, 18: {'pos': [15000, 1000], 'next_pos': [14600, 1000]}, 19: {'pos': [15000, 8000], 'next_pos': [14600, 8000]}},'score':0,'round':1},
    {'me':[8000, 4500],'hs':{0: [4000, 2250], 1: [4000, 6750], 2: [12000, 2250], 3: [12000, 6750]},'zs':{0: {'next_pos': [4000, 2975], 'pos': [4000, 3375]}, 1: {'next_pos': [12000, 2975], 'pos': [12000, 3375]}, 2: {'next_pos': [4000, 4100], 'pos': [4000, 4500]}, 3: {'next_pos': [12000, 4100], 'pos': [12000, 4500]}, 4: {'next_pos': [4000, 6025], 'pos': [4000, 5625]}, 5: {'next_pos': [12000, 6025], 'pos': [12000, 5625]}, 6: {'next_pos': [5600, 2250], 'pos': [6000, 2250]}, 7: {'next_pos': [8000, 2650], 'pos': [8000, 2250]}, 8: {'next_pos': [10400, 2250], 'pos': [10000, 2250]}, 9: {'next_pos': [5600, 6750], 'pos': [6000, 6750]}, 10: {'next_pos': [8000, 6350], 'pos': [8000, 6750]}, 11: {'next_pos': [10400, 6750], 'pos': [10000, 6750]}},'score':0,'round':1},
    {'me':[8000, 0],'hs':{0: [0, 4500], 1: [15999, 4500], 2: [8000, 7999]},'zs':{0: {'pos': [2000, 1200], 'next_pos': [1792, 1542]}, 1: {'pos': [3000, 1800], 'next_pos': [2702, 2067]}, 2: {'pos': [4000, 2400], 'next_pos': [3645, 2585]}, 3: {'pos': [5000, 3000], 'next_pos': [5282, 2717]}, 4: {'pos': [6000, 3600], 'next_pos': [6194, 3250]}, 5: {'pos': [9000, 5400], 'next_pos': [8856, 5773]}, 6: {'pos': [10000, 6000], 'next_pos': [9717, 6282]}, 7: {'pos': [11000, 6600], 'next_pos': [10637, 6769]}, 8: {'pos': [12000, 7200], 'next_pos': [11607, 7278]}, 9: {'pos': [13000, 7800], 'next_pos': [13269, 7503]}, 10: {'pos': [14000, 8400], 'next_pos': [14182, 8044]}, 11: {'pos': [14000, 600], 'next_pos': [14182, 955]}, 12: {'pos': [13000, 1200], 'next_pos': [13269, 1496]}, 13: {'pos': [12000, 1800], 'next_pos': [11635, 1635]}, 14: {'pos': [11000, 2400], 'next_pos': [10687, 2150]}, 15: {'pos': [10000, 3000], 'next_pos': [9778, 2667]}, 16: {'pos': [9000, 3600], 'next_pos': [8892, 3214]}, 17: {'pos': [6000, 5400], 'next_pos': [6243, 5717]}, 18: {'pos': [5000, 6000], 'next_pos': [5332, 6221]}, 19: {'pos': [4000, 6600], 'next_pos': [4377, 6732]}, 20: {'pos': [3000, 7200], 'next_pos': [2702, 6932]}, 21: {'pos': [2000, 7800], 'next_pos': [1792, 7457]}, 22: {'pos': [1000, 8400], 'next_pos': [900, 8012]}},'score':0,'round':1},
    {'me':[9000, 684],'hs':{0: [15999, 4500], 1: [8000, 7999], 2: [0, 4500]},'zs':{0: {'next_pos': [0, 3433], 'pos': [0, 3033]}, 1: {'next_pos': [1239, 5947], 'pos': [1500, 6251]}, 2: {'next_pos': [2667, 2723], 'pos': [3000, 2502]}, 3: {'next_pos': [4869, 6708], 'pos': [4500, 6556]}, 4: {'next_pos': [6272, 3612], 'pos': [6000, 3905]}, 5: {'next_pos': [7577, 5864], 'pos': [7500, 5472]}, 6: {'next_pos': [10217, 1908], 'pos': [10500, 2192]}, 7: {'next_pos': [11623, 6702], 'pos': [12000, 6568]}, 8: {'next_pos': [13758, 7142], 'pos': [13500, 7448]}},'score':0,'round':1},
    {'me':[8000, 4000],'hs':{0: [0, 4000], 1: [15000, 4000]},'zs':{0: {'next_pos': [4676, 2005], 'pos': [4333, 1800]}, 1: {'next_pos': [4730, 3643], 'pos': [4333, 3600]}, 2: {'next_pos': [4706, 5257], 'pos': [4333, 5400]}, 3: {'next_pos': [4634, 6936], 'pos': [4333, 7200]}, 4: {'next_pos': [10357, 2054], 'pos': [10666, 1800]}, 5: {'next_pos': [10270, 3659], 'pos': [10666, 3600]}, 6: {'next_pos': [10311, 5214], 'pos': [10666, 5400]}, 7: {'next_pos': [10409, 6892], 'pos': [10666, 7200]}, 8: {'next_pos': [0, 6800], 'pos': [0, 7200]}},'score':0,'round':1},
    {'me':[4920, 6810],'hs':{0: [50, 4810], 1: [14820, 3870], 2: [10869, 8250], 3: [9695, 7220], 4: [10160, 5600], 5: [12988, 5820], 6: [14892, 5180], 7: [881, 1210], 8: [7258, 2130], 9: [13029, 6990]},'zs':{0: {'next_pos': [10673, 859], 'pos': [11048, 720]}, 1: {'next_pos': [1776, 1519], 'pos': [2155, 1650]}, 2: {'next_pos': [9234, 2707], 'pos': [9618, 2820]}, 3: {'next_pos': [12307, 4140], 'pos': [12157, 3770]}, 4: {'next_pos': [1855, 5113], 'pos': [2250, 5180]}, 5: {'next_pos': [8980, 5057], 'pos': [8617, 4890]}, 6: {'next_pos': [7105, 1352], 'pos': [7028, 960]}, 7: {'next_pos': [1291, 610], 'pos': [1518, 280]}, 8: {'next_pos': [7854, 3705], 'pos': [7996, 4080]}, 9: {'next_pos': [13202, 510], 'pos': [13029, 150]}, 10: {'next_pos': [3371, 4910], 'pos': [3119, 4600]}, 11: {'next_pos': [3543, 4493], 'pos': [3339, 4150]}, 12: {'next_pos': [767, 6960], 'pos': [894, 7340]}, 13: {'next_pos': [7945, 7489], 'pos': [7550, 7550]}},'score':0,'round':1},
    {'me':[8020, 3500],'hs':{0: [11000, 1000], 1: [11000, 6000], 2: [4000, 3500]},'zs':{0: {'next_pos': [14600, 1000], 'pos': [15000, 1000]}, 1: {'next_pos': [14600, 6000], 'pos': [15000, 6000]}, 2: {'next_pos': [520, 3500], 'pos': [120, 3500]}, 3: {'next_pos': [396, 3950], 'pos': [0, 4000]}, 4: {'next_pos': [516, 3051], 'pos': [120, 3000]}},'score':0,'round':1},
    {'me':[3900, 5000],'hs':{0: [3000, 3000], 1: [3000, 5000], 2: [3000, 7000], 3: [12000, 3500]},'zs':{0: {'pos': [10000, 1000], 'next_pos': [10249, 1312]}, 1: {'pos': [10000, 6000], 'next_pos': [10249, 5687]}, 2: {'pos': [15500, 2000], 'next_pos': [15132, 2157]}, 3: {'pos': [15500, 3600], 'next_pos': [15100, 3588]}, 4: {'pos': [15500, 5000], 'next_pos': [15132, 4842]}, 5: {'pos': [0, 1200], 'next_pos': [342, 1405]}},'score':0,'round':1},
    {'me':[3989, 3259],'hs':{0: [302, 6109], 1: [3671, 981], 2: [6863, 809]},'zs':{0: {'next_pos': [597, 248], 'pos': [208, 156]}, 1: {'next_pos': [9729, 722], 'pos': [10129, 711]}, 2: {'next_pos': [12829, 437], 'pos': [13229, 413]}, 3: {'next_pos': [218, 4026], 'pos': [203, 3627]}, 4: {'next_pos': [7252, 3516], 'pos': [7310, 3912]}, 5: {'next_pos': [9504, 2969], 'pos': [9814, 3223]}, 6: {'next_pos': [13188, 3510], 'pos': [13556, 3668]}, 7: {'next_pos': [3931, 5851], 'pos': [3923, 6251]}, 8: {'next_pos': [6465, 6265], 'pos': [6720, 6574]}, 9: {'next_pos': [10166, 5802], 'pos': [10387, 6136]}, 10: {'next_pos': [12791, 5989], 'pos': [13093, 6253]}},'score':0,'round':1},
    {'me':[3989, 3259],'hs':{0: [3647, 384], 1: [60, 3262], 2: [2391, 1601], 3: [2363, 3422]},'zs':{0: {'pos': [6485, 499], 'next_pos': [6085, 482]}, 1: {'pos': [7822, 446], 'next_pos': [7422, 440]}, 2: {'pos': [9202, 826], 'next_pos': [8803, 794]}, 3: {'pos': [11060, 253], 'next_pos': [10660, 260]}, 4: {'pos': [12568, 808], 'next_pos': [12183, 917]}, 5: {'pos': [14148, 650], 'next_pos': [13760, 749]}, 6: {'pos': [6571, 1893], 'next_pos': [6217, 2080]}, 7: {'pos': [8484, 2013], 'next_pos': [8098, 2119]}, 8: {'pos': [9669, 1968], 'next_pos': [9278, 2056]}, 9: {'pos': [7570, 3338], 'next_pos': [7170, 3329]}, 10: {'pos': [9780, 3611], 'next_pos': [9380, 3586]}, 11: {'pos': [8360, 4767], 'next_pos': [7981, 4636]}, 12: {'pos': [9804, 4154], 'next_pos': [9408, 4093]}, 13: {'pos': [10935, 4977], 'next_pos': [10546, 4880]}, 14: {'pos': [12310, 4614], 'next_pos': [11915, 4549]}, 15: {'pos': [13891, 4302], 'next_pos': [13493, 4260]}, 16: {'pos': [913, 5636], 'next_pos': [777, 5259]}, 17: {'pos': [2410, 5912], 'next_pos': [2402, 5512]}, 18: {'pos': [3952, 6143], 'next_pos': [3957, 5743]}, 19: {'pos': [4615, 5995], 'next_pos': [4525, 5605]}, 20: {'pos': [6568, 6085], 'next_pos': [6298, 5789]}, 21: {'pos': [8204, 5579], 'next_pos': [7853, 5386]}, 22: {'pos': [9049, 5470], 'next_pos': [8682, 5309]}, 23: {'pos': [30, 6798], 'next_pos': [33, 6398]}, 24: {'pos': [1798, 6682], 'next_pos': [1866, 6287]}, 25: {'pos': [3247, 7664], 'next_pos': [3165, 7272]}, 26: {'pos': [5005, 7319], 'next_pos': [4907, 6930]}, 27: {'pos': [6415, 7094], 'next_pos': [6201, 6755]}, 28: {'pos': [8159, 7447], 'next_pos': [7876, 7163]}, 29: {'pos': [9550, 6847], 'next_pos': [9213, 6630]}},'score':0,'round':1},
    {'me':[3989, 3259],'hs':{0: [647, 384], 1: [60, 1262], 2: [1391, 1601], 3: [1363, 422], 4: [15470, 384], 5: [15060, 1262], 6: [11391, 1601], 7: [11363, 422]},'zs':{0: {'next_pos': [8299, 1581], 'pos': [7900, 1579]}, 1: {'next_pos': [8883, 2354], 'pos': [8500, 2470]}, 2: {'next_pos': [7104, 3737], 'pos': [7500, 3798]}, 3: {'next_pos': [6151, 4484], 'pos': [6500, 4682]}, 4: {'next_pos': [9202, 5319], 'pos': [9000, 5664]}, 5: {'next_pos': [7198, 6056], 'pos': [7500, 6319]}, 6: {'next_pos': [8195, 6834], 'pos': [8500, 7094]}, 7: {'next_pos': [7563, 8124], 'pos': [7800, 8447]}, 8: {'next_pos': [7862, 8524], 'pos': [8100, 8847]}, 9: {'next_pos': [291, 6726], 'pos': [0, 7000]}, 10: {'next_pos': [1216, 7563], 'pos': [1000, 7900]}, 11: {'next_pos': [3074, 8106], 'pos': [3000, 8500]}, 12: {'next_pos': [4907, 7110], 'pos': [5000, 7500]}, 13: {'next_pos': [6727, 6206], 'pos': [7000, 6500]}, 14: {'next_pos': [9161, 6634], 'pos': [9000, 7000]}, 15: {'next_pos': [11026, 7100], 'pos': [11000, 7500]}, 16: {'next_pos': [12909, 8110], 'pos': [13000, 8500]}, 17: {'next_pos': [15003, 7400], 'pos': [15000, 7800]}},'score':0,'round':1},
    {'me':[8000, 4500],'hs':{0: [3000, 4500], 1: [14000, 4500]},'zs':{0: {'next_pos': [2900, 4500], 'pos': [2500, 4500]}, 1: {'next_pos': [15260, 6180], 'pos': [15500, 6500]}},'score':0,'round':1},
    {'me':[0, 4500],'hs':{0: [7000, 3500], 1: [0, 500], 2: [7000, 5500], 3: [3500, 1000], 4: [9250, 8000], 5: [13000, 4500]},'zs':{0: {'pos': [3600, 3500], 'next_pos': [3584, 3100]}, 1: {'pos': [3700, 4500], 'next_pos': [4082, 4383]}, 2: {'pos': [3400, 6500], 'next_pos': [3785, 6392]}, 3: {'pos': [9000, 3500], 'next_pos': [8600, 3500]}, 4: {'pos': [8990, 4500], 'next_pos': [8632, 4320]}, 5: {'pos': [9000, 5500], 'next_pos': [8600, 5500]}, 6: {'pos': [11000, 4000], 'next_pos': [11388, 4097]}, 7: {'pos': [9100, 10], 'next_pos': [8893, 352]}},'score':0,'round':1},
    {'me':[7992, 8304],'hs':{0: [757, 3545], 1: [510, 8170], 2: [1119, 733], 3: [1416, 7409], 4: [1110, 8488], 5: [2118, 1983], 6: [3167, 480], 7: [6576, 664], 8: [8704, 1276], 9: [13340, 5663], 10: [13808, 4731], 11: [15355, 3528], 12: [15495, 5035], 13: [15182, 6184], 14: [15564, 7640]},'zs':{0: {'next_pos': [3734, 3849], 'pos': [3996, 4152]}, 1: {'next_pos': [3776, 4509], 'pos': [3996, 4844]}, 2: {'next_pos': [3597, 7580], 'pos': [3996, 7612]}, 3: {'next_pos': [5674, 1184], 'pos': [5328, 1384]}, 4: {'next_pos': [8115, 3079], 'pos': [7992, 3460]}, 5: {'next_pos': [11721, 5561], 'pos': [11322, 5536]}, 6: {'next_pos': [11564, 7986], 'pos': [11322, 8304]}},'score':0,'round':1}
    ]
    return(iData)

def getRoundData(iData):
    rData = copy.deepcopy(iData)
    return(rData)

def updateRoundData(iData, AgentOutput):
    print(iData['round'], iData['score'],AgentOutput,file=sys.stderr)
    #print(AgentOutput,file=sys.stderr)
    #print(iData['me'],file=sys.stderr)
    #print(len(iData['hs']),iData['hs'],file=sys.stderr)
    #print(len(iData['zs']),iData['zs'],file=sys.stderr)

    #ash move max 1000 or onto coordinates
    #all zombies at the end of round will be shot
    #zombies move max 400 or onto human coordinates

    #2. ash moves
    meTarget = [int(i) for i in AgentOutput.split()]
    if dist(meTarget,iData['me']) <= 1000:
        iData['me'] = meTarget
    else:
        iData['me'] = dest(iData['me'],meTarget,1000)
    #1. zombies move
    for zid in iData['zs']:
        z = iData['zs'][zid]
        z['pos'] = z['next_pos']
        chId = sorted(iData['hs'], key=lambda h: dist(iData['hs'][h],z['pos']))[0]
        zTarget = iData['hs'][chId]
        if dist(zTarget,z['pos']) <= 400:
            z['next_pos'] = zTarget
        else:
            if dist(z['pos'],zTarget) <= dist(z['pos'],iData['me']):
                z['next_pos'] = dest(z['pos'],zTarget,400)
            else:
                z['next_pos'] = dest(z['pos'],iData['me'],400)
    #3. ash shoots zomebies within range
    f1,f2 = 0,1
    zKilled = []
    for zid in sorted(iData['zs']):
        if dist(iData['me'],iData['zs'][zid]['pos']) <= 2000:
            zKilled.append(zid)
            del(iData['zs'][zid])
            iData['score']+= (len(iData['hs'])**2 * 10 * (f1+f2))
            f1,f2 = f2,f1+f2
    if zKilled:
        print("Zombies killed:",zKilled,file=sys.stderr)
    #4. zomebies eat humans they share coordinates with.
    hKilled = []
    for zid in sorted(iData['zs']):
        for hid in sorted(iData['hs']):
            if iData['zs'][zid]['pos'] == iData['hs'][hid]:
                hKilled.append(hid)
                del(iData['hs'][hid])
    if hKilled:
        print("Humans eaten:",hKilled,file=sys.stderr)
    # score: (nrHumans**2 * 10) * (n + 2) - nth zombie has the multipier of nth number in fibonnacci sequence (starting from 0: 0 1 1 2 3 5 8 13 21)
    if not iData['hs']:
        print("GAME OVER: You failed -- 0 points")
        iData['score'] = 0
        return(False)
    if not iData['zs']:
        print("GAME OVER: You scored\t",iData['score'],"\tpoints")
        return(False)
    iData['round']+=1
    return(True)

for s in range(5):
    for mz in range(5):
        for zh in range(10):
            iData = loadInit()
            CumSum = 0
            for gData in iData:
                #iData initial data for a game all the input in the binning of the game (including the beginning of the first round)
                while 1:
                    rData = getRoundData(gData)
                    rData['s'] = s
                    rData['mz'] = mz
                    rData['zh'] = zh
                    sTime = timer()
                    AgentOutput = cvz.botResponse(rData)
                    print("timing:",round(timer()-sTime,3),file=sys.stderr)
                    Status = updateRoundData(gData, AgentOutput)
                    if not Status:
                        break
                CumSum += gData['score']
                if gData['score'] == 0:
                    CumSum = 0
                    break
                    #pass
            print("Used params:",s,mz,zh,CumSum)
