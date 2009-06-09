"""



Parses configuration files, build like this:

	keyword operator value newline
	etc.

Example:

	host=localhost
	port=7878

Or:

	[keyword]
	value

Example:

	[welcome_msg]
	Hi welcome to the server..

"""

EOF = 1
SEPA = 2
WORD = 3
NEWLINE = 4


class Lexer:

	def __init__(self, content, separator = "="):
		self.content = content
		self.pos = 0
		self.lineno = 1
		self.charno = 0
		self.separator = separator

	def next_token(self):
		"""Finds the next token in the content.
		Returns a tuple containing the type of the token 
		and the actual value if there is one."""

		def find_next():
			token = ""
			if self.pos == len(self.content):
				return (EOF, token)
			t = self.content[self.pos]
			while t != ' ':
				if t == self.separator:
					if token == "":
						self.pos += 1
						return (SEPA, t)
					else:
						return (WORD, token)
				elif t == '\n':
					if token == "":
						self.pos += 1
						self.lineno += 1
						self.charno = 0
						return (NEWLINE, 0)
					else:
						return (WORD, token)
					
				elif t == '#':
					if self.charno == 0:
						self.eat_comment()
						return find_next()
				token += t
				self.pos += 1
				if self.pos == len(self.content):
					return (WORD, token)
				t = self.content[self.pos]

			self.pos += 1
			if token == "":
				return find_next()
			return (WORD, token)
			
		return find_next()

	def eat_comment(self):
		t = self.content
		while t != "\n":
			self.pos += 1
			t = self.content[self.pos]
		self.pos += 1
		self.lineno += 1
		self.charno = 0

class Parser:

	def __init__(self, options, separator = "="):
		"""
		@options
		Should be a dictionary containing keyword:default_value entries.
		
		@separator
		The separator used in the config file to separate keywords from values."""
		self.options = options
		self.separator = separator
		self.lexer = ""

	def parse_file(self, file):
		f = open(file, 'r')
		content = f.read()
		f.close()
		return self.parse_content(content)

	def parse_content(self, content):
		self.lexer = Lexer(content, self.separator)

		keyword = ""
		value = ""
		lastword = ""
		result = self.options
		inValue = False

		l = self.lexer.next_token()

		while l[0] != EOF:
			if l[0] == NEWLINE:
				if inValue:
					result[keyword] = value
					keyword = ""
					value = ""
					lastword = ""
					inValue = False
				else:
					if lastword != "":
						print "Syntax error on line %d. Expecting separator." % (self.lexer.lineno - 1)
						return False
			elif l[0] == SEPA:
				if not inValue:
					keyword = lastword
					if keyword in self.options.keys():
						inValue = True
					else:
						#warning should throw exception
						print "Invalid keyword '%s' on line %d." % (keyword, self.lexer.lineno)
						return False
				else:
					value += " " + self.separator
			elif l[0] == WORD:
				if inValue:
					if value != "":
						value += " " + l[1]
					else:
						value = l[1]
				else:
					if lastword != "":
						print "Syntax error on line %d. Expected separator." % self.lexer.lineno
						return False

				lastword = l[1]
			
			l = self.lexer.next_token()

		return result		
