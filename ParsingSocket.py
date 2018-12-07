import re
import socket
import protocol
import messages
import Parsing
from AgentTypes import PLAYER_TYPE, QUESTION_TYPE, INFO_STATUS

class Parser :
      
      def __init__(self, player_type, *args):
            self.type = player_type
            
      def initNetwork(self):
            self.link = socket.socket(socket.AF_INET,
            socket.SOCK_STREAM)
            self.link.connect(('127.0.0.1', 4242))
      
      def readMsg(self):
            r = protocol.recv_one_message(self.link)
            r = messages.deserialize(r)
            return r

      def sendMsg(self, msg):
            r = messages.Response(msg)
            protocol.send_one_message(self.link, r.toJson())

      def parseInfo(self, data):
            infosTour = re.findall(r'Tour:(\d*).*Score:(\d*).*Ombre:(\d*).*\{(.*)}\n(.*)', data)
            if (len(infosTour) > 0):
                  lastInfoTourFound = infosTour[-1]
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
                        "InfoStatus": INFO_STATUS.OK,
                        "Tour": int(lastInfoTourFound[0]),
                        "Score": int(lastInfoTourFound[1]),
                        "Ombre": int(lastInfoTourFound[2]),
                        "Lock" : lock,
                        "Tuiles" : listTuiles,
                  }
                  return infoTour
            else:
                  print("GOT UNKNWOWN DATA %s"%(data))
                  return {
                        "InfoStatus" : INFO_STATUS.ERROR,
                        "Data" : 'Nothing Change'
                  }

      def parseQuestion(self, question):
            parser = Parsing.Parser(None)
            if (question.find('Tuiles') != -1) :
                  return parser.parseTuiles(question)
            elif (question.find('pouvoir') != -1) :
                return parser.parsePower(question)
            elif (question.find('positions') != -1) :
                  return parser.parsePosition(question)
            elif (question.find('obscurcir') != -1) :
                  questionParsed = {
                        "QuestionType" : QUESTION_TYPE.GREY,
                  }
                  return questionParsed
            elif (question.find('échanger') != -1) :
                  questionParsed = {
                        "QuestionType" : QUESTION_TYPE.VIOLET,
                  }
                  return questionParsed
            elif (question.find("bloquer") != - 1 or question.find("sortie") != - 1) :
                  questionParsed = {
                        "QuestionType" : QUESTION_TYPE.BLUE,
                        "Data": question
                  }
                  return questionParsed
            else :
                  return { "QuestionType" : QUESTION_TYPE.ERROR,
                        "Data" : "Unknow Question"}