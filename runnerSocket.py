import logging
import sys
from GameAgent import GameAgent
from AgentTypes import PLAYER_TYPE, QUESTION_TYPE, INFO_STATUS
from ParsingSocket import Parser
from World import World
import time
from AlphaBetaDetective import AlphaBetaDetective
from AlphaBetaFantome import AlphaBetaFantome
from threading import Thread

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

def updateInfos(world, infoData):
    if infoData['InfoStatus'] == INFO_STATUS.OK:
        logging.info("Got info tour %s"%(infoData))
        world.setStatus(infoData)
    elif infoData['InfoStatus'] == INFO_STATUS.PLACEMENT:
        logging.info("Got info tour %s"%(infoData))
        world.updateTuiles(infoData['Data'])

def loop(world, parser, d):
    while (True):
        logging.info("Waiting msg...")
        msg = parser.readMsg()
        msgType = msg.type
        logging.info("Got msg of type %s"%(msgType))
        if msgType == "Information":
            if msg.content == "ResetGame" or msg.content == "EndGame":
                return msg.content
            infoData = parser.parseInfo(msg.content)
            if infoData['InfoStatus'] == INFO_STATUS.END:
                break
            updateInfos(world, infoData)
        elif msgType == "Question":
            questionData = parser.parseQuestion(msg.content)
            world.updateState(questionData)
            answer = ""
            if questionData["QuestionType"] == QUESTION_TYPE.MOVE:
                answer, node = d.nextPos(node)
            elif questionData["QuestionType"] == QUESTION_TYPE.POWER:
                logging.info("Got question %s"%(questionData))
                answer, node = d.powerChoice(node)
            elif questionData["QuestionType"] == QUESTION_TYPE.TUILES:
                node = world.getNode()
                node = world.getColor(node, questionData["Data"])
                tree = world.getTree(node)
                logging.info("Got question %s"%(questionData))
                answer, node = d.selectTuile(tree)
            elif questionData["QuestionType"] == QUESTION_TYPE.GREY:
                answer = d.greyPower(node)
            elif questionData["QuestionType"] == QUESTION_TYPE.VIOLET:
                answer = d.violetPower(node)
            elif questionData["QuestionType"] == QUESTION_TYPE.BLUE:
                answer = d.bluePower(node, questionData["Data"])
            parser.sendMsg(answer) 
    return "Unknown"   

def lancer(agentType):
    logging.info("Launching %s IA"%(agentType))
    parser = Parser(agentType)
    logging.info("Init network...")
    parser.initNetwork()
    logging.info("Done!")
    while True:
        world = World()
        d = GameAgent(world, agentType)
        result = loop(world, parser, d)        
        logging.info("Got result from game %s"%(result))
        if result == "EndGame":
            break
            