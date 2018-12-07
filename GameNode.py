class GameNode:
  def __init__(self, pos, color, sColor, score, used, parent=None):
    self.pos = pos      # a char
    self.color = color
    self.sColor = sColor 
    self.score = score
    self.used = used     # an int
    self.parent = parent  # a node reference
    self.move = ""
    self.child = []    # a list of nodes
    self.power = ""

  def addChild(self, childNode):
    self.children.append(childNode)