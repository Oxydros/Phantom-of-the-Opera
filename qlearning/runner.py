import logging
import sys
from . import GameAgent
from . import AgentTypes
from . import ParsingFile
from . import World
import time

# root = logging.getLogger()
# root.setLevel(logging.DEBUG)

hand_name = ["l'inspecteur", "le fantome"]
class GameRunner(object):
	previous_question = None
	current_hand = None

	def __init__(self, agentType):
		self.type = agentType

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
		if infoData['InfoStatus'] == AgentTypes.INFO_STATUS.CHANGE_HAND:
			new_hand = infoData["Data"]
			logging.debug("Change hand from %s to %s", self.current_hand, new_hand)
			self.current_hand = new_hand
			self._triggetNextState(world, gameAgent)
			if new_hand == hand_name[agentType]:
				world.setCurrentPlayedColor('none')
		if infoData['InfoStatus'] == AgentTypes.INFO_STATUS.OK:
			if msgContent.find("Rappel des positions :") == -1 and infoData.get('Tour', None) != None:
				self._triggetNextState(world, gameAgent)
			logging.debug("Got info TOUR %s"%(infoData))
			world.setStatus(infoData)
			# ##Check if a new tour is starting
			# ## to do so, check if the msg content is not violet power
			# ##Notify agent to calcuate reward of previous tour
			# if msgContent.find("Rappel des positions :") == -1 and infoData.get('Tour', None) != None:
			# 	gameAgent.endOfHalfTour(world)
		elif infoData['InfoStatus'] == AgentTypes.INFO_STATUS.PLACEMENT:
			logging.debug("Got info PLACEMENT %s"%(infoData))
			world.updateTuiles(infoData['Data'])
		elif infoData['InfoStatus'] == AgentTypes.INFO_STATUS.GHOST:
			if agentType == AgentTypes.PLAYER_TYPE.DETECTIVE:
				raise RuntimeError("Received ghost but I am detective !")
			logging.debug("Got info GHOST %s"%(infoData))
			world.setGhostColor(infoData['Data'])
		elif infoData['InfoStatus'] == AgentTypes.INFO_STATUS.SUSPECT:
			world.setInnocentColor(infoData['Data']['color'])
		elif infoData['InfoStatus'] == AgentTypes.INFO_STATUS.DRAW_GHOST:
			logging.debug("Draw FANTOME")
		elif infoData['InfoStatus'] == AgentTypes.INFO_STATUS.FINAL_SCORE:
			self._triggetNextState(world, gameAgent)
			finalScore = infoData['Data']
			if agentType == AgentTypes.PLAYER_TYPE.GHOST:
				gameAgent.reward(-1 if finalScore > 0 and finalScore < 22 else 1)
			elif agentType == AgentTypes.PLAYER_TYPE.DETECTIVE:
				gameAgent.reward(1 if finalScore > 0 and finalScore < 22 else -1)

	## Process a question send by the server
	def processQuestions(self, parser, world, msg, gameAgent):
		if self.current_hand != None and self.current_hand != hand_name[self.type]:
			logging.info("NOT MY TURN (%s). SKIPPING PARSING OF QUESTION"%(hand_name[self.type]))
			return
		#Parse question
		questionData = parser.parseQuestion(msg.content)
		questionType = questionData["QuestionType"]
		answer = None

		logging.debug("Got question %s"%(questionData))

		#Update world if there is any new informations
		world.updateState(questionData)

		self._triggetNextState(world, gameAgent)

		if questionType == AgentTypes.QUESTION_TYPE.MOVE:
			answer = gameAgent.nextCurrentColorPos(world, questionData["Data"])
		elif questionType == AgentTypes.QUESTION_TYPE.POWER:
			answer = gameAgent.powerChoice(world)
		elif questionType == AgentTypes.QUESTION_TYPE.TUILES:
			answer = gameAgent.selectTuile(world, questionData["Data"])
		elif questionType == AgentTypes.QUESTION_TYPE.P_BLANC:
			answer = gameAgent.nextPosColorWhitePower(world, questionData["Color"],
			questionData["Data"])
		elif questionType == AgentTypes.QUESTION_TYPE.P_VIOLET:
			answer = gameAgent.selectTuileVioletPower(world)
		elif questionType == AgentTypes.QUESTION_TYPE.P_GRIS:
			answer = gameAgent.nextPosBlackRoom(world)
		elif questionType == AgentTypes.QUESTION_TYPE.P_BLEU:
			answer = gameAgent.nextBlockedPathBluePower(world,
			questionData["Data"])
		elif questionType == AgentTypes.QUESTION_TYPE.ERROR:
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
				infoData = parser.parseInfo(msg.content)
				self.updateInfos(agentType, world, gameAgent, infoData, msg.content)
				if infoData['InfoStatus'] == AgentTypes.INFO_STATUS.FINAL_SCORE:
    					return "Detected END TOUR"
			elif msgType == "Question":
				self.processQuestions(parser, world, msg, gameAgent)
		return "Unknown"

def lancer(agentType, smart=True, training=False):
	# ch = logging.StreamHandler(sys.stdout)
	# ch.setLevel(logging.CRITICAL)
	# formatter = logging.Formatter('%(asctime)s - '+ hand_name[agentType] +' - %(levelname)s - %(message)s')
	# ch.setFormatter(formatter)
	# root.addHandler(ch)
	world = World.World()
	parser = ParsingFile.Parser(agentType)
	gameAgent = None
	if smart:
			gameAgent = GameAgent.SmartGameAgent(agentType, training=training)
	else:
		gameAgent = GameAgent.GameAgent()
	runner = GameRunner(agentType)
	runner.resetRunner()
	parser.start()
	result = runner.loop(world, parser, gameAgent, agentType)
	logging.debug("Got result from game %s"%(result))
	parser.stop()