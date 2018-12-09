import logging
import random
from GameNode import GameNode
from GameTree import GameTree
from Parsing import QUESTION_TYPE

# -- GAME Constants --
MAP_SIZE = 10
MAX_SCORE = 22

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
    score = 0
    tour = 0
    status = {}
    pos = []
    gameTree = GameTree()

    def __init__(self, *args, **kwargs):
        pass

    def _checkPos(self, pos):
        if pos < 0 or pos >= MAP_SIZE:
            raise ValueError("Position %d is not valid"%(pos))
        
    def _checkColor(self, color):
        if not color in TOTAL_COLORS:
            raise ValueError("Color %s doesn't exist!"%(color))

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

    ## Get the blocked path
    def getBlockedPath(self):
        return self.locked_path
    
    ## Print the MAP
    def printMap(self):
        print("---- GAME MAP ----")
        print("Tour is %d and score is %d"%(self.tour, self.score))
        print("Blocked path is %s"%(self.locked_path))
        print("Dark room is %d"%(self.blacktoken_pos))
        print("Cleaned: %s"%(self.innocent_colors))
        for id_room, room in enumerate(self.game_map):
            print("Room %d: %s"%(id_room, room))
        print(self.pos)
        print("---------------")
    
    ## Set the score of the current game
    def setScore(self, newScore):
        self.score = newScore

    ## Get the score of the current game
    def getScore(self):
        return (self.score)

    def isGameEnded(self):
        return len(self.non_innocent_colors) == 1 or self.score == MAX_SCORE

    def setTour(self, newTour):
        self.tour = newTour

    def getTour(self):
        return self.tour

    def getNode(self):
        return GameNode(self.pos, [], "", self.score, False)

    def getColor(self, node , infos) :
        for elem in infos :
            node.color.append(elem["color"]);
        return node;

    def getTree(self, node) :
        return (self.gameTree.doGameTree(node))

    def setPos(self, status, Tuiles) :
        for elem in Tuiles :
            tab = [elem['color'], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
            tab[elem['pos'] + 1] = 1
            if (elem['state'] != 'suspect') :
                tab[11] = 0
            self.pos.append(tab)
        tab = ['light', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        tab[status['Ombre'] + 1] = 1;
        self.pos.append(tab)
        tabLock = ['lock', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        tabLock[list(status['Lock'])[0] + 1] = 1
        tabLock[list(status['Lock'])[1] + 1] = 1
        self.pos.append(tabLock)
    ## Set the current status of the game
    ## Fetch by the Parser in infos.txt
    def setStatus(self, status):
        self.pos = []
        self.status = status
        self.updateTuiles(status["Tuiles"])
        self.setBlackRoom(status["Ombre"])
        self.setBlockedPath(status["Lock"])
        self.setScore(status['Score'])
        self.setTour(status['Tour'])
        self.setPos(status, status['Tuiles'])

    ## Get the current status of the game
    ## Fetch by the Parser in infos.txt
    def getStatus(self):
        return self.status

    ## Update the state of the world depending on the questions
    def updateState(self, questionInfos):
        if questionInfos["QuestionType"] == QUESTION_TYPE.MOVE:
            pass
        elif questionInfos["QuestionType"] == QUESTION_TYPE.POWER:
            pass
        elif questionInfos["QuestionType"] == QUESTION_TYPE.TUILES:
            self.updateTuiles(questionInfos["Data"])
    
    ## Update local tuiles infos
    def updateTuiles(self, tuilesInfos):
        for line in self.pos :
            for elem in tuilesInfos :
                if (line[0] == elem['color']) :
                    line[1] = 0
                    line[2] = 0
                    line[3] = 0
                    line[4] = 0
                    line[5] = 0
                    line[6] = 0
                    line[7] = 0
                    line[8] = 0
                    line[9] = 0
                    line[10] = 0
                    line[elem['pos'] + 1] = 1
                    if (elem['state'] != 'suspect') :
                        line[11] = 0

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
