import logging
import sys
from AlphaBetaDetective import AlphaBetaDetective
from AlphaBetaFantome import AlphaBetaFantome
from Parsing import PLAYER_TYPE

class GameAgent():

    actualTuile = None
    actualColor = None
    actualPos = None
    selectedPos = 0
    powerQ = 0
    selectedPower = [0, 0]
    world = None
    agentType = None

    def __init__(self, world, agentType):
        self.world = world
        self.agentType = agentType

    def bluePower(self, node, data) :
        if (data.find("bloquer") != - 1) :
            return (str(node.power[0]))
        return (str(node.power[1]))

    def violetPower(self, node) :
        return node.power

    def greyPower(self, node) :
        return(node.power)

    def getAgentType(self):
        return self.agentType

    ## Return the best tuile selection
    def selectTuile(self, root):
        logging.info("[IA] Trying to find best tuile")
        if (self.agentType != PLAYER_TYPE.DETECTIVE) :
            alphaB = AlphaBetaFantome(root)
        else :
            alphaB = AlphaBetaDetective(root)
        node = alphaB.alpha_beta_search(root);
        nbAnswer = node.parent.color.index(node.sColor)
        return str(nbAnswer), node 

    ## Return the best next pos
    def nextPos(self, root):
        if (self.agentType != PLAYER_TYPE.DETECTIVE) :
            alphaB = AlphaBetaFantome(root)
        else :
            alphaB = AlphaBetaDetective(root)
        node = alphaB.alpha_beta_search(root)
        if (node.move == '') :
            node = alphaB.alpha_beta_search(root)
        logging.info("[IA] selected POSITION %s"%(node.move))
        return str(node.move), node

    ## Return the best power choice
    def powerChoice(self, root):
        if (self.agentType != PLAYER_TYPE.DETECTIVE) :
            alphaB = AlphaBetaFantome(root)
        else :
            alphaB = AlphaBetaDetective(root)
        alphaB = AlphaBetaDetective(root)
        node = alphaB.alpha_beta_search(root)
        if (node.used == True and node.parent.used == False) :
            return str(1), node
        return str(0), node