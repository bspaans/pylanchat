class userPanel:
	
	def __init__(self, treestore):
		self.treestore = treestore
		self.IDs = [];
		
	def add (self, User):
		
		if self.IDs.count(User.ID) == 0:
			if int(User.ID) >= 1000:
				self.IDs.append(User.ID)
				name = self.treestore.append(None, ["  " + User.name])
				self.treestore.append(name, [" ID: " + User.ID])
				self.treestore.append(name, [" Known Since: " + str(User.knownsince)])
	
	def remove(self, user):
		if user.ID in self.IDs:
			self.IDs.remove(user.ID)
			a = self.treestore.get_iter_first()
			while a != None:
				if self.treestore.get_value(a, 0) == "  " + user.name:
					self.treestore.remove(a)
					break
				a = self.treestore.iter_next(a)

	def clear(self):
		self.IDs = []
		self.treestore.clear()

class chanPanel:

	def __init__(self, treestore):
		self.treestore = treestore
		self.channels = [];

	def add(self, chan):
		
		if not (chan.name in self.channels):
			if chan.name != "":
				self.channels.append(chan.name)
				name = self.treestore.append(None, ["  " + chan.name, chan.persons, "Unknown"])
				
	def remove(self, chan):
		if chan.name in self.channels:
			self.channels.remove(chan)
			a = self.treestore.get_iter_first()
			while a != None:
				if self.treestore.get_value(a, 0) == "  " + chan.name:
					self.treestore.remove(a)
					break
				a = self.treestore.iter_next(a)

	def update_persons(self, chan):
		if chan.name in self.channels:
			a = self.treestore.get_iter_first()
			while a != None:
				if self.treestore.get_value(a, 0)[:2+len(chan.name)] == "  " + chan.name:
					self.treestore.set_value(a, 1, chan.persons)
					break
				a = self.treestore.iter_next(a)

	def clear(self):
		self.channels = []
		self.treestore.clear()





