import logging
import sys

class GameAgent():
    world = None
    agentType = None

    def __init__(self, world, agentType):
        self.world = world
        self.agentType = agentType

    def getAgentType(self):
        return self.agentType

    ## Return the best tuile selection
    def selectTuile(self, tuiles):
        logging.info("[IA] Trying to find best tuile")

        # IA HERE
        # MUST SET selectedPower and selectedPos
        # MUST RET TUILE COLOR

        return (str(0), tuiles[0]['color'])

    ## Return the best next pos
    def nextPos(self, available_pos):
        logging.info("[IA] selected POSITION %s"%(0))
        return str(0)

    ## Return the best power choice
    def powerChoice(self):
        logging.info("[IA] Use power %d"%(0))
        return str(0)

    def rewardAgent(self):
        pass