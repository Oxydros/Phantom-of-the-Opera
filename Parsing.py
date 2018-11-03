import re
from enum import Enum

class PLAYER_TYPE(Enum):
      DETECTIVE = 0
      GHOST = 1

class QUESTION_TYPE(Enum):
      ERROR = 0
      TUILES = 1
      POWER = 2
      MOVE = 3

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


## return a dictionnary with the information parsed at the beginning of a turn
    def getInfoTour(self, strInfo) :
      listInfoTourFound = re.findall(r'Tour:(\d*).*Score:(\d*).*Ombre:(\d*).*\[(.*)\]\)\n(.*)', strInfo)
      lastInfoTourFound = listInfoTourFound[-1]
      infoTour =	{
        "Tour": lastInfoTourFound[0],
        "Score": lastInfoTourFound[1],
        "Ombre": lastInfoTourFound[2],
        "Lock" : lastInfoTourFound[3],
        "Tuiles" : lastInfoTourFound[4],
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
    def checkNewQuestion(self, question):
      if (question != self.oldQuestion) :
        self.oldQuestion = question
        return True
      return False

## Return tuiles available from the question (list)
    def parseTuiles(self, question) :
      regex = re.search(r'\[(.*)\]', question)
      tuilesAvailable = regex.group(1).replace(' ', '')
      listTuilesAvailable = tuilesAvailable.split(',')
      listColorTuiles = []
      listPosTuiles = []
      listStateTuiles = []
      for tuile in listTuilesAvailable :
        tuileInfo = tuile.split('-');
        listColorTuiles.append(tuileInfo[0])
        listPosTuiles.append(tuileInfo[1])
        listStateTuiles.append(tuileInfo[2])

      questionParsed = {
        "QuestionType" : QUESTION_TYPE.TUILES,
        "ListColorTuiles" : listColorTuiles,
        "ListPositionTuiles" : listPosTuiles,
        "ListStateTuiles" : listStateTuiles,
      }
      return questionParsed

## Return positions available from the question (list)
    def parsePosition(self, question) :
      regex = re.search(r'\[(.*)\]', question)
      positionsAvailable = regex.group(1).replace(' ', '')
      listPositionsAvailable = positionsAvailable.split(',')
      questionParsed = {
        "QuestionType" : QUESTION_TYPE.MOVE,
        "Data" : listPositionsAvailable,
      }
      return questionParsed

## Return answer available from the question (list)
    def parsePower(self, question) :
      listPowerChoice = [0, 1]
      questionParsed = {
        "QuestionType" : QUESTION_TYPE.POWER,
        "Data" : listPowerChoice,
      }
      return questionParsed

## call the parsing function who match the question
## if forest tmp, just to test
    def findQuestion(self, question) :
      if (question.find('Tuiles') != -1) :
        return self.parseTuiles(question)
      elif (question.find('pouvoir') != -1) :
        return self.parsePower(question)
      elif (question.find('positions') != -1) :
        return self.parsePosition(question)

## Read the info file
    def readInfo(self) :
      file = open(self.infoPath, 'r')
      infos = file.read()
      file.close()
      return self.getInfoTour(infos)

## Read the question file then parse the question
    def readQuestion(self):
      file = open(self.questionsPath, 'r')
      question = file.read()
      file.close()
      if (self.checkNewQuestion(question) == True) :
        return self.findQuestion(question)
      return { "QuestionType" : QUESTION_TYPE.ERROR,
                "Data" : "No new question", }

## Write in the answerFile file
    def writeAnswer(self, answer):
      file = open(self.responsesPath, 'w')
      file.write(answer)
      file.close()

if __name__ == "__main__":
  test = Parser(PLAYER_TYPE.DETECTIVE)
  tmp = test.readInfo()
  print(tmp)