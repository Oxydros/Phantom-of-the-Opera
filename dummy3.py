#!/usr/bin/env python

from AlphaBeta import runnerSocket
from AlphaBeta import AgentTypes

def lancer():
    runnerSocket.lancer(AgentTypes.PLAYER_TYPE.GHOST)

if __name__ == "__main__":
    lancer()
