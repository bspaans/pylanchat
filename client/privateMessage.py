#GUI libraries;
#See http://www.pygtk.org/ for documentation
import pygtk
pygtk.require('2.0')
import gtk

class privateMessage:
	
	def __init__(self, name, msgObject, log):
		
		self.to = name
		self.log = log
		self.messages = msgObject
		
		#initiate the container window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_icon(gtk.gdk.pixbuf_new_from_file_at_size("user_icon.gif",14,16 ))
		self.window.set_resizable(True)
		self.window.connect("destroy", self.closeWindow)
		self.window.set_title("Private conversation with " + name)
		self.window.set_border_width(20)
		self.window.show()
		
		#adding widgets
		self.table= gtk.Table (5,5, True)
		self.makeLabels()
		self.makeEntries()
		self.makeTextArea()
		self.makeFrames()
		self.makeButtons()
		
		self.window.add(self.table)
		self.table.show()
		
		
	def 	makeLabels(self):
		labels = ["To:", "Chat:", "Message:"]; a = 0
		for label in labels:
			l = gtk.Label(label)
			self.table.attach(l, 0, 1, a, a + 1)
			l.show()
			a = a +1
			if a == 2: a = 4
	
	def makeEntries(self):
		self.hostText =gtk.Entry()
		self.hostText.set_text(self.to)
		self.hostText.set_editable(False)
		self.table.attach(self.hostText, 1, 5, 0, 1)
		self.hostText.show()
		
		self.msgText = gtk.Entry()
		self.msgText.connect("key-press-event", self.pressedMsgKey)
		self.table.attach(self.msgText, 1, 4, 4, 5)
		self.msgText.show()
	
	def makeTextArea(self):
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		sw.set_shadow_type(gtk.SHADOW_IN)
		textview = gtk.TextView()
		textview.set_editable(False)
		textview.set_wrap_mode(gtk.WRAP_WORD)
		self.textbuffer = textview.get_buffer()
		self.log.addPrivateLog(self.to, textview, self.textbuffer)
		sw.add(textview)
		sw.show()
		textview.show()
		self.table.attach(sw, 1, 5, 1, 4)
	
	def makeFrames(self):
		f= gtk.Frame()
		f.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		f.set_label_align(0.0,0.0)
		self.table.attach(f, 0, 5, 0, 5)
		f.show()
	
	def makeButtons(self):
		b=gtk.Button("Send")
		b.connect("clicked", self.sendMessage)
		self.table.attach(b, 4, 5, 4, 5)
		b.show()
	
	def pressedMsgKey(self, widget, event):
		if event.keyval == 65293:
			self.sendMessage("")
			
	def sendMessage(self, widget):
		msg = self.msgText.get_text()
		if msg != "":
			self.messages.addPrivateMessage(msg, self.to)
			self.msgText.set_text("")	
	def closeWindow(self, widget):
		print "Exiting private message"
	
	def openWindow(self, widget, event, name):
		print "PM" + name