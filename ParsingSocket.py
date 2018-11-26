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
                  ghost = re.findall(r'!!! Le fantôme est : (.*)', data)
                  if len(ghost) > 0:
                        return {
                              "InfoStatus" : INFO_STATUS.GHOST,
                              "Data" : ghost[0]
                        }
                  else:
                        return {
                              "InfoStatus" : INFO_STATUS.ERROR,
                              "Data" : 'Nothing Change'
                        }

      def parseQuestion(self, question):
            parser = Parsing.Parser(None)
            return parser.findQuestion(question)