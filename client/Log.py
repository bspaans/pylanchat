import time
from clientVars import *
from privateMessage import *
import os

class Log:
	pid = 0;


	def __init__(self, textbuffer, view, msgObject):
		self.textbuffer = textbuffer
		self.view = view
		self.view.set_buffer(self.textbuffer)
		self.privateLogs = []
		self.messages = msgObject
		self.icon_width = 12
		self.icon_height = 12

		self.emoticons = {\
				":)" : self.load_img("icon_smile.gif"),
				";)" : self.load_img("icon_wink.gif"),
				":D" : self.load_img("icon_lol.gif"),
				"8)" : self.load_img("icon_cool.gif"),
				":'(" : self.load_img("icon_cry.gif"),
				":(" : self.load_img("icon_sad.gif"),
				":P" : self.load_img("icon_razz.gif"),
				":O" : self.load_img("icon_eek.gif"),
				":$" : self.load_img("icon_redface.gif"),
				">(" : self.load_img("icon_mad.gif"),
			}

	def load_img(self, location):
		loc = os.path.join("gif", location)
		return gtk.gdk.pixbuf_new_from_file_at_size(\
			loc, self.icon_width, self.icon_height)
		
	def dumplog(self):
		##save??
		self.pid = self.pid + 1
		
	def log(self, msg, style = LOG_INFO):
		
		if style == LOG_INFO: 
			color = "gray"
		elif style == LOG_RECV: 
			color = "black"
		elif style == LOG_SEND: 
			color = "orange"
		elif style == LOG_ERR: 
			color = "red"
		elif style == LOG_CONN: 
			color = "gray"
		elif style == LOG_SERVER:
			color = "blue"
		elif style == LOG_MSG:
			color = "orange"
		elif style == LOG_PM_SENT:
			color = "blue"
		elif style == LOG_PM_RECV:
			color = "black"
		
		iter = self.textbuffer.get_end_iter()
		offset = iter.get_offset()
		if style == LOG_MSG:
			self.parse_Message(msg)
			iter = self.textbuffer.get_end_iter()
			self.textbuffer.insert(iter, "\n")
		elif style == LOG_PM_RECV:
			self.textbuffer.insert(iter, ">>> "  + msg + "\n")
		elif style == LOG_PM_SENT:
			self.textbuffer.insert(iter, "<<< "  + msg + "\n")
		else:
			self.textbuffer.insert(iter, msg + "\n")
		startiter = self.textbuffer.get_iter_at_offset(offset)
		enditer = self.textbuffer.get_end_iter()
		tag = self.textbuffer.create_tag(None, foreground = color)
		self.textbuffer.apply_tag(tag, startiter, enditer)
		
		self.view.scroll_to_mark(self.textbuffer.get_insert(),0)

		self.dumplog()

	def parse_Message(self, msg):
		minval = len(msg) + 1
		min = ""
		for x in self.emoticons.keys():	
			i = msg.find(x)
			if i < minval and i != -1:
				minval = i
				min = x

		iter = self.textbuffer.get_end_iter()

		if minval == len(msg) + 1:
			self.textbuffer.insert(iter, msg)
		elif minval == 0:
			self.textbuffer.insert_pixbuf(iter, self.emoticons[min])
			self.parse_Message(msg[len(min):])
		else:
			self.parse_Message(msg[:minval])
			self.parse_Message(msg[minval:])

		
	def addPrivateLog (self, user, textview, textbuffer):
		self.privateLogs.append([user, textview, textbuffer])
		
	def plog(self, username, msg, style=LOG_INFO):

		windowOpen = False
		for logs in self.privateLogs:
			if logs[0] == username:
				windowOpen = True
				oldtb = self.textbuffer
				oldview = self.view
				self.view = logs[1]
				self.textbuffer = logs[2]
				self.log(msg, style)
				self.textbuffer = oldtb
				self.view = oldview
		if windowOpen == False:
			pm = privateMessage(username, self.messages, self)
			self.plog(username, msg, style)
