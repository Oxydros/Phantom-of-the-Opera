import logging
import sys
from . import GameAgent
from . import AgentTypes
from . import ParsingFile
from . import World

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

def updateInfos(world, infoData):
    if infoData['InfoStatus'] == AgentTypes.INFO_STATUS.OK:
        logging.info("Got info tour %s"%(infoData))
        world.setStatus(infoData)
    elif infoData['InfoStatus'] == AgentTypes.INFO_STATUS.PLACEMENT:
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
                logging.info("Got question %s"%(questionData))
                answer, node = d.powerChoice(node)
            elif questionData["QuestionType"] == AgentTypes.QUESTION_TYPE.TUILES:
                node = world.getNode()
                node = world.getColor(node, questionData["Data"])
                tree = world.getTree(node)
                logging.info("Got question %s"%(questionData))
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
    logging.info("Launching %s IA"%(agentType))
    parser = ParsingFile.Parser(agentType)
    parser.start()
    logging.info("Done!")
    while True:
        world = World.World()
        d = GameAgent.GameAgent(world, agentType)
        result = loop(world, parser, d)        
        logging.info("Got result from game %s"%(result))
        if result == "EndGame":
            break