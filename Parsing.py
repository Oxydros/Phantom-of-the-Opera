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

class INFO_STATUS(Enum):
      ERROR = 0
      OK = 1
      PLACEMENT = 2
      END = 3

class Parser :
    oldQuestion = ''
    oldInfoTour = ()
    responsesPath = ''
    questionsPath = ''
    infoPath = ''


    ## Helpful function to 
    def cmp(self, a, b):
      return (a > b) - (a < b) 

    def __init__(self, player_type, *args):
      if (player_type == PLAYER_TYPE.GHOST) :
        self.responsesPath = './1/reponses.txt'
        self.questionsPath = './1/questions.txt'
        self.infoPath = './1/infos.txt'
        self.getGhost()
      else :
        self.responsesPath = './0/reponses.txt'
        self.questionsPath = './0/questions.txt'
        self.infoPath = './0/infos.txt'


##DOIS PARSER NOUVEAU PLACEMENT

    def getLastPlacement(self, allNewPlacement) :
      colourFound = []
      lastNewPlacement = []
      for newPlacement in allNewPlacement :
        newPlacementTab = newPlacement.split('-');
        if newPlacementTab[0] not in colourFound :
          lastNewPlacement.append({
            'color': newPlacementTab[0],
            'pos': int(newPlacementTab[1]),
            'state' : newPlacementTab[2]
          })
          colourFound.append(newPlacementTab[0])
      return lastNewPlacement


## return a dictionnary with the information parsed at the beginning of a turn
    def getInfoTour(self, strInfo) :
      listInfoTourFound = re.findall(r'Tour:(\d*).*Score:(\d*).*Ombre:(\d*).*\{(.*)}\n(.*)', strInfo)
      if (len(listInfoTourFound) == 0) :
        return {
          "InfoStatus" : INFO_STATUS.ERROR,
          "Data" : "File is empty",
        }
      lastInfoTourFound = listInfoTourFound[-1]
      if (self.cmp(lastInfoTourFound, self.oldInfoTour) == 0) :
        allNewPlacement = re.findall(r'NOUVEAU PLACEMENT : (.*)', strInfo)
        allNewPlacement.reverse()
        listLastPlacement = self.getLastPlacement(allNewPlacement)
        return {
          "InfoStatus" : INFO_STATUS.PLACEMENT,
          "Data" : listLastPlacement,
        }
      listTuilesAvailable = lastInfoTourFound[4].split('  ')
      listTuiles = []
      for tuile in listTuilesAvailable :
        tuileInfo = tuile.split('-');
        listTuiles.append({
          'color': tuileInfo[0],
          'pos': int(tuileInfo[1]),
          'state' : tuileInfo[2]
        })
      print("LAST INF ", lastInfoTourFound[3])
      regex = re.search(r'(\d*), (\d*)', lastInfoTourFound[3])
      lock = {int(regex.group(1)), int(regex.group(2))}
      infoTour =	{
        "InfoStatus": INFO_STATUS.OK,
        "Tour": int(lastInfoTourFound[0]),
        "Score": int(lastInfoTourFound[1]),
        "Ombre": int(lastInfoTourFound[2]),
        "Lock" : lock,
        "Tuiles" : listTuiles,
      }
      self.oldInfoTour = lastInfoTourFound
      return infoTour

## get the Ghost color
    def getGhost(self) :
      file = open(self.infoPath)
      ghostColorLine = file.readline()
      ghostColor = re.search(r': (.*)', ghostColorLine)
      file.close()
      if (ghostColor) :
        return (ghostColor.group(1))
      return 'No Color'                                         

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
      for tuile in listTuilesAvailable :
        tuileInfo = tuile.split('-');
        listColorTuiles.append({
          'color': tuileInfo[0],
          'pos': int(tuileInfo[1]),
          'state' : tuileInfo[2]
        })

      questionParsed = {
        "QuestionType" : QUESTION_TYPE.TUILES,
        "Data" : listColorTuiles,
      }
      return questionParsed

## Return positions available from the question (list)
    def parsePosition(self, question) :
      regex = re.search(r'{(.*)}', question)
      if (regex) :
        positionsAvailable = regex.group(1).replace(' ', '')
        listPositionsAvailable = positionsAvailable.split(',')
        questionParsed = {
          "QuestionType" : QUESTION_TYPE.MOVE,
          "Data" : listPositionsAvailable,
        }
        return questionParsed
      return {
        "QuestionType": QUESTION_TYPE.ERROR,
        "Data" : regex
      }

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


    def checkEndOfGame(self, infostr) :
      regex = re.search(r'Score final', infostr)
      if(regex) :
        return True
      return False

## Read the info file
    def readInfo(self) :
      file = open(self.infoPath, 'r')
      infos = file.read()
      file.close()
      if (self.checkEndOfGame(infos) == True) :
        return {
          "InfoStatus" : INFO_STATUS.END,
          "Data" : 'The game is over',
        }
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
      print(self.responsesPath)
      file = open(self.responsesPath, 'w')
      file.write(answer)
      file.close()

if __name__ == "__main__":
  test = Parser(PLAYER_TYPE.DETECTIVE)
  tmp = test.readInfo()
  print(tmp)