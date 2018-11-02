from enum import Enum

class IA():
    
    ##Describing the two types of IA
    class IA_TYPE(Enum):
        GHOST = 0,
        DETECTIVE = 1
    
    type = IA_TYPE.GHOST

    def __init__(self, type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = type

    def getIAType(self):
        return type