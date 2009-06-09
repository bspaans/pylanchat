#file User.py

class User:
	
	def __init__(self, ID):
		self.name = ""
		self.loggedIN = False
		self.online = True
		self.ID = ID

		# Encryption
		self.encrytion_enabled = False
		self.send_to_unencrypted_clients = False
		self.receive_from_unencrypted_clients = True

		self.RSAkey = ""

		# For registered users only
		self.registered = False
		self.password = ''
