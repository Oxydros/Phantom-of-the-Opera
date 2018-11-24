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

def updateInfos(world, d, infoData, lastQuestionType):
    if infoData['InfoStatus'] == INFO_STATUS.OK:
        logging.info("Got info tour %s"%(infoData))
        world.setStatus(infoData)
        d.nextState(world, lastQuestionType)
    elif infoData['InfoStatus'] == INFO_STATUS.PLACEMENT:
        logging.info("Got info tour %s"%(infoData))
        world.updateTuiles(infoData['Data'])
        d.nextState(world, lastQuestionType)

def loop(world, parser, d, agentType):
    lastQuestionType = None
    prevScore = None
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
            updateInfos(world, d, infoData, lastQuestionType)

            ##Update reward: check if score changed
            new_score = world.getScore()
            if prevScore == None:
                prevScore = new_score
            elif new_score != prevScore:
                if agentType == PLAYER_TYPE.GHOST:
                    d.rewardAgent(1 if new_score > prevScore else -1, 0)
                else:
                    d.rewardAgent(1 if new_score <= prevScore else -1, 0)
        elif msgType == "Question":
            questionData = parser.parseQuestion(msg.content)
            world.updateState(questionData)
            answer = ""
            if questionData["QuestionType"] == QUESTION_TYPE.MOVE:
                logging.info("Got question %s"%(questionData))
                answer = d.nextPos(world, questionData["Data"])
            elif questionData["QuestionType"] == QUESTION_TYPE.POWER:
                logging.info("Got question %s"%(questionData))
                answer = d.powerChoice(world)
            elif questionData["QuestionType"] == QUESTION_TYPE.TUILES:
                logging.info("Got question %s"%(questionData))
                answer, actual_color = d.selectTuile(world, questionData["Data"])
                world.setCurrentPlayedColor(actual_color)
            parser.sendMsg(answer) 
            lastQuestionType = questionData["QuestionType"]
    return "Unknown"   

def lancer(agentType):
    logging.info("Launching %s IA"%(agentType))
    parser = Parser(agentType)
    logging.info("Init network...")
    parser.initNetwork()
    logging.info("Done!")
    d = GameAgent(agentType)
    while True:
        world = World()
        result = loop(world, parser, d, agentType)        
        logging.info("Got result from game %s"%(result))
        if result == "EndGame":
            break
            