class Channels:

	def __init__(self, panel):
		self.channels = []
		self.panel = panel

	def addChannel(self, name, persons = 1):
		newchan = Channel(name, persons)
		self.channels.append(newchan)
		self.panel.add(newchan)

	def update_persons(self, name, diff):
		for n in self.channels:
			if n.name == name:
				n.update_persons(diff)
				self.panel.update_persons(n)

	def clear(self):
		self.channels = []
		self.panel.clear()

class Channel:

	def __init__(self, name, persons = 1):
		self.name = name
		self.persons = int(persons)

	def update_persons(self, diff):
		self.persons += diff

