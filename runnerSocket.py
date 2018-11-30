import logging
import sys
from GameAgent import SmartGameAgent, GameAgent
from AgentTypes import PLAYER_TYPE, QUESTION_TYPE, INFO_STATUS
from ParsingSocket import Parser
from World import World
import time
from threading import Thread

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

hand_name = ["l'inspecteur", "le fantome"]
class GameRunner(object):
		
	previous_question = None
	current_hand = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def _triggetNextState(self, world, gameAgent):
		#Feed the new state to the previous question
		if self.previous_question != None:
				logging.debug("TRIGGER NEXT STATE UPDATE")
				gameAgent.triggerNextState(world, self.previous_question)
				self.previous_question = None
		else:
				logging.debug("NO PREVIOUS QUESTION. SKIPPING NEXT STATE TRIGGER")

	def resetRunner(self):
			self.previous_question = None
			self.current_hand = None

	## Process informations send by the server
	def updateInfos(self, agentType, world, gameAgent, infoData, msgContent):
		if infoData['InfoStatus'] == INFO_STATUS.OK:
			if msgContent.find("Rappel des positions :") == -1 and infoData.get('Tour', None) != None:
				self._triggetNextState(world, gameAgent)
			logging.debug("Got info TOUR %s"%(infoData))
			world.setStatus(infoData)
			# ##Check if a new tour is starting
			# ## to do so, check if the msg content is not violet power
			# ##Notify agent to calcuate reward of previous tour
			# if msgContent.find("Rappel des positions :") == -1 and infoData.get('Tour', None) != None:
			# 	gameAgent.endOfHalfTour(world)
		elif infoData['InfoStatus'] == INFO_STATUS.PLACEMENT:
			logging.debug("Got info PLACEMENT %s"%(infoData))
			world.updateTuiles(infoData['Data'])
		elif infoData['InfoStatus'] == INFO_STATUS.GHOST:
			if agentType == PLAYER_TYPE.DETECTIVE:
				raise RuntimeError("Received ghost but I am detective !")
			logging.debug("Got info GHOST %s"%(infoData))
			world.setGhostColor(infoData['Data'])
		elif infoData['InfoStatus'] == INFO_STATUS.SUSPECT:
			world.setInnocentColor(infoData['Data']['color'])
		elif infoData['InfoStatus'] == INFO_STATUS.CHANGE_HAND:
			new_hand = infoData["Data"]
			logging.debug("Change hand from %s to %s", self.current_hand, new_hand)
			self.current_hand = new_hand
			self._triggetNextState(world, gameAgent)
			if new_hand == hand_name[agentType]:
				world.setCurrentPlayedColor('none')
		elif infoData['InfoStatus'] == INFO_STATUS.DRAW_GHOST:
			logging.debug("Draw FANTOME")
		elif infoData['InfoStatus'] == INFO_STATUS.FINAL_SCORE:
			self._triggetNextState(world, gameAgent)
			finalScore = infoData['Data']
			if agentType == PLAYER_TYPE.GHOST:
				gameAgent.reward(-1 if finalScore > 0 and finalScore < 22 else 1)
			elif agentType == PLAYER_TYPE.DETECTIVE:
				gameAgent.reward(1 if finalScore > 0 and finalScore < 22 else -1)
					

	## Process a question send by the server
	def processQuestions(self, parser, world, msg, gameAgent):
		#Parse question
		questionData = parser.parseQuestion(msg.content)
		questionType = questionData["QuestionType"]
		answer = None

		logging.debug("Got question %s"%(questionData))

		#Update world if there is any new informations
		world.updateState(questionData)

		self._triggetNextState(world, gameAgent)

		if questionType == QUESTION_TYPE.MOVE:
			answer = gameAgent.nextCurrentColorPos(world, questionData["Data"])
		elif questionType == QUESTION_TYPE.POWER:
			answer = gameAgent.powerChoice(world)
		elif questionType == QUESTION_TYPE.TUILES:
			answer = gameAgent.selectTuile(world, questionData["Data"])
		elif questionType == QUESTION_TYPE.P_BLANC:
			answer = gameAgent.nextPosColorWhitePower(world, questionData["Color"],
														questionData["Data"])
		elif questionType == QUESTION_TYPE.P_VIOLET:
			answer = gameAgent.selectTuileVioletPower(world)
		elif questionType == QUESTION_TYPE.P_GRIS:
			answer = gameAgent.nextPosBlackRoom(world)
		elif questionType == QUESTION_TYPE.P_BLEU:
			answer = gameAgent.nextBlockedPathBluePower(world,
														questionData["Data"])
		elif questionType == QUESTION_TYPE.ERROR:
			raise ValueError("Unknown question " + msg.content)

		logging.debug("Sending answer %s"%(answer))
		parser.sendMsg(answer)
		self.previous_question = questionType

	## Game loop
	def loop(self, world, parser, gameAgent, agentType):
		while (True):
			msg = parser.readMsg()
			msgType = msg.type
			if msgType == "Information":
				logging.debug("MSG INFO: " + msg.content)
				if msg.content == "ResetGame" or msg.content == "EndGame":
					# assert(False)
					return msg.content
				infoData = parser.parseInfo(msg.content)
				if infoData['InfoStatus'] == INFO_STATUS.END:
					return "Detected END TOUR"
				self.updateInfos(agentType, world, gameAgent, infoData, msg.content)
			elif msgType == "Question":
				self.processQuestions(parser, world, msg, gameAgent)
		return "Unknown"

def lancer(agentType, smart=True):
	logging.info("Launching %s IA"%(agentType))
	parser = Parser(agentType)
	logging.info("Init network...")
	parser.initNetwork()
	logging.info("Done!")
	gameAgent = None
	if smart:
		gameAgent = SmartGameAgent(agentType)
	else:
		gameAgent = GameAgent()
	runner = GameRunner()
	while True:
		world = World()
		runner.resetRunner()
		result = runner.loop(world, parser, gameAgent, agentType)        
		logging.debug("Got result from game %s"%(result))
		if result == "EndGame":
			break
			