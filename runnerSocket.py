import logging
import sys
from GameAgent import GameAgent
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

def updateInfos(world, infoData):
    if infoData['InfoStatus'] == INFO_STATUS.OK:
        logging.info("Got info tour %s"%(infoData))
        world.setStatus(infoData)
    elif infoData['InfoStatus'] == INFO_STATUS.PLACEMENT:
        logging.info("Got info tour %s"%(infoData))
        world.updateTuiles(infoData['Data'])

def lancer(agentType):
    logging.info("Launching %s IA"%(agentType))
    world = World()
    parser = Parser(agentType)
    logging.info("Init network...")
    parser.initNetwork()
    logging.info("Done!")
    d = GameAgent(world, agentType)
    while (not world.isGameEnded()):
        logging.info("Waiting msg...")
        msg = parser.readMsg()
        msgType = msg.type
        logging.info("Got msg of type %s"%(msgType))
        if msgType == "Information":
            infoData = parser.parseInfo(msg.content)
            if infoData['InfoStatus'] == INFO_STATUS.END:
                break
            updateInfos(world, infoData)
        elif msgType == "Question":
            questionData = parser.parseQuestion(msg.content)
            world.updateState(questionData)
            answer = ""
            print(questionData["QuestionType"], " ", QUESTION_TYPE.TUILES)
            if questionData["QuestionType"] == QUESTION_TYPE.MOVE:
                logging.info("Got question %s"%(questionData))
                answer = d.nextPos(questionData["Data"])
            elif questionData["QuestionType"] == QUESTION_TYPE.POWER:
                logging.info("Got question %s"%(questionData))
                answer = d.powerChoice()
            elif questionData["QuestionType"] == QUESTION_TYPE.TUILES:
                print("OUI")
                logging.info("Got question %s"%(questionData))
                answer = d.selectTuile(questionData["Data"])
            parser.sendMsg(answer)