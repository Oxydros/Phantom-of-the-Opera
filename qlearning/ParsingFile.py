import re
import socket
import logging
import queue
import threading
import time
import asyncio
from . import protocol
from . import Parsing
from . import messages
from . import AgentTypes

class Message:
      def __init__(self, type, content):
            self.type = type
            self.content = content

class Parser :
      def __init__(self, player_type, *args):
            self.type = player_type
            self.message_queue = queue.Queue()
            if (player_type == AgentTypes.PLAYER_TYPE.GHOST) :
                  self.responsesPath = './1/reponses.txt'
                  self.questionsPath = './1/questions.txt'
                  self.infoPath = './1/infos.txt'
            else :
                  self.responsesPath = './0/reponses.txt'
                  self.questionsPath = './0/questions.txt'
                  self.infoPath = './0/infos.txt'
            self.tI = threading.Thread(target=self.readInfoFile)
            self.running = True

      def __del__(self):
            self.stop()

      def start(self):
            self.tI.start()

      def stop(self):
            self.running = False
            self.tI.join()
      
      def readMsg(self):
            msg = self.message_queue.get()
            logging.info("Fetching message from queue:")
            logging.info("Type: %s  content: %s"%(msg.type, msg.content))
            return msg

      def sendMsg(self, msg):
            file = open(self.responsesPath, 'w')
            file.write(msg)
            file.close()

      def readInfoFile(self):
            with open(self.infoPath, 'r') as file:
                  while self.running:
                        where = file.tell()
                        lines = file.readlines()
                        if len(lines) == 0:
                              time.sleep(0.05)
                              file.seek(where)
                        else:
                              to_send = []
                              for line in lines:
                                    isQuestion = re.findall(r'QUESTION : (.*)', line)
                                    if len(isQuestion) > 0:
                                          question = isQuestion[0]
                                          newMessage = Message("Question", question)
                                          self.message_queue.put(newMessage)
                                          to_send.clear()
                                          continue
                                    to_send.append(line.strip())
                                    isTour = len(re.findall(r'Tour:', line)) > 0
                                    if isTour:
                                          continue
                                    else:
                                          newMessage = Message("Information", "\n".join(to_send))
                                          self.message_queue.put(newMessage)
                                          to_send.clear()

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
                        "InfoStatus":  AgentTypes.INFO_STATUS.OK,
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
                        "InfoStatus" :  AgentTypes.INFO_STATUS.GHOST,
                        "Data" : ghost[0]
                  }
            infosSuspect = re.findall(r'(.*) a été tiré', data)
            if len(infosSuspect) > 0:
                  if infosSuspect[0] == "fantome":
                        return {
                              "InfoStatus" :  AgentTypes.INFO_STATUS.DRAW_GHOST
                        }
                  tuileInfo = infosSuspect[0].split('-')
                  tuile = {
                        'color': tuileInfo[0],
                        'pos': int(tuileInfo[1]),
                        'state' : tuileInfo[2]
                  }
                  return {
                        "InfoStatus" :  AgentTypes.INFO_STATUS.SUSPECT,
                        "Data": tuile
                  }
            agentTurn = re.findall(r'Tour de (.*)', data)
            if len(agentTurn) > 0:
                  return {
                        "InfoStatus" :  AgentTypes.INFO_STATUS.CHANGE_HAND,
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
                        "InfoStatus" :  AgentTypes.INFO_STATUS.PLACEMENT,
                        "Data": tuile
                  }
            finalScore = re.findall(r'Score final : (.*)', data)
            if len(finalScore) > 0:
                  return {
                        "InfoStatus" :  AgentTypes.INFO_STATUS.FINAL_SCORE,
                        "Data": int(finalScore[0])
                  }
            logging.debug("COULDN'T PARSE!")
            return {
                  "InfoStatus" :  AgentTypes.INFO_STATUS.ERROR,
                  "Data" : 'Nothing Change'
            }

      def parseQuestion(self, question):
            parser = Parsing.Parser(None)
            return parser.findQuestion(question)