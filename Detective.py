import logging

class Detective():

    actualTuile = None
    actualColor = None
    actualPos = None
    selectedPos = 0
    powerQ = 0
    selectedPower = [0, 0]
    world = None

    def __init__(self, world):
        self.world = world

    ## Return the best tuile selection
    def selectTuile(self, tuiles):
        self.powerQ = 0
        logging.info("Trying to find best tuile")
        self.actualTuile = tuiles[0]
        self.actualPos = tuiles[0]['pos']
        self.actualColor = tuiles[0]['color']

        # IA HERE
        # MUST SET selectedPower and selectedPos
        # MUST RET TUILE COLOR

        return "0"

    ## Return the best next pos
    def nextPos(self, available_pos):
        logging.info("IA selected POSITION %s"%(self.selectedPos))
        return str(self.selectedPos)

    ## Return the best power choice
    def powerChoice(self):
        logging.info("Use power %d"%(self.selectedPower[self.powerQ]))
        self.powerQ += 1
        return str(0)