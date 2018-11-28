from enum import IntEnum

class PLAYER_TYPE(IntEnum):
      DETECTIVE = 0
      GHOST = 1

class QUESTION_TYPE(IntEnum):
      ERROR = 0
      TUILES = 1
      POWER = 2
      MOVE = 3
      P_VIOLET = 4
      P_BLANC = 5
      P_GRIS = 6
      P_BLEU = 7

class INFO_STATUS(IntEnum):
      ERROR = 0
      OK = 1
      PLACEMENT = 2
      END = 3
      GHOST = 4
      SUSPECT = 5