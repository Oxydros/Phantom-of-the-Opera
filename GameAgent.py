import logging
import sys
from DQNLearning import DQNAgent
from AgentTypes import QUESTION_TYPE, PLAYER_TYPE
from World import COLOR_INTEG, INTEG_COLOR

def extractColorSelection(tensor):
    return tensor[:8]
    
def extractPositionSelection(tensor):
    return tensor[9:18]
    
def extractPowerSelection(tensor):
    return tensor[19:]

def extractGameState(qType):
    if qType == QUESTION_TYPE.TUILES:
        return 0
    elif qType == QUESTION_TYPE.POWER:
        return 1
    elif qType == QUESTION_TYPE.MOVE:
        return 2
    return 3

class GameAgent():
    agentType = None

    def __init__(self, agentType):
        self.agentType = agentType
        if self.agentType == PLAYER_TYPE.GHOST:
            self.agent = DQNAgent(23, 20)
        else:
            self.agent = DQNAgent(22, 20)

    def getAgentType(self):
        return self.agentType

    ## Return the best tuile selection
    def selectTuile(self, world, tuiles):
        logging.info("[IA] Trying to find best tuile")

        possible_tuiles = [COLOR_INTEG[d['color']] for d in tuiles ]

        gameState = extractGameState(QUESTION_TYPE.TUILES)
        idata = world.getQLearningData(self.agentType, gameState)
        data = self.agent.process(idata)

        logging.info("[IA] Got result from DQN: %s"%(data))
        ##Feed action taken
        ##Take best color from possible tuiles
        best_value = float("-inf")
        best_id_rep = float("-inf")
        best_id_color = float("-inf")
        data_to_process = extractColorSelection(data[0])
        for idx, d in enumerate(possible_tuiles):
            if data_to_process[d] >= best_value:
                best_value = data_to_process[d]
                best_id_rep = idx
                best_id_color = d
        self.agent.action_taken(idata, best_id_color)

        print(tuiles[best_id_rep]['color'])
        print(type(tuiles[best_id_rep]['color']))

        #Setting up current color in world state
        world.setCurrentPlayedColor(tuiles[best_id_rep]['color'])

        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        return (str(best_id_rep), tuiles[best_id_rep]['color'])

    ## Return the best next pos
    def nextPos(self, world, available_pos):
        logging.info("[IA] selected POSITION %s"%(0))
        return str(0)

    ## Return the best power choice
    def powerChoice(self, world):
        logging.info("[IA] Use power %d"%(0))
        return str(0)

    def _processRewardGhost(self, world):
        ## Compute ratio score
        score_diff = world.getScore() - world.getOldScore()

        #If gain more than 6 then its reward of 1, else its near 0
        score_evol = score_diff / 6
        reward = score_evol

        ## Check if game ended
        game_ended = world.getScore() >= 22

        logging.info("[IA] Agent GHOST got %d reward"%(reward))
        self.agent.reward(reward, game_ended)

    def _processRewardDetective(self, world):
        ## Compute ratio score
        score_diff = world.getScore() - world.getOldScore()

        if score_diff == 0:
            score_diff = 1

        #If gain more than 6 then its reward of 1, else its near 0
        score_evol = 1 / score_diff
    
        #If score_evol is negative its really good, so we maximize reward
        reward = 1 if score_evol <= 0 else score_evol

        ## Check if game ended
        game_ended = world.getScore() >= 22

        logging.info("[IA] Agent DETECTIVE got %d reward"%(reward))
        self.agent.reward(reward, game_ended)

    ## Reward the agents
    ## Calculate a reward based on score, innocents people, etc
    def endOfHalfTour(self, world):
        if self.agentType == PLAYER_TYPE.GHOST:
            return self._processRewardGhost(world)
        return self._processRewardDetective(world)
