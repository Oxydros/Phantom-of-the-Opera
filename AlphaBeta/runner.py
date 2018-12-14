import logging
import sys
from . import GameAgent
from . import AgentTypes
from . import ParsingFile
from . import World

def updateInfos(world, infoData):
    if infoData['InfoStatus'] == AgentTypes.INFO_STATUS.OK:
        world.setStatus(infoData)
    elif infoData['InfoStatus'] == AgentTypes.INFO_STATUS.PLACEMENT:
        world.updateTuiles(infoData['Data'])

def loop(world, parser, d):
    while (True):
        msg = parser.readMsg()
        msgType = msg.type
        if msgType == "Information":
            infoData = parser.parseInfo(msg.content)
            if infoData['InfoStatus'] == AgentTypes.INFO_STATUS.FINAL_SCORE:
                return "Detected END TOUR"
            if msg.content == "ResetGame" or msg.content == "EndGame":
                return msg.content
            if infoData['InfoStatus'] == AgentTypes.INFO_STATUS.END:
                break
            updateInfos(world, infoData)
        elif msgType == "Question":
            questionData = parser.parseQuestion(msg.content)
            world.updateState(questionData)
            answer = ""
            if questionData["QuestionType"] == AgentTypes.QUESTION_TYPE.MOVE:
                answer, node = d.nextPos(node)
            elif questionData["QuestionType"] == AgentTypes.QUESTION_TYPE.POWER:
                answer, node = d.powerChoice(node)
            elif questionData["QuestionType"] == AgentTypes.QUESTION_TYPE.TUILES:
                node = world.getNode()
                node = world.getColor(node, questionData["Data"])
                tree = world.getTree(node)
                answer, node = d.selectTuile(tree)
            elif questionData["QuestionType"] == AgentTypes.QUESTION_TYPE.GREY:
                answer = d.greyPower(node)
            elif questionData["QuestionType"] == AgentTypes.QUESTION_TYPE.VIOLET:
                answer = d.violetPower(node)
            elif questionData["QuestionType"] == AgentTypes.QUESTION_TYPE.BLUE:
                answer = d.bluePower(node, questionData["Data"])
            parser.sendMsg(answer) 
    return "Unknown"   

def lancer(agentType):
    parser = ParsingFile.Parser(agentType)
    parser.start()
    world = World.World()
    d = GameAgent.GameAgent(world, agentType)
    result = loop(world, parser, d)        
    parser.stop();