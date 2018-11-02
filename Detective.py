import logging
from IA import IA

class Detective(IA):
    def __init__(self, world, *args, **kwargs):
        super().__init__(IA.IA_TYPE.DETECTIVE, world, *args, **kwargs)

    ## Return the best next pos
    def nextPos(self):
        logging.info("Trying to find best next pos")

    ## Return the best power choice
    def powerChoice(self):
        logging.info("Trying to find best use of power")

    ## Return the best tuile selection
    def selectTuile(self, tuiles):
        logging.info("Trying to find best tuile")