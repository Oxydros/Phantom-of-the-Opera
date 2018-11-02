from enum import Enum

class IA():
    
    ##Describing the two types of IA
    class IA_TYPE(Enum):
        GHOST = 0,
        DETECTIVE = 1
    
    type = IA_TYPE.GHOST

    world = None

    def __init__(self, type, world, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = type
        self.world = world

    def getIAType(self):
        return type

    ## Return the best next pos
    def nextPos(self):
        raise RuntimeError("No method implemented for this IA")

    ## Return the best power choice
    def powerChoice(self):
        raise RuntimeError("No method implemented for this IA")

    ## Return the best tuile selection
    def selectTuile(self, tuiles):
        raise RuntimeError("No method implemented for this IA")