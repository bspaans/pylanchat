#file Users.py
from User import User

class Users:
	
	blockednames = []

	def __init__(self):
		self.numUser = 0
		self.users =[]
		self.cID = 1000
	
	def addUser(self):
		ID = self.cID
		self.cID += 1
		self.numUser += 1
		self.users.append(User(ID))
		return ID
	
	def remUser(self, ID):
		for user in self.users:
			if user.ID == ID:
				user.loggedIn = False
				user.online = False
		self.numUser -= 1
	
	def regUsers(self):
		return self.cID - 1000
		
	def addName(self, ID, name):

		# Check for blocked names
		if name in self.blockednames:
			return False

		# Checked for protected names (registered or online)
		for user in self.users:
			if user.name == name and (user.registered or user.loggedIn):
				return False
		for user in self.users:
			if user.ID == ID:
				user.name = name
				user.loggedIn = True
				return True
