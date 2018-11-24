import logging
import sys
from DQNLearning import DQNAgent
from AgentTypes import QUESTION_TYPE, PLAYER_TYPE
from World import COLOR_INTEG, INTEG_COLOR

TUILE_IDATA_POINTS = 93
TUILE_ODATA_POINTS = 8

POWER_IDATA_POINTS = 107
POWER_ODATA_POINTS = 2

MOV_IDATA_POINTS = 107
MOV_ODATA_POINTS = 10

class GameAgent():
    agentType = None

    def __init__(self, agentType):
        self.agentType = agentType
        if self.agentType == PLAYER_TYPE.GHOST:
            self.tuileAgent = DQNAgent(TUILE_IDATA_POINTS + 1,
            TUILE_ODATA_POINTS)
        else:
            self.tuileAgent = DQNAgent(TUILE_IDATA_POINTS,
            TUILE_ODATA_POINTS)

    def getAgentType(self):
        return self.agentType

    ## Return the best tuile selection
    def selectTuile(self, world, tuiles):
        logging.info("[IA] Trying to find best tuile")

        possible_tuiles = [COLOR_INTEG[d['color']] for d in tuiles ]

        idata = world.getQLearningData(QUESTION_TYPE.TUILES,
                                        self.agentType)
        data = self.tuileAgent.process(idata)

        logging.info("[IA] Got result from DQN: %s"%(data))
        ##Feed action taken
        ##Take best color from possible tuiles
        best_value = -1
        best_id_rep = -1
        best_id_color = -1
        data_to_process = data[0]
        for idx, d in enumerate(possible_tuiles):
            if data_to_process[d] > best_value:
                best_value = data_to_process[d]
                best_id_rep = idx
                best_id_color = d
        # print(tuiles)
        # print(possible_tuiles)
        # print("Data is %s and best id is %d which is colore %s"%(data, best_id_color, INTEG_COLOR[best_id_color]))
        # print(best_id_rep)
        self.tuileAgent.action_taken(idata, data[0, best_id_color])

        # State doesn't change for Tuile selection
        self.tuileAgent.next_state(idata)
        return (str(best_id_rep), tuiles[best_id_rep]['color'])

    ## Return the best next pos
    def nextPos(self, world, available_pos):
        logging.info("[IA] selected POSITION %s"%(0))
        return str(0)

    ## Return the best power choice
    def powerChoice(self, world):
        logging.info("[IA] Use power %d"%(0))
        return str(0)

    ## Reward the agents
    def rewardAgent(self, reward, end_game):
        self.tuileAgent.reward(reward, end_game)

    ## Notify the agents of a new state
    def nextState(self, world, lastQuestionType):
        pass
        # logging.info("[IA] Next state called with last type %s"%(lastQuestionType))
        # if lastQuestionType == QUESTION_TYPE.TUILES:
        #     self.tuileAgent.next_state(world.getQLearningData(lastQuestionType,
        #     self.agentType))