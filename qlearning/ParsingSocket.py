import re
import socket
import logging
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
            ghost = re.findall(r'!!! Le fantôme est : (.*)', data)
            if len(ghost) > 0:
                  return {
                        "InfoStatus" : INFO_STATUS.GHOST,
                        "Data" : ghost[0]
                  }
            infosSuspect = re.findall(r'(.*) a été tiré', data)
            if len(infosSuspect) > 0:
                  if infosSuspect[0] == "fantome":
                        return {
                              "InfoStatus" : INFO_STATUS.DRAW_GHOST
                        }
                  tuileInfo = infosSuspect[0].split('-')
                  tuile = {
                        'color': tuileInfo[0],
                        'pos': int(tuileInfo[1]),
                        'state' : tuileInfo[2]
                  }
                  return {
                        "InfoStatus" : INFO_STATUS.SUSPECT,
                        "Data": tuile
                  }
            agentTurn = re.findall(r'Tour de (.*)', data)
            if len(agentTurn) > 0:
                  return {
                        "InfoStatus" : INFO_STATUS.CHANGE_HAND,
                        "Data": agentTurn[0]
                  }
            newPlacement = re.findall(r'NOUVEAU PLACEMENT : (.*)', data)
            if len(newPlacement) > 0:
                  tuileInfo = newPlacement[0].split('-')
                  tuile = [{
                        'color': tuileInfo[0],
                        'pos': int(tuileInfo[1]),
                        'state' : tuileInfo[2]
                  }]
                  return {
                        "InfoStatus" : INFO_STATUS.PLACEMENT,
                        "Data": tuile
                  }
            finalScore = re.findall(r'Score final : (.*)', data)
            if len(finalScore) > 0:
                  return {
                        "InfoStatus" : INFO_STATUS.FINAL_SCORE,
                        "Data": int(finalScore[0])
                  }
            logging.debug("COULDN'T PARSE!")
            return {
                  "InfoStatus" : INFO_STATUS.ERROR,
                  "Data" : 'Nothing Change'
            }

      def parseQuestion(self, question):
            parser = Parsing.Parser(None)
            return parser.findQuestion(question)