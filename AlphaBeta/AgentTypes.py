from enum import IntEnum

class PLAYER_TYPE(IntEnum):
      DETECTIVE = 0
      GHOST = 1

class QUESTION_TYPE(IntEnum):
      ERROR = 0
      TUILES = 1
      POWER = 2
      MOVE = 3
      GREY = 4
      VIOLET = 5
      BLUE = 6

class INFO_STATUS(IntEnum):
      ERROR = 0
      OK = 1
      PLACEMENT = 2
      END = 3