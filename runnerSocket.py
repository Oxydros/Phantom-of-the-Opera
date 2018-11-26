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
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

def updateInfos(agentType, world, d, infoData, lastQuestionType):
    if infoData['InfoStatus'] == INFO_STATUS.OK:
        logging.info("Got info TOUR %s"%(infoData))
        world.setStatus(infoData)
        ##Check if a new tour is starting
        ##Notify agent to calcuate reward of previous tour
        if infoData.get('Tour', None) != None:
            d.endOfHalfTour(world)
    elif infoData['InfoStatus'] == INFO_STATUS.PLACEMENT:
        logging.info("Got info PLACEMENT %s"%(infoData))
        world.updateTuiles(infoData['Data'])
    elif infoData['InfoStatus'] == INFO_STATUS.GHOST:
        if agentType == PLAYER_TYPE.DETECTIVE:
            raise RuntimeError("Received ghost but I am detective !")
        logging.info("Got info GHOST %s"%(infoData))
        world.setGhostColor(infoData['Data'])

def processQuestions(parser, world, msg, d):
    questionData = parser.parseQuestion(msg.content)
    logging.info("Got question %s"%(questionData))

    world.updateState(questionData)
    answer = ""

    if questionData["QuestionType"] == QUESTION_TYPE.MOVE:
        answer = d.nextPos(world, questionData["Data"],
                            questionData["Color"])
    elif questionData["QuestionType"] == QUESTION_TYPE.POWER:
        answer = d.powerChoice(world)
    elif questionData["QuestionType"] == QUESTION_TYPE.TUILES:
        answer = d.selectTuile(world, questionData["Data"])
    elif questionData["QuestionType"] == QUESTION_TYPE.P_VIOLET:
        answer = d.selectTuile(world, None, True)
    elif questionData["QuestionType"] == QUESTION_TYPE.P_GRIS:
        answer = d.selectPowerGris(world)
    elif questionData["QuestionType"] == QUESTION_TYPE.P_BLEU:
        answer = d.selectPowerBlue(world, questionData["Data"])
    elif questionData["QuestionType"] == QUESTION_TYPE.ERROR:
        raise ValueError("Unknown question " + msg.content)

    logging.info("Sending answer %s"%(answer))
    parser.sendMsg(answer)
    lastQuestionType = questionData["QuestionType"]    

def loop(world, parser, d, agentType):
    lastQuestionType = None
    prevScore = None
    while (True):
        msg = parser.readMsg()
        msgType = msg.type
        if msgType == "Information":
            if msg.content == "ResetGame" or msg.content == "EndGame":
                return msg.content
            infoData = parser.parseInfo(msg.content)
            if infoData['InfoStatus'] == INFO_STATUS.END:
                break
            updateInfos(agentType, world, d, infoData, lastQuestionType)
        elif msgType == "Question":
            processQuestions(parser, world, msg, d)
    return "Unknown"   

def lancer(agentType, smart=True):
    logging.info("Launching %s IA"%(agentType))
    parser = Parser(agentType)
    logging.info("Init network...")
    parser.initNetwork()
    logging.info("Done!")
    d = None
    if smart:
        d = SmartGameAgent(agentType)
    else:
        d = GameAgent()
    while True:
        world = World()
        result = loop(world, parser, d, agentType)        
        logging.info("Got result from game %s"%(result))
        if result == "EndGame":
            break
            