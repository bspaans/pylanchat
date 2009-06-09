## Python Chat and Game server client
## Written by Bart Spaans, Sep 2007
## See http://www.onderstekop.nl/coding/ for more scripts

#GUI libraries;
#See http://www.pygtk.org/ for documentation
import pygtk
pygtk.require('2.0')
import gtk

#Import protocol to start and stop connections and send messages
from clientProtocol import *

#Global macros
from clientVars import *

from Log import *
from Panels import userPanel, chanPanel
import os
from privateMessage import *
from Crypto.PublicKey import RSA
from os import urandom

## The Client's Graphical User Interface (GUI) is managed here (PyGTK+2,0)
class GUI:
	
	##The constructor class
	def __init__(self, msgObject, option_dict):
		self.messages = msgObject;
		self.options = option_dict
		self.toggleDisabled = []
		
		#initiate the container window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_icon(gtk.gdk.pixbuf_new_from_file_at_size("user_icon.gif",14,16 ))
		self.window.set_resizable(True)
		self.window.connect("destroy", self.close_application)
		self.window.set_title(APP_NAME + " " + APP_VERSION)
		self.window.set_default_size(900, 200)


		self.main_vbox = gtk.VBox(False)
		self.window.add(self.main_vbox)
		self.main_vbox.show()
		
		
		self.notebook = gtk.Notebook()
		self.notebook.set_tab_pos(gtk.POS_TOP)



		#adding widgets to chat tab
		self.table = gtk.Table(9, 6, True)
		self.channel_table = gtk.Table(9, 6, True)
		self.logtab = gtk.Table(9, 6, True)
		self.server_tab = gtk.Table(9, 6, True)
		self.pref_tab = gtk.Table(9,6, True)

		self.makeEntries()
		self.makeButtons()
		self.makeTextArea()
		self.makeTreeViews()
		self.notebook.append_page(self.server_tab, gtk.Label("Servers"))
		self.notebook.append_page(self.table, gtk.Label("Chat"))
		self.notebook.append_page(self.channel_table, gtk.Label("Channels"))
		self.notebook.append_page(self.logtab, gtk.Label("Status Log"))
		self.notebook.append_page(self.pref_tab, gtk.Label("Preferences"))


		self.main_vbox.pack_start(self.notebook, True, True, 5)

		self.statuslabel = gtk.Label("")
		self.main_vbox.pack_start(self.statuslabel, False)
		
		#make the widgets visible
		self.window.show_all()

			
	##Adds a number of entries (textfields) to the widget table.
	def makeEntries(self):
		
		self.msgText = gtk.Entry()
		self.msgText.connect("key-press-event", self.pressedMsgKey)
		self.table.attach(self.msgText, 0, 3, 8, 9)

		self.RSAkeysizetext = gtk.Entry()
		self.pref_tab.attach(self.RSAkeysizetext, 1, 4, 2, 3)

		self.aliasText = gtk.Entry()
		
		# If no alias is supplied in the configuration file,
		# try the username in the environment.
		if self.options["alias"] == "":
			try:
				name = os.environ["USERNAME"]
			except:
				name = "Anonymous"
		else:
			name = self.options["alias"]
		self.aliasText.set_text(name)
		self.pref_tab.attach(self.aliasText, 1, 3, 3, 4)

		self.hostText =gtk.Entry()
		self.server_tab.attach(self.hostText, 0, 7, 7, 8, gtk.FILL, gtk.FILL, 20)

	def pressedMsgKey(self, widget, event):
		if event.keyval == 65293:
			self.sendMessage("")
		
	
	
	## Add and display Connect and Send buttons
	def makeButtons(self):

		b=gtk.Button("Send")
		b.connect("clicked", self.sendMessage)
		self.table.attach(b, 3, 4, 8, 9, gtk.FILL, False, 0, 2)
		
		b = gtk.Button("Refresh")
		b.connect("clicked", self.refreshUserlist)
		pb = gtk.Image()
		pb.set_from_file("refresh.gif")
		b.set_image(pb)
		self.table.attach(b, 5, 6, 8, 9)

		b = gtk.Button("Refresh")
		b.connect("clicked", self.refreshChannels)
		pb = gtk.Image()
		pb.set_from_file("refresh.gif")
		b.set_image(pb)
		self.channel_table.attach(b, 5, 6, 8, 9)

		b=gtk.Button("Revert")
		b.connect("clicked", self.revertPreferenes)
		self.pref_tab.attach(b, 4, 5, 8, 9, gtk.FILL, False, 0, 2)

		b=gtk.Button("Save")
		b.connect("clicked", self.savePreferenes)
		self.pref_tab.attach(b, 5, 6, 8, 9, gtk.FILL, False, 0, 2)

		b=gtk.Button("Connect")
		b.connect("clicked", self.startService)
		self.server_tab.attach(b, 7, 8, 1, 2, gtk.FILL, False, 5, 2)
		self.connect_button = b

		b=gtk.Button("Disconnect")
		b.set_sensitive(0)
		#b.connect("clicked", None)
		self.server_tab.attach(b, 7, 8, 2, 3, gtk.FILL, False, 5, 2)
		self.disconnect_button = b

		b=gtk.Button("Save")
		b.connect("clicked", self.save_servers)
		b.set_sensitive(0)
		self.server_save_button = b
		self.server_tab.attach(b, 7, 8, 6, 7, gtk.FILL, False, 5, 2)

		b=gtk.Button("Add")
		b.connect("clicked", self.add_server)
		self.server_tab.attach(b, 7, 8, 7, 8, gtk.FILL, False, 5, 2)

	## Add the chat text area
	def makeTextArea(self):
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		sw.set_shadow_type(gtk.SHADOW_IN)
		textview = gtk.TextView()
		textview.set_editable(False)
		textview.set_wrap_mode(gtk.WRAP_WORD)
		self.textbuffer = textview.get_buffer()
		sw.add(textview)
		sw.show()
		textview.show()
		self.table.attach(sw, 0, 4, 0, 8)
		self.log = Log(self.textbuffer, textview, self.messages)
		

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		sw.set_shadow_type(gtk.SHADOW_IN)
		textview = gtk.TextView()
		textview.set_editable(False)
		textview.set_wrap_mode(gtk.WRAP_WORD)
		textbuffer = textview.get_buffer()
		sw.add(textview)
		sw.show()
		textview.show()
		self.logtab.attach(sw, 0, 6, 0, 9)
		self.status_log = Log(textbuffer, textview, self.messages)
		
		
	def makeTreeViews(self):


		# User tree
		self.treestore = gtk.TreeStore(str)
		self.tm = gtk.TreeModelSort(self.treestore)
		self.tm.set_sort_column_id(0, gtk.SORT_ASCENDING);
		
		self.treeview = gtk.TreeView(self.tm);
		self.tvcolumn = gtk.TreeViewColumn('Online Users')
		self.treeview.append_column(self.tvcolumn)
		
		self.cell = gtk.CellRendererText()
		self.treeview.set_headers_clickable(True)
		self.treeview.connect("button_press_event", self.treeviewCallback, None)
		self.cellpb = gtk.CellRendererPixbuf()
		self.tvcolumn.pack_start(self.cellpb, True)
		self.tvcolumn.pack_start(self.cell, False)
		self.tvcolumn.add_attribute(self.cell, 'text', 0)
		self.tvcolumn.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		self.tvcolumn.set_cell_data_func(self.cellpb, self.userImage)
		self.tvcolumn.set_sort_column_id(0)
		
		scrolled = gtk.ScrolledWindow()
		scrolled.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		scrolled.set_shadow_type(gtk.SHADOW_IN)
		scrolled.add(self.treeview)
		
		self.table.attach(scrolled, 4,6, 0, 8)
		
		self.userPanel = userPanel(self.treestore);

		# Channel tree
		self.chantreestore = gtk.TreeStore(str, int, str)
		self.chantm = gtk.TreeModelSort(self.chantreestore)
		self.chantm.set_sort_column_id(0, gtk.SORT_ASCENDING);
		self.chantreeview = gtk.TreeView(self.chantm)

		tvcolumn = gtk.TreeViewColumn('Channel name')
		tvcolumn2 = gtk.TreeViewColumn("Persons")
		tvcolumn3 = gtk.TreeViewColumn("Description")

		self.chantreeview.set_headers_clickable(True)
		self.chantreeview.connect("button_press_event", self.chanviewCallback, None)

		self.chancell = gtk.CellRendererText()
		tvcolumn.pack_start(self.chancell, False)
		tvcolumn.add_attribute(self.chancell, 'text', 0)
		self.tvcolumn.set_sort_column_id(0)

		self.chancell = gtk.CellRendererText()
		tvcolumn2.pack_start(self.chancell, False)
		tvcolumn2.add_attribute(self.chancell, 'text', 1)
		tvcolumn2.set_sort_column_id(1)

		tvcolumn3.pack_start(self.chancell, False)
		tvcolumn3.add_attribute(self.chancell, 'text', 2)
		tvcolumn3.set_sort_column_id(2)


		self.chantreeview.append_column(tvcolumn)
		self.chantreeview.append_column(tvcolumn2)
		self.chantreeview.append_column(tvcolumn3)

		scrolled = gtk.ScrolledWindow()
		scrolled.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		scrolled.set_shadow_type(gtk.SHADOW_IN)
		scrolled.add(self.chantreeview)

		self.channel_table.attach(scrolled, 0, 6, 0, 8, gtk.FILL, gtk.FILL, 20)
		self.chanPanel = chanPanel(self.chantreestore)


		# Server tree
		server_treestore = gtk.TreeStore(str)
		tm = gtk.TreeModelSort(server_treestore)
		tm.set_sort_column_id(0, gtk.SORT_ASCENDING);
		
		treeview = gtk.TreeView(tm);
		tvcolumn = gtk.TreeViewColumn('Servers')
		treeview.append_column(tvcolumn)
		treeview.set_headers_clickable(True)
		self.server_treeview = treeview

		cell = gtk.CellRendererText()
		tvcolumn.pack_start(cell, False)
		tvcolumn.add_attribute(cell, 'text', 0)
		tvcolumn.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		tvcolumn.set_sort_column_id(0)
		
		scrolled = gtk.ScrolledWindow()
		scrolled.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		scrolled.set_shadow_type(gtk.SHADOW_IN)
		scrolled.add(treeview)
		
		self.server_tab.attach(scrolled, 0, 7, 1, 7, gtk.FILL, gtk.FILL, 20)
		self.server_treestore = server_treestore	
		self.server_model = tm
		self.load_servers_from_file()
	
	## Gets called when the user double clicked someone from the user panel
	def treeviewCallback(self, treeview, event, data=None):
		if event.type == gtk.gdk._2BUTTON_PRESS:
			treeselection = self.treeview.get_selection()
			(model, treeiter) = treeselection.get_selected()
			treeiter = self.tm.convert_iter_to_child_iter(None, treeiter)
			name = self.treestore.get_value(treeiter,0)
			if name[0:5] != " ID: " and name[0:14] != " Known Since: ":
				pm = privateMessage(str(name[2:]), self.messages, self.log)


	def chanviewCallback(self, treeview, event, data=None):
		if event.type == gtk.gdk._2BUTTON_PRESS:
			treesel = treeview.get_selection()
			(model, treeiter) = treesel.get_selected()
			treeiter = self.chantm.convert_iter_to_child_iter(None, treeiter)
			name = self.chantreestore.get_value(treeiter, 0)[2:]
			self.joinChannel(name)

	def joinChannel(self, chan):
		self.update_status_log("Joining channel %s" % chan, LOG_INFO)
		self.messages.addmsg("/COMMAND JOIN CHANNEL %s" % chan)


	## Event function that gets called when the client has clicked the connect button
	def startService(self, widget):

		treesel = self.server_treeview.get_selection()
		(model, treeiter) = treesel.get_selected()
		try:
			treeiter = self.server_model.convert_iter_to_child_iter(None, treeiter)
		except:
			return 

		hostparts = self.server_treestore.get_value(treeiter, 0)
		hostparts = hostparts.split(":")

		host = hostparts[0]
		port = int(hostparts[1])
		alias = self.aliasText.get_text()
		self.update_status_log("Generating secure %s bit RSA public key" %\
				self.options["RSAkeysize"], LOG_INFO)
		rsakey = RSA.generate(int(self.options["RSAkeysize"]), urandom)
		self.update_status_log("You are trying to connect to " + host + " at port " + str(port) + " under the name " + alias, LOG_CONN)
		self.connect_button.set_sensitive(0)
		self.notebook.set_current_page(3)
		self.disconnect_button.set_sensitive(1)
		runReactor(host, port, alias, rsakey, self)
		
	## Event function that gets called when the client has clicked the send button
	def sendMessage(self, widget):
		msg = self.msgText.get_text()
		if msg != "":
			self.messages.addmsg(msg)
			self.msgText.set_text("")
	
	## Function that gets called when the GUI is being closed
	def close_application(self, widget):
		try:
			stopReactor()
		except:
			pass
		gtk.main_quit()
	
	def userImage(self, column, cell, model, iter):
		pb = gtk.gdk.pixbuf_new_from_file_at_size("user_icon.gif",14,16 )
		cell.set_property('pixbuf', pb)
		return


	def refreshChannels(self, event, data = None):
		self.messages.addmsg("/COMMAND CHANNELLIST");

	def refreshUserlist(self, event, data=None):
		self.messages.addmsg("/COMMAND USERLIST");

	def revertPreferenes(self, event, data=None):
		pass

	def savePreferenes(self, event, data=None):
		pass

	def update_status_log(self, msg, style = LOG_INFO):
		self.status_log.log(msg, style)
		if style == LOG_MSG or style == LOG_INFO or style == LOG_ERR:
			self.log.log(msg, style)

	def load_servers_from_file(self):
		try:
			f = open("servers.conf")
			servers = f.read().split("\n")
			f.close()
		except:
			servers = []
		for s in servers:
			if s != "" and s != "\r":
				if s[-1] == '\r':
					s = s[:-1]
				a = self.server_treestore.append(None, [s])


	def add_server(self, event, data = None):
		newserv = self.hostText.get_text()

		servparts = newserv.split(":")
		if len(servparts) != 2:
			return
		try:
			 int(servparts[1]) 
		except:
			return

		a = self.server_treestore.get_iter_first()
		while a != None:
			if self.server_treestore.get_value(a, 0) == newserv:
				self.server_treestore.remove(a)
				break
			a = self.server_treestore.iter_next(a)
		if newserv != "":
			self.server_treestore.append(None, [newserv])
			self.hostText.set_text("")
			self.server_save_button.set_sensitive(1)



	def save_servers(self, event, data = None):
		f = open("servers.conf", 'w')
		a = self.server_treestore.get_iter_first()
		while a != None:
			res = self.server_treestore.get_value(a,0) + "\n"
			f.write(res)
			a = self.server_treestore.iter_next(a)
		f.close()
		self.server_save_button.set_sensitive(0)

	def select_server(self, event, data=None):
		pass


def startGUI(msgObject, options):
	GUI(msgObject, options)
	gtk.main()
	return 0
