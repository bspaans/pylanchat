#file Messages.py
class Messages:
	def __init__(self):
		self.messages = []
		self.privateMessages = []
		
	def addmsg(self, msg):
		self.messages.append(msg)
		
	def length(self):
		return len(self.messages)
		
	def addPrivateMessage(self, msg, to):
		self.privateMessages.append([msg, to])
