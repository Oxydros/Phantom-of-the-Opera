import re
import copy
import threading
from enum import Enum
import multiprocessing
from GameNode import GameNode


DEF_ALLOWED_PATH = [{1,4}, {0,2}, {1,3}, {2,7}, {0,5,8}, {4,6}, {5,7}, {3,6,9}, {4,9}, {7,8}]
ROSE_ALLOWED_PATH = [{1,4}, {0,2,5,7}, {1,3,6}, {2,7}, {0,5,8,9}, {4,6,1,8}, {5,7,2,9}, {3,6,9,1}, {4,9,5}, {7,8,4,6}]
POWER_PERMANENT = {'rose'}
POWER_BEFORE = {"violet", "marron"}
POWER_AFTER = {"noir" , "blanc"}
POWER_BOTH = {"rouge", "gris", "bleu"}

class GameTree :
  
  def newDico(self, copyDico) :
    dictio = GameNode(copy.deepcopy(copyDico.pos), copy.deepcopy(copyDico.color), copyDico.sColor, copy.copy(copyDico.score), copy.copy(copyDico.used))
    return (dictio)

  def findListIndex(self, color, allPos) :
    for index, listPos in enumerate(allPos) :
      if (listPos[0] == color) :
        return index

  def findPos(self, color, allPos) :
    for listPos in allPos :
      if (listPos[0] == color) :
        for index, isIn in enumerate(listPos) :
          if (isIn == 1) :
            return index - 1

  def getLocked_path(self, listLockPos) :
    locked_path = []
    for index, isIn in enumerate(listLockPos) :
      if (len(locked_path) == 2) :
        return locked_path
      if (isIn == 1) :
        locked_path.append(index - 1)

  def getPossibleDeplacementFromPos(self, infos):
    color = infos.sColor
    cPos = self.findPos(color, infos.pos);
    
    possible = copy.deepcopy(DEF_ALLOWED_PATH if color != "rose" else ROSE_ALLOWED_PATH)
    possible = possible[cPos]
    locked_path = self.getLocked_path(infos.pos[9])

    try:
        possible.remove(locked_path[0])
    except KeyError:
        pass
    try:
        possible.remove(locked_path[1])
    except KeyError:
        pass
    return possible
      
  def chooseColor(self, infos) :
    color_copy = list(infos.color)
    for color in color_copy :
      infos_copy = self.newDico(infos)
      infos_copy.sColor = color
      infos_copy.color.remove(color)
      infos_copy.parent = infos
      infos.child.append(infos_copy)

    return infos

  def blackPower(self, infos_child) :
    possibleMove = self.getPossibleDeplacementFromPos(infos_child)
    cPos = self.findPos(infos_child.sColor, infos_child.pos) + 1;
    for move in possibleMove :
      for index, line in enumerate(infos_child.pos) :
        if (line[move + 1] == 1) :
          infos_child.pos[index][move + 1] = 0
          infos_child.pos[index][cPos] = 1
    return infos_child

  def greyPower(self, infos_child, i) :
    for index, room in enumerate(infos_child.pos[8]) :
      if (room == 1) :
        infos_child.pos[8][index] == 0
      if (index == i) :
        infos_child.pos[8][index] == 1
    infos_child.power = str(i - 1)
    return infos_child

  def violetPower(self, infos_child, i) :
    if (infos_child.pos[i][0] == "violet") :
      return "violet"
    listIndex = self.findListIndex("violet", infos_child.pos)
    actualPosIndex = self.findPos(infos_child.pos[i][0], infos_child.pos)
    actualVioletIndex = self.findPos("violet", infos_child.pos)
    infos_child.pos[listIndex][actualVioletIndex + 1] = 0
    infos_child.pos[listIndex][actualPosIndex + 1] = 1
    infos_child.pos[i][actualVioletIndex + 1] = 1
    infos_child.pos[i][actualPosIndex + 1] = 1
    infos_child.power = infos_child.pos[i][0]
    return (infos_child)

