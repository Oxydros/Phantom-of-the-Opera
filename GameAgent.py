import logging
import sys
from DQNLearning import DQNAgent
from AgentTypes import QUESTION_TYPE, PLAYER_TYPE
from World import COLOR_INTEG, INTEG_COLOR

def extractColorSelection(tensor):
    return tensor[:8]
    
def extractPositionSelection(tensor):
    return tensor[8:18]
    
def extractPowerSelection(tensor):
    return tensor[18:]

class GameAgent():
    def selectTuile(self, world, tuiles, violet_power = False):
        logging.info("Selecting Random Tuile 0")
        return str(0)

    def nextPos(self, world, available_pos, color):
        logging.info("Selecting Random Pos 0")
        return str(0)

    def selectPowerGris(self, world):
        logging.info("Selecting Random GRIS power")
        return str(0)

    def selectPowerBlue(self, world, available_pos):
        logging.info("Selecting Random GRIS power")
        return str(0)

    def powerChoice(self, world):
        logging.info("Selecting Random Power 0")
        return str(0)

    def endOfHalfTour(self, world):
        pass

def extractGameState(qType):
    return qType.value

class SmartGameAgent(GameAgent):
    agentType = None

    def __init__(self, agentType):
        self.agentType = agentType
        if self.agentType == PLAYER_TYPE.GHOST:
            self.agent = DQNAgent(23, 20)
        else:
            self.agent = DQNAgent(22, 20)

    def getAgentType(self):
        return self.agentType

    def selectData(self, data_to_process, possible_data):
        best_value = float("-inf")
        best_id_rep = float("-inf")
        best_id_data = float("-inf")
        for idx, d in enumerate(possible_data):
            if data_to_process[d] >= best_value:
                best_value = data_to_process[d]
                best_id_rep = idx
                best_id_data = d
        return best_id_rep, best_id_data, best_value

    ## Return the best tuile selection
    def selectTuile(self, world, tuiles, violet_power = False):
        logging.debug("[IA] Trying to find best tuile")

        possible_tuiles = None

        #If power is activated, agent can choose from every color
        #except violet
        if violet_power == True:
            possible_tuiles = [i for i in range(8)]
            possible_tuiles.remove(COLOR_INTEG['violet'])
        else:
            possible_tuiles = [COLOR_INTEG[d['color']] for d in tuiles ]

        gameState = extractGameState(QUESTION_TYPE.P_VIOLET if violet_power else
                                    QUESTION_TYPE.TUILES)
        idata = world.getQLearningData(self.agentType, gameState)
        data = self.agent.process(idata)
        logging.debug("[IA] Got result from DQN: %s"%(data))

        data_to_process = extractColorSelection(data[0])
        best_id_rep, best_id_data, best_value = self.selectData(data_to_process, possible_tuiles)
        
        self.agent.action_taken(idata, best_id_data)

        #Setting up current color in world state
        world.setCurrentPlayedColor(INTEG_COLOR[best_id_rep])

        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting tuile %s"%(INTEG_COLOR[best_id_rep]))
        return str(best_id_rep)

    ## Return the best next pos
    def nextPos(self, world, available_pos, color):
        logging.debug("[IA] Trying to find best new Position")

        possible_positions = [int(p) for p in available_pos]

        gameState = extractGameState(QUESTION_TYPE.MOVE if color == None else
                                    QUESTION_TYPE.P_BLANC)

        ##Save in case we have to switch for white power
        saved_color = world.getCurrentPlayedColor()

        if color != None:
            world.setCurrentPlayedColor(color['color'])

        idata = world.getQLearningData(self.agentType, gameState)
        data = self.agent.process(idata)
        logging.debug("[IA] Got result from DQN: %s"%(data))

        data_to_process = extractPositionSelection(data[0])
        best_id_rep, best_id_data, best_value = self.selectData(data_to_process, possible_positions)

        ##Add 8 because of position in actions
        assert(data[0][best_id_data + 8].item() == best_value.item())
        self.agent.action_taken(idata, best_id_data + 8)

        #Set new position
        world.setColorPosition(world.getCurrentPlayedColor(), best_id_data)

        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting position %s for %s"%(best_id_data,
                    world.getCurrentPlayedColor()))

        #Reset color in case of white poser was used
        if color != None:
            world.setCurrentPlayedColor(saved_color)
        return (str(best_id_rep))

    def selectPowerBlue(self, world, available_pos):
        logging.debug("[IA] Trying to find BLUE POS")

        possible_positions = None
        if available_pos != None:
            possible_positions = [int(p) for p in available_pos]
        else:
            possible_positions = [i for i in range(10)]

        gameState = extractGameState(QUESTION_TYPE.P_BLEU)

        idata = world.getQLearningData(self.agentType, gameState)
        data = self.agent.process(idata)
        logging.debug("[IA] Got result from DQN: %s"%(data))

        data_to_process = extractPositionSelection(data[0])
        best_id_rep, best_id_data, best_value = self.selectData(data_to_process, possible_positions)

        ##Add 8 because of position in actions
        assert(data[0][best_id_data + 8].item() == best_value.item())
        self.agent.action_taken(idata, best_id_data + 8)

        if available_pos != None:
            print("BLOCKING END IS ", best_id_data)
            world.setBlockedPathByIdx(best_id_data, 1)
        else:
            print("BLOCKING FIRST IS ", best_id_data)
            world.setBlockedPathByIdx(best_id_data, 0)
        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting position %s for BLEU"%(best_id_data))
        return (str(best_id_rep))

    ## Select the best position for gris power token
    def selectPowerGris(self, world):
        logging.debug("[IA] Trying to find best new BLACK TOKEN pos")

        gameState = extractGameState(QUESTION_TYPE.P_GRIS)

        idata = world.getQLearningData(self.agentType, gameState)
        data = self.agent.process(idata)
        logging.debug("[IA] Got result from DQN: %s"%(data))

        data_to_process = extractPositionSelection(data[0])
        possible_positions = range(0, 9)
        best_id_rep, best_id_data, best_value = self.selectData(data_to_process, possible_positions)

        ##Add 8 because of position in actions
        assert(data[0][best_id_data + 8].item() == best_value.item())
        self.agent.action_taken(idata, best_id_data + 8)

        #Set new black token position
        world.setBlackRoom(best_id_data)

        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting position %s for BLACK TOKEN"%(best_id_data))

        return (str(best_id_rep))

    ## Return the best power choice
    def powerChoice(self, world):
        logging.debug("[IA] Trying to active power")

        gameState = extractGameState(QUESTION_TYPE.POWER)
        idata = world.getQLearningData(self.agentType, gameState)
        data = self.agent.process(idata)
        logging.debug("[IA] Got result from DQN: %s"%(data))

        data_to_process = extractPowerSelection(data[0])
        best_id_rep, best_id_data, best_value = self.selectData(data_to_process, [0, 1])

        assert(data[0][best_id_data + 18].item() == best_value.item())
        self.agent.action_taken(idata, best_id_data + 18)

        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting power %s"%(best_id_data))
        return (str(best_id_rep))

    def _processRewardGhost(self, world):
        ## Compute ratio score
        score_diff = world.getScore() - world.getOldScore()

        #If gain more than 6 then its reward of 1, else its near 0
        score_evol = score_diff / 6
        reward = score_evol

        ## Check if game ended
        game_ended = world.getScore() >= 22

        logging.debug("[IA] Agent GHOST got %f reward"%(reward))
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

        logging.debug("[IA] Agent DETECTIVE got %d reward"%(reward))
        self.agent.reward(reward, game_ended)

    ## Reward the agents
    ## Calculate a reward based on score, innocents people, etc
    def endOfHalfTour(self, world):
        if self.agentType == PLAYER_TYPE.GHOST:
            return self._processRewardGhost(world)
        return self._processRewardDetective(world)
