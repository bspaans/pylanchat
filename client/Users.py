import datetime
import time

class Users:
	
	def __init__(self, userPanelObject):
		self.users = []
		self.usersOnline = 0
		self.usersEver = 0
		self.userPanel = userPanelObject
		
	def addUser(self, ID, name, inchat=False, ingame=False):
		newUser = User(ID, name, inchat, ingame)
		self.users.append(newUser)
		self.userPanel.add(newUser)
	
	def getName(self, ID):
		for user in self.users:
			if user.ID == ID:
				return user.name
		return "Unknown User (" + ID + ")";
	
	def removeUser(self, ID):
		name = ""
		for user in self.users:
			if user.ID == ID:
				name = user.name
				self.userPanel.remove(user)
				self.users.remove(user)
	
	def clear(self):
		self.users = []
		self.userPanel.clear()
	
class User:
	
	def __init__(self, ID, name, inchat=False, ingame=False):
		self.ID = ID
		self.name = name
		self.inchat = inchat
		self.ingame = ingame
		t = datetime.datetime.now()
		now = datetime.datetime.fromtimestamp(time.mktime(t.timetuple()))
		self.knownsince = now.ctime()
