#!/usr/bin/env python

from AlphaBeta import runner
from AlphaBeta import AgentTypes

def lancer():
    runner.lancer(AgentTypes.PLAYER_TYPE.DETECTIVE)

if __name__ == "__main__":
    lancer()