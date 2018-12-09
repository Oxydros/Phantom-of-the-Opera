import logging
import sys
from . import GameAgent
from . import Parsing
from . import World
from . import AgentTypes
import time

root = logging.getLogger()
root.setLevel(logging.DEBUG)
hand_name = ["l'inspecteur", "le fantome"]

def lancer(agentType):
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - '+ hand_name[agentType] +' - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    print("Launching %s"%(hand_name[agentType]))
    world = World.World()
    parser = Parsing.Parser(AgentTypes.PLAYER_TYPE.DETECTIVE)
    d = GameAgent.GameAgent(world, agentType)
    while (not world.isGameEnded()):
        infos = parser.readInfo()
        # time.sleep(1)
        if infos['InfoStatus'] == AgentTypes.INFO_STATUS.OK:
                logging.info("Got info tour %s"%(infos))
                world.setStatus(infos)
        elif infos['InfoStatus'] == AgentTypes.INFO_STATUS.END:
                break
        elif infos['InfoStatus'] == AgentTypes.INFO_STATUS.PLACEMENT:
                logging.info("Got info tour %s"%(infos))
                world.updateTuiles(infos['Data'])
        question = parser.readQuestion()
        world.updateState(question)
        answer = ""
        if question["QuestionType"] == AgentTypes.QUESTION_TYPE.MOVE:
                logging.info("Got question %s"%(question))
                answer, node = d.nextPos(node)
        elif question["QuestionType"] == AgentTypes.QUESTION_TYPE.POWER:
                logging.info("Got question %s"%(question))
                answer, node = d.powerChoice(node)
        elif question["QuestionType"] == AgentTypes.QUESTION_TYPE.TUILES:
                node = world.getNode()
                node = world.getColor(node, question["Data"])
                tree = world.getTree(node)
                logging.info("Got question %s"%(question))
                answer, node = d.selectTuile(tree)
        elif question["QuestionType"] == AgentTypes.QUESTION_TYPE.GREY:
                answer = d.greyPower(node)
        elif question["QuestionType"] == AgentTypes.QUESTION_TYPE.VIOLET:
                answer = d.violetPower(node)
        elif question["QuestionType"] == AgentTypes.QUESTION_TYPE.BLUE:
                answer = d.bluePower(node, question["Data"])
        parser.writeFileAnswer(answer)
        # time.sleep(1)
    world.printMap()
    logging.info("END IA")


def updateInfos(world, infoData):
    if infoData['InfoStatus'] == AgentTypes.INFO_STATUS.OK:
        logging.info("Got info tour %s"%(infoData))
        world.setStatus(infoData)
    elif infoData['InfoStatus'] == AgentTypes.INFO_STATUS.PLACEMENT:
        logging.info("Got info tour %s"%(infoData))
        world.updateTuiles(infoData['Data'])
            