import logging
import sys
from Detective import Detective
from Parsing import Parser, PLAYER_TYPE, INFO_STATUS, QUESTION_TYPE
from World import World
import time

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

def lancer():
    print("Launching Detective IA")
    world = World()
    parser = Parser(PLAYER_TYPE.DETECTIVE)
    d = Detective(world)
    while (not world.isGameEnded()):
        infos = parser.readInfo()
        logging.info("Got info tour %s"%(infos))
        time.sleep(1)
        if infos['InfoStatus'] == INFO_STATUS.OK:
                world.setStatus(infos)
        elif infos['InfoStatus'] == INFO_STATUS.END:
                break
        elif infos['InfoStatus'] == INFO_STATUS.PLACEMENT:
                world.updateTuiles(infos['Data'])
        question = parser.readQuestion()
        world.updateState(question)
        logging.info("Got question %s"%(question))
        answer = ""
        if question["QuestionType"] == QUESTION_TYPE.MOVE:
                answer = d.nextPos(question["Data"])
        elif question["QuestionType"] == QUESTION_TYPE.POWER:
                answer = d.powerChoice()
        elif question["QuestionType"] == QUESTION_TYPE.TUILES:
                answer = d.selectTuile(question["Data"])
        logging.info("IA Answer: %s"%(answer))
        parser.writeAnswer(answer)
        time.sleep(1)
    world.printMap()
    logging.info("END IA")