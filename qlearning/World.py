import logging
import random
from . import AgentTypes

# -- GAME Constants --
MAP_SIZE = 10
MAX_SCORE = 22

COLOR_INTEG = {
    'rose': 0,
    'violet': 1,
    'marron': 2,
    'noir': 3,
    'blanc': 4,
    'rouge' : 5,
    'gris' : 6,
    'bleu' : 7
}

INTEG_COLOR = ['rose', 'violet', 'marron', 'noir', 'blanc', 'rouge', 'gris', 'bleu']

## Definition of the various color and when they can trigger their powers
POWER_PERMANENT = {'rose'}
POWER_BEFORE = {"violet", "marron"}
POWER_AFTER = {"noir" , "blanc"}
POWER_BOTH = {"rouge", "gris", "bleu"}
TOTAL_COLORS = POWER_PERMANENT | POWER_BEFORE | POWER_AFTER | POWER_BOTH

## Definition of the paths
DEF_ALLOWED_PATH = [{1,4}, {0,2}, {1,3}, {2,7}, {0,5,8}, {4,6}, {5,7}, {3,6,9}, {4,9}, {7,8}]
ROSE_ALLOWED_PATH = [{1,4}, {0,2,5,7}, {1,3,6}, {2,7}, {0,5,8,9}, {4,6,1,8}, {5,7,2,9}, {3,6,9,1}, {4,9,5}, {7,8,4,6}]

# Class reprensenting the state of the world
class World:

# passage
#
# 8--------9
# |        |
# |        |
# 4--5--6--7
# |        |
# 0--1--2--3
#

