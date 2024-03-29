import re
from . import AgentTypes

class Parser :
    oldQuestion = ''
    oldInfoTour = ()
    oldLastPlacement = []
    responsesPath = ''
    questionsPath = ''
    infoPath = ''


    ## Helpful function to 
    def cmp(self, a, b):
      return (a > b) - (a < b) 

    def __init__(self, player_type, *args):
      if (player_type == AgentTypes.PLAYER_TYPE.GHOST) :
        self.responsesPath = './1/reponses.txt'
        self.questionsPath = './1/questions.txt'
        self.infoPath = './1/infos.txt'
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
          "InfoStatus" : AgentTypes.INFO_STATUS.ERROR,
          "Data" : "File is empty",
        }
      lastInfoTourFound = listInfoTourFound[-1]
      if (self.cmp(lastInfoTourFound, self.oldInfoTour) == 0) :
        allNewPlacement = re.findall(r'NOUVEAU PLACEMENT : (.*)', strInfo)
        allNewPlacement.reverse()
        listLastPlacement = self.getLastPlacement(allNewPlacement)
        if (listLastPlacement != self.oldLastPlacement) :
          self.oldLastPlacement = listLastPlacement
          return {
            "InfoStatus" :  AgentTypes.INFO_STATUS.PLACEMENT,
            "Data" : listLastPlacement,
          }
        return {
          "InfoStatus" : AgentTypes.INFO_STATUS.ERROR,
          "Data" : 'Nothing Change'
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
      regex = re.search(r'(\d*), (\d*)', lastInfoTourFound[3])
      lock = {int(regex.group(1)), int(regex.group(2))}
      infoTour =	{
        "InfoStatus": AgentTypes.INFO_STATUS.OK,
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
        "QuestionType" : AgentTypes.QUESTION_TYPE.TUILES,
        "Data" : listColorTuiles,
      }
      return questionParsed

## Return positions available from the question (list)
    def parsePosition(self, question) :
      regex = re.search(r'{(.*)}', question)
      if (regex) :
        positionsAvailable = regex.group(1).replace(' ', '')
        listPositionsAvailable = positionsAvailable.split(',')
        find_color = re.search(r"(.*), positions", question)
        color = None
        if find_color:
              color = find_color.group(0).split(',')[0]
              tuileInfo = color.split('-');
              color = {
                'color': tuileInfo[0],
                'pos': int(tuileInfo[1]),
                'state' : tuileInfo[2]
              }
              return {
                "QuestionType" : AgentTypes.QUESTION_TYPE.P_BLANC,
                "Data" : listPositionsAvailable,
                "Color" : color
              }
        return {
          "QuestionType" : AgentTypes.QUESTION_TYPE.MOVE,
          "Data" : listPositionsAvailable,
          "Color" : color
        }
      return {
        "QuestionType": AgentTypes.QUESTION_TYPE.ERROR,
        "Data" : regex
      }

## Return answer available from the question (list)
    def parsePower(self, question) :
      listPowerChoice = [0, 1]
      questionParsed = {
        "QuestionType" : AgentTypes.QUESTION_TYPE.POWER,
        "Data" : listPowerChoice,
      }
      return questionParsed

    def parseBluePosition(self, question):
          regex = re.search(r'{(.*)}', question)
          if (regex) :
                positionsAvailable = regex.group(1).replace(' ', '')
                listPositionsAvailable = positionsAvailable.split(',')
                questionParsed = {
                  "QuestionType" : AgentTypes.QUESTION_TYPE.P_BLEU,
                  "Data" : listPositionsAvailable,
                }
                return questionParsed
          return {
              "QuestionType": AgentTypes.QUESTION_TYPE.ERROR,
              "Data" : regex
            }


## call the parsing function who match the question
## if forest tmp, just to test
    def findQuestion(self, question) :
      if (question.find('Tuiles') != -1) :
        return self.parseTuiles(question)
      elif (question.find('pouvoir') != -1) :
        return self.parsePower(question)
      elif (question.find('positions') != -1) :
        return self.parsePosition(question)
      elif (question.find("Avec quelle couleur échanger (pas violet!) ?") != -1):
        return {
          "QuestionType" : AgentTypes.QUESTION_TYPE.P_VIOLET,
          "Data" : None
        }
      elif (question.find("Quelle salle obscurcir ?") != -1):
        return {
                  "QuestionType" : AgentTypes.QUESTION_TYPE.P_GRIS,
                  "Data" : None
              }
      elif (question.find("Quelle salle bloquer ?") != -1):
        return {
          "QuestionType" : AgentTypes.QUESTION_TYPE.P_BLEU,
          "Data": None
        }
      elif (question.find("Quelle sortie ?") != -1):
        return self.parseBluePosition(question)
      else :
        return { "QuestionType" : AgentTypes.QUESTION_TYPE.ERROR,
                "Data" : "Unknow Question"}


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
          "InfoStatus" : AgentTypes.INFO_STATUS.END,
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
      return { "QuestionType" : AgentTypes.QUESTION_TYPE.ERROR,
                "Data" : "No new question", }

## Write in the answerFile file
    def writeFileAnswer(self, answer):
      file = open(self.responsesPath, 'w')
      file.write(answer)
      file.close()

if __name__ == "__main__":
  test = Parser(AgentTypes.PLAYER_TYPE.DETECTIVE)
  tmp = test.readInfo()