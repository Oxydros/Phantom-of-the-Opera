#!/usr/bin/env python

from qlearning import runnerSocket
from qlearning import AgentTypes

def lancer():
    runnerSocket.lancer(AgentTypes.PLAYER_TYPE.DETECTIVE, smart = True, training = False)

if __name__ == "__main__":
    lancer()