# passage secret
#   ________
#  /        \
# | 8--------9
# | |\      /|
#  \| \    / |
#   4--5--6--7
#   |  |  |  |\
#   0--1--2--3 |
#       \______/
#
    ## MAP
    game_map = [set() for i in range(MAP_SIZE)]
    ## Position of the special items
    blacktoken_pos = 0
    #Locked of the form [roomA, roomB]
    locked_path = []
    ## Current non innocent
    non_innocent_colors = TOTAL_COLORS.copy()
    innocent_colors = set()
    score = 4
    oldScore = 4
    tour = 0
    status = {}
    ghost_color = ""
    current_color = "none"

    def __init__(self, *args, **kwargs):
        pass

    def _checkPos(self, pos):
        if pos < 0 or pos >= MAP_SIZE:
            raise ValueError("Position %d is not valid"%(pos))
        
    def _checkColor(self, color):
        if not color in TOTAL_COLORS and color != "none":
            raise ValueError("Color %s doesn't exist!"%(color))

    def setGhostColor(self, color):
        self.ghost_color = color

    ## Set the position of the given Color
    def setColorPosition(self, color, pos):
        self._checkColor(color)
        self._checkPos(pos)
        #Check if color exist in map to remove it
        prev = self.getColorPosition(color)
        if (prev != -1):
            self.game_map[prev].remove(color)
        self.game_map[pos].add(color)
    
    ## Get the position of the given color
    def getColorPosition(self, color):
        self._checkColor(color)
        for id_room, room in enumerate(self.game_map):
            if color in room:
                return id_room
        return -1
    
    ## Get the possible deplacement for a given color and position
    def getPossibleDeplacementFromPos(self, color, cPos):
        self._checkColor(color)
        self._checkPos(cPos)
        possible = DEF_ALLOWED_PATH if color != "rose" else ROSE_ALLOWED_PATH
        if self.locked_path == None:
            raise RuntimeError("Locked is not set!")
        possible = possible[cPos]
        logging.info("Possible deplacement %s. Blocked is %s"%(possible, self.locked_path))
        #Try to delete from set the blocked path
        try:
            possible.remove(self.locked_path[0])
        except KeyError:
            pass
        try:
            possible.remove(self.locked_path[1])
        except KeyError:
            pass
        return possible

    ## Return all the colors found at the given pos
    def getColorsFromPos(self, pos):
        self._checkPos(pos)
        return self.game_map[pos]

    ## Return the current innocents
    def getInnocentColors(self):
        return self.innocent_colors

    def isInnocent(self, color):
        for iColor in self.innocent_colors:
            if (color == iColor):
                return True
        return False

    ## Return the list of potential fantoms
    def getPotentialFantoms(self):
        return (self.non_innocent_colors)

    ## Set a color as innocent
    def setInnocentColor(self, color):
        self._checkColor(color)
        try:
            self.non_innocent_colors.remove(color)
            self.innocent_colors.add(color)
        except KeyError:
            pass

    ## Set the given room as black (blacktoken_pos)
    def setBlackRoom(self, pos):
        self._checkPos(pos)
        self.blacktoken_pos = pos

    ## Get the black room
    def getBlackRoom(self):
        return self.blacktoken_pos

    ## Set blocked path
    def setBlockedPath(self, path):
        if (type(path) is not set or len(path) != 2):
            raise ValueError("Given blocked path is not valid")
        self.locked_path = list(path)
    
    def setBlockedPathByIdx(self, roomId, idx):
        self.locked_path[idx] = roomId

    ## Get the blocked path
    def getBlockedPath(self):
        return self.locked_path
    
    ## Print the MAP
    def printMap(self, gameState = None):
        logging.debug("---- GAME MAP ----")
        if gameState != None:
            logging.debug("Called for STATE: %s ==> %d"%(AgentTypes.QUESTION_TYPE(gameState),
                            gameState))
        logging.debug("Tour is %d and score is %d"%(self.tour, self.score))
        logging.debug("Ghost is %s"%(self.ghost_color))
        logging.debug("Current played color is %s"%(self.current_color))
        logging.debug("Blocked path is %s"%(self.locked_path))
        logging.debug("Dark room is %d"%(self.blacktoken_pos))
        logging.debug("Cleaned colors: %s"%(self.innocent_colors))
        for id_room, room in enumerate(self.game_map):
            logging.debug("Room %d: %s"%(id_room, room))
        logging.debug("---------------")
    
    ## Set the score of the current game
    def setScore(self, newScore):
        self.oldScore = self.score
        self.score = newScore

    def getOldScore(self):
        return self.oldScore

    ## Get the score of the current game
    def getScore(self):
        return (self.score)

    def isGameEnded(self):
        return len(self.non_innocent_colors) == 1 or self.score == MAX_SCORE

    def setTour(self, newTour):
        self.tour = newTour

    def getTour(self):
        return self.tour

    ## Set the current status of the game
    ## Fetch by the Parser in infos.txt
    def setStatus(self, status):
        self.status = status
        self.updateTuiles(status["Tuiles"])
        self.setBlackRoom(status["Ombre"])
        self.setBlockedPath(status["Lock"])
        self.setScore(status['Score'])
        self.setTour(status['Tour'])

    ## Get the current status of the game
    ## Fetch by the Parser in infos.txt
    def getStatus(self):
        return self.status

    ## Update the state of the world depending on the questions
    def updateState(self, questionInfos):
        if questionInfos["QuestionType"] == AgentTypes.QUESTION_TYPE.MOVE:
            pass
        elif questionInfos["QuestionType"] == AgentTypes.QUESTION_TYPE.POWER:
            pass
        elif questionInfos["QuestionType"] == AgentTypes.QUESTION_TYPE.TUILES:
            self.updateTuiles(questionInfos["Data"])
    
    ## Update local tuiles infos
    def updateTuiles(self, tuilesInfos):
        #For each tuiles
        for t in tuilesInfos:
            color = t['color']
            pos = t['pos']
            state = t['state']
            #Update the position
            self.setColorPosition(color, pos)
            #Update the state
            if state == 'clean':
                self.setInnocentColor(color)

    def setCurrentPlayedColor(self, color):
        if not isinstance(color, str):
            raise ValueError("Bad args for color, expected string")
        self.current_color = color

    def getCurrentPlayedColor(self):
        return self.current_color

    def getQLearningData(self, agentType, gameState):
        data = []
        logging.debug("--QLearningData--")
        logging.debug("Color positions:")
        ##Setup color position data 8
        for color in INTEG_COLOR:
            color_pos = self.getColorPosition(color)
            data.append(color_pos)
            logging.debug("%s: %d"%(color, color_pos))
        logging.debug("Innocents color:")
        ##Setup innocents color 8
        for color in INTEG_COLOR:
            logging.debug("%s: %d"%(color, 1 if self.isInnocent(color) else 0))
            if self.isInnocent(color):
                data.append(1)
            else:
                data.append(0)
        ##Setup lock and light position data => 3
        sortedLock = sorted(self.locked_path)
        data.append(sortedLock[0])
        data.append(sortedLock[1])
        logging.debug("Blocked path: %d %d"%(sortedLock[0], sortedLock[1]))
        data.append(self.blacktoken_pos)
        logging.debug("Black room: %d"%(self.blacktoken_pos))
        ##Setup score => 1
        logging.debug("Score: %d"%(self.score))
        data.append(self.score)
        data.append(COLOR_INTEG[self.current_color] if self.current_color != "none" else -1)
        logging.debug("Current color: %d"%(COLOR_INTEG[self.current_color] if self.current_color != "none" else -1))
        data.append(gameState)
        logging.debug("Current gameState: %d"%(gameState))
        if (agentType == AgentTypes.PLAYER_TYPE.GHOST):
            data.append(COLOR_INTEG[self.ghost_color])
        logging.debug("--QLearningData END--")
        self.printMap(gameState)
        return data

if __name__ == "__main__":
    #Test the World class
    world = World()
    world.setBlockedPath({0,1})
    world.setBlackRoom(0)
    for c in TOTAL_COLORS:
        world.setColorPosition(c, random.randrange(MAP_SIZE))
    world.printMap()
    newRosePos = world.getPossibleDeplacementFromPos('rose', world.getColorPosition('rose'))
    print("New possible pos for rose are %s"%(newRosePos))
    world.setColorPosition('rose', newRosePos.pop())
    world.printMap()
    print("Not innocents are %s"%(world.getPotentialFantoms()))
    print("Innocents are %s"%(world.getInnocentColors()))
