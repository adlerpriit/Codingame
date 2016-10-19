import sys
import math
import CodeVsZombies

#this code should be able to run entire CodinGame games.
#idea is to make a base for simulating CodingGame challenge games. Either optimisation tasks like CodeVSZombies or Accountat or VS plays like CodeBusters.
#the exmample here is CodeVSZombies

def loadInit():
    iData = dict()
    return(iData)

def updateRoundData(iData, AgentOutput):
    return()

#iData initial data for a game all the input in the binning of the game (including the beginning of the first round)
iData = loadInit()

while 1:
    rData = getRoundData(iData)
    AgentOutput = botResponse(rData)
    updateRoundData(iData, AgentOutput)
    break
