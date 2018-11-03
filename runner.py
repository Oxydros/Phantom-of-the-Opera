import logging
from Detective import Detective
from Parsing import Parser, PLAYER_TYPE
from World import World


def lancer():
    print("Launching Detective IA")
    world = World()
    parser = Parser(PLAYER_TYPE.DETECTIVE)
    d = Detective(world)
    while (not world.isGameEnded()):
        infos = parser.readInfo()
        logging.info("Got info tour %s"%(infos))
        question = parser.readQuestion()
        logging.info("Got question %s"%(question))