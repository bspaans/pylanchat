from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor, defer
from clientVars import *
from Messages import Messages
from urllib import quote_plus, unquote_plus
from Users import Users, User
from Channels import Channels, Channel
from Crypto.PublicKey import RSA

class clientProtocol(Protocol):


	def connectionMade(self):
		self.factory.GUI.update_status_log("You are connected to the server!\n", LOG_CONN)
		self.init = True
		self.message = 0;
		self.pm = 0;
		self.channel = ""

		self.protocol  = "1.1"
		self.messages_encrypted = False
		self.responses_encrypted = False

		self.server_key = {}
		d = self.sendMessages();
		d.addCallback(self.sendMessages);
		
		
	def dataReceived(self, data, unencrypted = False):
		if data == '':
			return 

		if not unencrypted:
			self.factory.received += len(data)
			self.update_status_bar()

		if self.init:
			self.factory.GUI.update_status_log("********** MESSAGE FROM SERVER **********\n", LOG_SERVER)
			block = data.split("\r\n\r\n")
			welcome = block[0]
			self.factory.GUI.update_status_log(welcome, LOG_SERVER)
			self.factory.GUI.update_status_log("\n********** MESSAGE FROM SERVER **********\n", LOG_SERVER)
			
			connData = block[1]
			connData = connData.split("\r\n");
			for lines in connData:
				params = lines.split(" ")
				if params[0] == "UID":
					self.factory.Users.usersEver = params[2]
					self.factory.Users.usersOnline = params[3]
					self.factory.Users.addUser(params[1], self.factory.alias)
					self.factory.GUI.update_status_log("There are currently " + params[3] + " users online. This server had " + params[2] + " logins\n", LOG_SERVER)
				elif lines[0:13] == "PUBLIC RSAKEY":
					
					self.server_key[params[2]] = long(params[3])

				elif params[0] == "CHALLENGE":
					self.server_key = RSA.construct((self.server_key['n'], self.server_key['e']))
					self.sendMsg("CHALLENGE " + self.server_key.encrypt(params[1], "")[0])
				elif params[0] == "PROTOCOL":
					self.protocol = params[1]

			self.sendMsg("USER "  + self.factory.alias)
			self.init = False
		else:
			if data[0:7] == "USER OK":
				self.sendMsg("JOIN CHAT")

			elif data[0:24] == "PUBLIC KEY RSA CHALLENGE":
				data = data.split("\r\n")
				for d in data[1:]:
					self.dataReceived(d)
				params = data[0].split(" ")
				if params[4] == "FAILED":
					self.factory.imp.rsa_server_auth_failed()
					self.factory.GUI.update_status_log("RSA sending disabled. Handshake failed.", LOG_ERR)
				elif params[4] == "PASSED":
					self.messages_encrypted = True
					self.sendMsg("PUBLIC RSAKEY e " + str(self.factory.publickey['e']) + "\r\nPUBLIC RSAKEY n " + str(self.factory.publickey['n']) + "\r\nMYCHALLENGE " + self.factory.challenge)
					self.factory.GUI.update_status_log("RSA sending enabled", LOG_CONN)
			elif data[0:11] == "MYCHALLENGE":
				challenge = data[12:]
				ans = self.factory.challenge_answer[0]
				if challenge == ans:
					self.responses_encrypted = True
					self.sendMsg("MYCHALLENGE PASSED")
					self.factory.GUI.update_status_log("RSA receiving enabled", LOG_CONN)
				else:
					self.sendMsg("MYCHALLENGE FAILED")
					self.factory.GUI.update_status_log("RSA receiving disabled. Handshake failed.", LOG_ERR)


			elif data[0:9] == "JOIN CHAT":
				block = data.split("\r\n\r\n")
				other = ""
				for d in block[1:]:
					other += d
				self.dataReceived(other)

				params = block[0].split(" ")
				try:
					ID = params[3]
				except:
					self.factory.GUI.update_status_log("You've joined the chat as " + self.factory.alias + "\n", LOG_INFO)
					return
				username = "NameNotSet"
				
				try:
					name = params[4]
					name = name.split("\n")
					if self.protocol != "1.1":
						self.channel = params[5]
						self.channel = self.channel.split("\r")[0]
						self.factory.Channels.update_persons(self.channel, 1)
					self.factory.log.log(name[0] + " joined %s!" % self.channel , LOG_RECV)
					username = name[0]
					if name[0] == self.factory.alias:
						self.sendMsg("USERLIST")
				except:
					pass
				self.factory.Users.addUser(ID, username, True)

			elif data[0:8] == "USERLIST":
				lines =data.split("\r\n");
				self.factory.Users.clear()
				for block in lines:
					params = block.split("\t")
					try:
						ID = params[1]
					except:
						ID = -1;
					try: 
						name = params[2]
					except:
						name = "NameNotSet";
					self.factory.Users.addUser(ID, name, True);
				if self.protocol != "1.1":
					self.sendMsg("CHANNELLIST")

			elif data[0:7] == "CHANNEL":
				self.factory.Channels.clear()
				channels = data.split("\r\n")
				for block in channels:
					params = block.split(" ")
					if len(params) == 3:
						channame = params[1]
						chanmem = params[2]
						self.factory.Channels.addChannel(channame, chanmem)
				self.factory.GUI.statuslabel.set_text("Joined channel %s" % self.channel)

			elif data[0:8] == "EXIT UID":
				data = data.split("\r\n\r\n")
				d = data[0]
				params = d.split(" ")
				try:
					ID = params[2]
					name = self.factory.Users.getName(ID)
					if name != "Unknown User" and name != self.factory.alias:
						self.factory.log.log(name + " left %s" % self.channel, LOG_INFO);
						self.factory.Users.removeUser(ID)
						self.factory.Channels.update_persons(self.channel, -1)
				except:
					params = ""
				other = ""
				for d in data[1:]:
					other += d
				self.dataReceived(other)

			elif data[0:6] == "MSG PM":
				block = data.split("\n")
				params = block[0].split(" ")
				fromUser = params[2]
				toUser = params[3]
				msg = unquote_plus(params[4])
				if self.factory.alias != fromUser:
					self.factory.log.plog(fromUser, msg, LOG_PM_RECV)
				else:
					self.factory.log.plog(toUser, msg, LOG_PM_SENT)
			
			elif data[0:13] == "MSG CHAT UID ":
				params = data.split(" ")
				m = params[4].split("\r\n")[0];
				m = unquote_plus(m)
				self.factory.log.log(self.factory.Users.getName(params[3]) + ": " + m, LOG_MSG)


			else:	
				if self.responses_encrypted and not(unencrypted):
					blocks = data.split("\r\n\r\n")
					for b in blocks:
						realdata = self.get_decrypted_message(b)
						self.dataReceived(realdata, True)
				else:
					return False
	
	def connectionLost(self, reason):
		self.factory.GUI.update_status_log("\n\n===Lost connection to the server ===", LOG_CONN);
		self.factory.GUI.update_status_log("Received %d bytes (%d kB), sent %d (%d kB)" % (self.factory.received, self.factory.received / 1024, self.factory.sent, self.factory.sent / 1024))
		self.factory.Users.clear()
		self.factory.Channels.clear()
		
	def sendMessages(self):
		d= defer.Deferred()
		msglen = len(self.factory.messages.messages);
		pmlen = len(self.factory.messages.privateMessages);
		if msglen != self.message:
			while self.message != msglen:
				m = self.factory.messages.messages[self.message]
				if m[0:9] != "/COMMAND ":
					self.sendMsg("MSG CHAT " + quote_plus(m))
				else:
					self.sendMsg(m[9:])
				self.message = self.message + 1
			d.callback("SEND MESSAGES")
		elif pmlen != self.pm:
			while self.pm != pmlen:
				prim = self.factory.messages.privateMessages[self.pm];
				msg = prim[0]
				to = prim[1]
				self.sendMsg("MSG PM " + quote_plus(to) +" " + quote_plus(msg))
				self.pm = self.pm + 1
			d.callback("SEND MESSAGES")
		reactor.callLater(CHECK_FOR_MESSAGES_TO_SEND_TIMEOUT, self.sendMessages);
		return d;
		
	def sendMsg(self, msg):
		self.factory.pid += 1
		msg = self.get_encrypted_message(msg)
		self.factory.sent += len(msg)
		self.update_status_bar()
		self.transport.write(msg + "\r\n\r\n")

	def get_encrypted_message(self, msg):
		if self.messages_encrypted:
			if len(msg) < self.server_key.size() / 8:
				return self.server_key.encrypt(msg, "")[0]
			else:
				return self.server_key.encrypt(msg[:self.server_key.size() / 8], "")[0] + "\r\n" + self.get_encrypted_message(msg[self.server_key.size() / 8:])
		else:
			return msg

	def get_decrypted_message(self, data):
		data = data.split("\r\n")
		res = ""
		for d in data:
			d = self.remove_whitespace_at_end(d)
			res += self.factory.RSAkey.decrypt(d)
		return res

		
	def remove_whitespace_at_end(self, str):
		if str == "":
			return ""
		if str[-1] == '\n' or str[-1] == '\n':
			return self.remove_whitespace_at_end(str[:-1])
		return str	

	def update_status_bar(self):
		msg = "%d bytes received (%d kB), %d bytes sent (%d kB)" % (self.factory.received, self.factory.received / 1024, self.factory.sent, self.factory.sent / 1024)
		self.factory.GUI.statuslabel.set_text(msg)

class clientProtocolFactory(ClientFactory):
	
	protocol = clientProtocol
	
	def __init__(self, alias, rsakey, GUIobject):
		self.GUI = GUIobject
		self.log = GUIobject.log
		self.status_log = GUIobject.status_log
		self.messages = GUIobject.messages

		self.received = 0
		self.sent = 0

		self.alias = alias
		self.pid = 1
		self.RSAkey = rsakey
		self.publickey = rsakey.publickey().__getstate__()
		self.challenge = "my_encryption_challenge"
		self.challenge_answer = rsakey.encrypt(self.challenge, "")
		
		self.Users = Users(GUIobject.userPanel);
		self.Users.addUser("1", alias);
		self.Channels = Channels(GUIobject.chanPanel)
	
	def clientConnectionFailed(self, reason, bla):
		self.GUI.update_status_log("Couldn't connect...\n", LOG_ERR)

def runReactor(host, port, alias, rsakey, GUIobject):	
	f = clientProtocolFactory(alias, rsakey, GUIobject)
	GUIobject.factory = f
	reactor.connectTCP(host, port, f)
	reactor.run()

def stopReactor():
	reactor.stop()
	
