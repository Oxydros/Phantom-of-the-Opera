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
    def nextCurrentColorPos(self, world, available_pos):
        logging.info("Selecting Random Pos 0")
        return str(0)

    def nextPosColorWhitePower(self, world, target_color, available_pos):
        logging.info("Selecting Random WHITE POWER")
        return str(0)

    def nextBlockedPathBluePower(self, world, available_pos):
        logging.info("Selecting Random BLUE POWER")
        return str(0)

    def nextPosBlackRoom(self, world):
        logging.info("Selecting Random GRIS POWER")
        return str(0)

    def selectTuile(self, world, tuiles):
        logging.info("Selecting Random Tuile 0")
        return str(0)

    def selectTuileVioletPower(self, world, tuiles):        
        logging.info("Selecting Random Tuile 0 for VIOLET POWER")
        return str(0)

    def powerChoice(self, world):
        logging.info("Selecting Random Power 0")
        return str(0)

    def endOfHalfTour(self, world):
        pass

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

    def _selectData(self, data_to_process, possible_data):
        best_value = float("-inf")
        best_id_rep = float("-inf")
        best_id_data = float("-inf")
        for idx, d in enumerate(possible_data):
            if data_to_process[d] >= best_value:
                best_value = data_to_process[d]
                best_id_rep = idx
                best_id_data = d
        return best_id_rep, best_id_data, best_value

    def _selectPosition(self, world, gameState, possible_data):
        logging.debug("[IA][GameState=%s] Trying to find an optimal position between %s"%(gameState, possible_data))

        idata = world.getQLearningData(self.agentType, gameState)
        data = self.agent.process(idata)
        logging.debug("[IA][GameState=%s] Got result from DQN: %s"%(gameState, data))

        data_to_process = extractPositionSelection(data[0])
        best_id_rep, best_id_data, best_value = self._selectData(data_to_process, possible_data)

        ##Add 8 because of position in actions
        assert(data[0][best_id_data + 8].item() == best_value.item())
        self.agent.action_taken(idata, best_id_data + 8)

        return best_id_rep, best_id_data, best_value

    ## Return the best next pos
    def nextCurrentColorPos(self, world, available_pos):
        possible_positions = [int(p) for p in available_pos]

        gameState = QUESTION_TYPE.MOVE.value

        best_id_rep, best_id_data, _ = self._selectPosition(world, gameState, possible_positions)

        #Set new position
        world.setColorPosition(world.getCurrentPlayedColor(), best_id_data)

        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting position %s for %s"%(best_id_data,
                    world.getCurrentPlayedColor()))
        return (str(best_id_data))

    ## Return the best next pos for white power
    def nextPosColorWhitePower(self, world, target_color, available_pos):
        possible_positions = [int(p) for p in available_pos]

        ##Save in case we have to switch for white power
        saved_color = world.getCurrentPlayedColor()
        world.setCurrentPlayedColor(target_color['color'])

        gameState = QUESTION_TYPE.P_BLANC.value

        best_id_rep, best_id_data, _ = self._selectPosition(world, gameState, possible_positions)

        #Set new position
        world.setColorPosition(world.getCurrentPlayedColor(), best_id_data)

        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting position %s for %s"%(best_id_data,
                    world.getCurrentPlayedColor()))
        world.setCurrentPlayedColor(saved_color)
        return (str(best_id_data))

    ## Return best pos for blue power, blocked path
    def nextBlockedPathBluePower(self, world, available_pos):
        logging.debug("[IA] Trying to find BLOCKED PATH for BLUE POWER")

        possible_positions = None
        if available_pos != None:
            possible_positions = [int(p) for p in available_pos]
        else:
            possible_positions = [i for i in range(10)]

        gameState = QUESTION_TYPE.P_BLEU.value

        best_id_rep, best_id_data, _ = self._selectPosition(world, gameState, possible_positions)

        if available_pos != None:
            world.setBlockedPathByIdx(best_id_data, 1)
        else:
            world.setBlockedPathByIdx(best_id_data, 0)
        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting position %s for BLEU"%(best_id_data))
        return (str(best_id_rep))

    ## Select the best position for gris power token
    def nextPosBlackRoom(self, world):
        logging.debug("[IA] Trying to find best new BLACK TOKEN pos")

        gameState = QUESTION_TYPE.P_GRIS.value

        possible_positions = range(0, 9)
        best_id_rep, best_id_data, _ = self._selectPosition(world, gameState, possible_positions)

        #Set new black token position
        world.setBlackRoom(best_id_data)

        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting position %s for BLACK TOKEN"%(best_id_data))

        return (str(best_id_rep))

    ## Return the best tuile selection
    def selectTuile(self, world, tuiles):
        logging.debug("[IA][GameState=%s] Trying to find best tuile"%(QUESTION_TYPE.TUILES))

        possible_tuiles = [COLOR_INTEG[d['color']] for d in tuiles ]

        gameState = QUESTION_TYPE.TUILES.value
        idata = world.getQLearningData(self.agentType, gameState)
        data = self.agent.process(idata)
        logging.debug("[IA] Got result from DQN: %s"%(data))

        data_to_process = extractColorSelection(data[0])
        best_id_rep, best_id_data, _ = self._selectData(data_to_process, possible_tuiles)
        
        self.agent.action_taken(idata, best_id_data)

        #Setting up current color in world state
        world.setCurrentPlayedColor(INTEG_COLOR[best_id_data])

        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting tuile %s"%(INTEG_COLOR[best_id_data]))
        return str(best_id_rep)

    ## Return the best tuile selection
    def selectTuileVioletPower(self, world):
        logging.debug("[IA][GameState=%s] Trying to find best tuile"%(QUESTION_TYPE.P_VIOLET))

        # If power is activated, agent can choose from every color except violet
        possible_tuiles = [i for i in range(8)]
        possible_tuiles.remove(COLOR_INTEG['violet'])

        gameState = QUESTION_TYPE.P_VIOLET.value
        idata = world.getQLearningData(self.agentType, gameState)
        data = self.agent.process(idata)
        logging.debug("[IA] Got result from DQN: %s"%(data))

        data_to_process = extractColorSelection(data[0])
        best_id_rep, best_id_data, _ = self._selectData(data_to_process, possible_tuiles)
        
        self.agent.action_taken(idata, best_id_data)

        self.agent.next_state(world.getQLearningData(self.agentType, gameState))

        logging.info("Selecting tuile for VIOLET POWER %s"%(INTEG_COLOR[best_id_data]))
        return str(best_id_rep)

    ## Return the best power choice
    def powerChoice(self, world):
        logging.debug("[IA] Trying to active power")

        gameState = QUESTION_TYPE.POWER.value
        idata = world.getQLearningData(self.agentType, gameState)
        data = self.agent.process(idata)
        logging.debug("[IA] Got result from DQN: %s"%(data))

        data_to_process = extractPowerSelection(data[0])
        best_id_rep, best_id_data, best_value = self._selectData(data_to_process, [0, 1])

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
        logging.info("[IA] Notified END OF TOUR. Calculating rewards...")
        if self.agentType == PLAYER_TYPE.GHOST:
            return self._processRewardGhost(world)
        return self._processRewardDetective(world)
