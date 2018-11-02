import re
from enum import Enum

class PLAYER_TYPE(Enum):
      DETECTIVE = 0
      GHOST = 1

class Parser :
    oldQuestion = ''
    responsesPath = ''
    questionsPath = ''
    infoPath = ''

    def __init__(self, player_type, *args):
      if (player_type == PLAYER_TYPE.GHOST) :
        self.responsePath = './1/responses.txt'
        self.questionsPath = './1/questions.txt'
        self.infoPath = './1/infos.txt'
        self.getGhost()
      else :
        self.responsePath = './0/responses.txt'
        self.questionsPath = './0/questions.txt'
        self.infoPath = './0/infos.txt'

    def getInfoTour(self, strInfo) :
      infoTourFound = re.search(r'\Tour:(\d*).*Score:(\d*).*Ombre:(\d*).*\[(.*)\]\)\n(.*)', strInfo)
      infoTour =	{
        "Tour": infoTourFound.group(1),
        "Score": infoTourFound.group(2),
        "Ombre": infoTourFound.group(3),
        "Lock" : infoTourFound.group(4),
        "Tuiles" : infoTourFound.group(5),
      }
      return infoTour


## get the Ghost color
    def getGhost(self) :
      file = open(self.infoPath)
      ghostColorLine = file.readline()
      ghostColor = re.search(r': (.*)', ghostColorLine)
      file.close()
      return (ghostColor.group(1))                                         

## check if there is a new question
    def checkNewQuestion(self):
      question = self.readQuestion()
      if (question != self.oldQuestion) :
        oldQuestion = question
        return True
      return False

## Return tuiles available from the question (list)
    def parseTuiles(self, question) :
      regex = re.search(r'\[(.*)\]', question)
      tuilesAvailable = regex.group(1).replace(' ', '')
      listTuilesAvailable = tuilesAvailable.split(',')
      return listTuilesAvailable

## Return positions available from the question (list)
    def parsePosition(self, question) :
      regex = re.search(r'\[(.*)\]', question)
      positionsAvailable = regex.group(1).replace(' ', '')
      listPositionsAvailable = positionsAvailable.split(',')
      return listPositionsAvailable
  
## call the parsing function who match the question
## if forest tmp, just to test
    def findQuestion(self, question) :
      if (question.find('Tuiles') != -1) :
        self.parseTuiles(question)
      elif (question.find('pouvoir') != -1) :
        self.parseTuiles(question)
      elif (question.find('positions') != -1) :
        self.parsePosition(question)

    def readInfo(self) :
      file = open(self.infoPath, 'r')
      infos = file.read()
      file.close()
      return infos

## Read the question file
    def readQuestion(self):
      file = open(self.questionsPath, 'r')
      question = file.read()
      file.close()
      return question

## Write in the answerFile file
    def writeAnswer(self, answer):
      file = open(self.responsesPath, 'w')
      file.write(answer)
      file.close()

if __name__ == "__main__":
  test = Parser(PLAYER_TYPE.GHOST)