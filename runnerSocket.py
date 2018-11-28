import logging
import sys
from GameAgent import SmartGameAgent, GameAgent
from AgentTypes import PLAYER_TYPE, QUESTION_TYPE, INFO_STATUS
from ParsingSocket import Parser
from World import World
import time
from threading import Thread

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

def updateInfos(agentType, world, gameAgent, infoData, msgContent):
    if infoData['InfoStatus'] == INFO_STATUS.OK:
        logging.info("Got info TOUR %s"%(infoData))
        world.setStatus(infoData)
        ##Check if a new tour is starting
        ## to do so, check if the msg content is not violet power
        ##Notify agent to calcuate reward of previous tour
        if msgContent.find("Rappel des positions :") == -1 and infoData.get('Tour', None) != None:
            gameAgent.endOfHalfTour(world)
    elif infoData['InfoStatus'] == INFO_STATUS.PLACEMENT:
        logging.info("Got info PLACEMENT %s"%(infoData))
        world.updateTuiles(infoData['Data'])
    elif infoData['InfoStatus'] == INFO_STATUS.GHOST:
        if agentType == PLAYER_TYPE.DETECTIVE:
            raise RuntimeError("Received ghost but I am detective !")
        logging.info("Got info GHOST %s"%(infoData))
        world.setGhostColor(infoData['Data'])
    elif infoData['InfoStatus'] == INFO_STATUS.SUSPECT:
        world.setInnocentColor(infoData['Data']['Color'])

def processQuestions(parser, world, msg, gameAgent):
    questionData = parser.parseQuestion(msg.content)
    logging.info("Got question %s"%(questionData))

    world.updateState(questionData)
    answer = ""

    if questionData["QuestionType"] == QUESTION_TYPE.MOVE:
        answer = gameAgent.nextCurrentColorPos(world, questionData["Data"])
    elif questionData["QuestionType"] == QUESTION_TYPE.POWER:
        answer = gameAgent.powerChoice(world)
    elif questionData["QuestionType"] == QUESTION_TYPE.TUILES:
        answer = gameAgent.selectTuile(world, questionData["Data"])
    elif questionData["QuestionType"] == QUESTION_TYPE.P_BLANC:
        answer = gameAgent.nextPosColorWhitePower(world, questionData["Color"],
                                                    questionData["Data"])
    elif questionData["QuestionType"] == QUESTION_TYPE.P_VIOLET:
        answer = gameAgent.selectTuileVioletPower(world)
    elif questionData["QuestionType"] == QUESTION_TYPE.P_GRIS:
        answer = gameAgent.nextPosBlackRoom(world)
    elif questionData["QuestionType"] == QUESTION_TYPE.P_BLEU:
        answer = gameAgent.nextBlockedPathBluePower(world,
                                                    questionData["Data"])
    elif questionData["QuestionType"] == QUESTION_TYPE.ERROR:
        raise ValueError("Unknown question " + msg.content)

    logging.info("Sending answer %s"%(answer))
    parser.sendMsg(answer)

def loop(world, parser, gameAgent, agentType):
    while (True):
        msg = parser.readMsg()
        msgType = msg.type
        if msgType == "Information":
            logging.debug("MSG INFO: " + msg.content)
            if msg.content == "ResetGame" or msg.content == "EndGame":
                return msg.content
            infoData = parser.parseInfo(msg.content)
            if infoData['InfoStatus'] == INFO_STATUS.END:
                break
            updateInfos(agentType, world, gameAgent, infoData, msg.content)
        elif msgType == "Question":
            processQuestions(parser, world, msg, gameAgent)
    return "Unknown"   

def lancer(agentType, smart=True):
    logging.info("Launching %s IA"%(agentType))
    parser = Parser(agentType)
    logging.info("Init network...")
    parser.initNetwork()
    logging.info("Done!")
    gameAgent = None
    if smart:
        gameAgent = SmartGameAgent(agentType)
    else:
        gameAgent = GameAgent()
    while True:
        world = World()
        result = loop(world, parser, gameAgent, agentType)        
        logging.info("Got result from game %s"%(result))
        if result == "EndGame":
            break
            