#need refacto
  def getPath(self, i) :
    if i == 0 :
      return [0, 1]
    if i == 1 :
      return [1, 2]
    if i == 2 :
      return [2, 3]
    if i == 3 :
      return [0, 4]
    if i == 4 :
      return [4, 5]
    if i == 5 :
      return [5, 6]
    if i == 6 :
      return [6, 7]
    if i == 7 :
      return [3, 7]
    if i == 8 :
      return [4, 8]
    if i == 9 :
      return [7, 9]
    if i == 10 :
      return [8, 9]

  def bluePower(self, infos_child, i) :
    locked_path = self.getLocked_path(infos_child.pos[9])
    newLock = self.getPath(i)
    if ((newLock[0] == locked_path[0] or newLock[0] == locked_path[1]) and
    (newLock[1] == locked_path[0] or newLock[1] == locked_path[1])) :
      return "bleu"
    infos_child.pos[9][locked_path[0] + 1] = 0
    infos_child.pos[9][locked_path[1] + 1] = 0
    infos_child.pos[9][newLock[0] + 1] = 1
    infos_child.pos[9][newLock[1] + 1] = 1
    infos_child.power = newLock
    return infos_child

  def redPower(self, infos_child, i) :
    if (i == 8) :
      infos_child.score = infos_child.score - 1
      return infos_child
    if (infos_child.pos[i][11] == 0) :
      return "rouge"
    infos_child.pos[i][11] = 0
    return infos_child

  def marronPower(self, infos_copy, actualPosIndex, move) :
    for index in range(8) :
      if infos_copy.pos[index][actualPosIndex] == 1 :
        infos_copy.pos[index][actualPosIndex] = 0
        infos_copy[index][move] = 1
    return infos_copy

  def usePowserAfter(self, infos) :
    if (infos.sColor in POWER_PERMANENT or infos.sColor in POWER_BEFORE) :
      infos_child = self.newDico(infos)
      infos_child.parent = infos
      infos.child.append(infos_child)
      return infos
    i = 0
    while (i != 2) :
      infos_child = self.newDico(infos)
      if (i == 0) :
        if (infos.sColor == "gris") :
          for cpt in range(1) :
            infos_child = self.newDico(infos)
            infos_child.used = True
            infos_child = self.greyPower(infos_child, cpt + 1)
            infos_child.parent = infos
            infos.child.append(infos_child)
        if (infos.sColor == "rouge") :
          for cpt in range(9) :
            infos_child = self.newDico(infos)
            infos_child.used = True
            infos_child = self.redPower(infos_child, cpt)
            if (infos_child != "rouge") :
              infos_child.parent = infos
              infos.child.append(infos_child)
    #     if (infos.sColor == "bleu") :
    #       for cpt in range(1) :
    #         infos_child = self.newDico(infos)
    #         infos_child.used = True
    #         infos_child = self.bluePower(infos_child, cpt)
    #         if (infos_child != "bleu") :
    #           infos_child.parent = infos
    #           infos.child.append(infos_child)
      else :
        infos_child.used = False
        infos_child.parent = infos
        infos.child.append(infos_child)
      i = i + 1

    return infos

  def usePowserBefore(self, infos) :

    infos_child = self.newDico(infos)
    infos_child.parent = infos
    infos.child.append(infos_child)
    return infos
    i = 0
    while (i != 2) :
      infos_child = self.newDico(infos)
      if (i == 0) :
        if (infos.sColor == "violet") :
          for cpt in range(8) :
            infos_child = self.newDico(infos)
            infos_child.used = True
            infos_child = self.violetPower(infos_child, cpt)
            if (infos_child != "violet") :
              infos_child.parent = infos
              infos.child.append(infos_child)
        if (infos.sColor == "gris") :
          for cpt in range(1) :
              infos_child = self.newDico(infos)
              infos_child.used = True
              infos_child = self.greyPower(infos_child, cpt + 1)
              infos_child.parent = infos
              infos.child.append(infos_child)
        if (infos.sColor == "rouge") :
          for cpt in range(9) :
            infos_child = self.newDico(infos)
            infos_child.used = True
            infos_child = self.redPower(infos_child, cpt)
            if (infos_child != "rouge") :
              infos_child.parent = infos
              infos.child.append(infos_child)
        if (infos.sColor == "bleu") :
          for cpt in range(1) :
            infos_child = self.newDico(infos)
            infos_child.used = True
            infos_child = self.bluePower(infos_child, cpt)
          if (infos_child != "bleu") :
            infos_child.parent = infos
            infos.child.append(infos_child)
      else :
        infos_child.used = False
        infos_child.parent = infos
        infos.child.append(infos_child)
      i = i + 1

    return infos

  def moveIt(self, infos) :
  
    possibleMove = self.getPossibleDeplacementFromPos(infos)
    for move in possibleMove :
      infos_copy = self.newDico(infos)
      listIndex = self.findListIndex(infos_copy.sColor, infos_copy.pos)
      actualPosIndex = self.findPos(infos_copy.sColor, infos_copy.pos)
      infos_copy.pos[listIndex][actualPosIndex + 1] = 0
      infos_copy.pos[listIndex][move + 1] = 1
      infos_copy.parent = infos
      infos_copy.move = move;
      infos.child.append(infos_copy)

    return infos

  def calculScream(self, infos) :
    copyScream = self.newDico(infos);
    i = 1
    while (i != 11) :
      cpt = 0
      for index, room in enumerate(copyScream.pos) :
        if (index < 8) :
          cpt = cpt + room[i]
      if (cpt > 1 and copyScream.pos[8][i] == 0) :
        for index, room in enumerate(copyScream.pos) :
          if (index < 8 and room[i] == 1) :
            room[11] = 0
      i = i + 1

    nbSuspect = 0
    for room in copyScream.pos :
      nbSuspect = nbSuspect + room[11]
    copyScream.score = copyScream.score + 1 + nbSuspect
    return copyScream

  def calculNotScream(self, infos) :
    copyNotScream = self.newDico(infos);
    i = 1
    while (i != 11) :
      cpt = 0
      for index, room in enumerate(copyNotScream.pos) :
        if (index < 8) :
          cpt = cpt + room[i]
      if (cpt < 2 or copyNotScream.pos[8][i] == 1) :
        for index, room in enumerate(copyNotScream.pos) :
          if (index < 8 and room[i] == 1) :
            room[11] = 0
      i = i + 1

    nbSuspect = 0
    for room in copyNotScream.pos :
      nbSuspect = nbSuspect + room[11]
    copyNotScream.score = copyNotScream.score + nbSuspect
    return copyNotScream

  def scoreCalcul(self, infos) :
    copyScream = self.calculScream(infos)
    copyNotScream = self.calculNotScream(infos)

    copyScream.parent = infos
    copyNotScream.parent = infos
    infos.child.append(copyScream);
    infos.child.append(copyNotScream);

    return infos

  def doGameTree(self, root) :
    root = self.chooseColor(root)
    root_children = root.child
    for nodeTuile in root_children :
      nodeTuile = self.usePowserBefore(nodeTuile)
      tuile_children = nodeTuile.child
      for nodePowerBefore in tuile_children :
        nodePowerBefore = self.moveIt(nodePowerBefore)
        before_children = nodePowerBefore.child
        for nodeMove in before_children :
          nodeMove = self.usePowserAfter(nodeMove)
          move_children = nodeMove.child
          jobs = []
          for index, nodePowerAfter in enumerate(move_children) :
            out_list = list()
            if (len(nodePowerAfter.color) != 0) :
              nodePowerAfter.used = False
              nodePowerAfter = (self.doGameTree2(nodePowerAfter)).child
            else :
              nodePowerAfter.score = self.scoreCalcul(nodePowerAfter)
    return root
