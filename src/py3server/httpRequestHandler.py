from http.server import HTTPServer, BaseHTTPRequestHandler
from http import cookies
from io import BytesIO
import uuid
import datetime

from py3server.mySQLDatabase import MySQLDatabase
from py3server.passwordHashing import *
from py3server.calenderEvent import *
from py3server.webScraper import WebScraper

hexDict = [
	("%09", '\t'), ("%0A", '\n'), ("%0D", '\r'), ("%20", ' '),
	("%21", '!'), ("%22", '"'),	("%23", '#'), ("%24", '$'), ("%25", '%'), ("%26", '&'),
	("%27", "'"), ("%28", '('), ("%29", ')'), ("%2A", '*'), ("%2B", '+'), ("%2C", ','),
	("%2D", '-'), ("%2E", '.'), ("%2F", '/'), ("%3A", ':'), ("%3B", ';'), ("%3C", '<'),
	("%3D", '='), ("%3E", '>'), ("%3F", '?'), ("%40", '@'), ("%5B", '['), ("%5C", '\\'),
	("%5D", ']'), ("%5E", '^'), ("%5F", '_'), ("%60", '`'), ("%7B", '{'), ("%7C", '|'),
	("%7D", '}'), ("%7E", '~')
];

beeASCII = \
b"              \     /\n" + \
b"          \    . ^ .    /\n" + \
b"            \ (     ) /\n" + \
b" ____________(%%%%%%%)____________\n" + \
b"(     /   /  )%%%%%%%(  \   \     )\n" + \
b"(___/___/__/           \__\___\___)\n" + \
b"   (     /  /(%%%%%%%)\  \     )\n" + \
b"   (     /  /(%%%%%%%)\  \     )\n" + \
b"    (__/___/ (%%%%%%%) \___\__)\n" + \
b"            /(       )\ \n" + \
b"          /   (%%%%%)   \ \n" + \
b"               (%%%)\n" + \
b"                 !\n";

teapotASCII = \
b"             ;,'\n" + \
b"     _o_    ;:;'\n" + \
b" ,-.'---`.__ ;\n" + \
b"((j`=====',-'\n" + \
b" `-\     /\n" + \
b"    `-=-'     hjw";


def replaceHex(input):
	for x in hexDict:
		if('%' not in input):
			break;
		input = input.replace(x[0], x[1]);
	return input;

class Py3ServerHTTPRequestHandler(BaseHTTPRequestHandler):
	database = MySQLDatabase("localhost", "user", "password", "py3db");
	# location of html files
	viewPATH = "../view/";
	configPATH = "../config/";

	def POST_getParams(self, message):
		encoding = "utf-8";
		message = str(message, encoding);
		if(len(message) <= 0):
			return;
		message = message[1:-1];
		pairs = message.split(',');
		dict = [x.split(':') for x in pairs];
		for x in dict:
			x[0] = x[0][1:-1];
			x[1] = x[1][1:-1];
			if(len(x) > 1):
				if(len(x)):
					x[1] = replaceHex(x[1]);
		return dict;

	def print_POST(self, message):
		print("");
		print("POST message contents:");
		encoding = "utf-8";
		message = str(message, encoding);
		if(len(message) <= 0):
			return;
		message = message[1:-1];
		pairs = message.split(',');
		dict = [x.split(':') for x in pairs];
		for x in dict:
			x[0] = x[0][1:-1];
			x[1] = x[1][1:-1];
			if(len(x) > 1):
	#			x = x[1:-1];
	#			x[1] = x[1].replace('+', ' ');
				if(len(x)):
					x[1] = replaceHex(x[1]);
			print(*x, sep = '\t= ');
#		eventName = dict[0][1];
#		eventOrganizer = dict[1][1];
#		eventDescription = dict[2][1];
#		eventUID = uuid.uuid4();
		
#		event = CalenderEvent(eventName, eventOrganizer, eventDescription, eventUID);

#		self.database.addEvent(eventOrganizer, eventDescription);
#		self.database.addEvent(event);

	def respond(self, code, payload = ""):
		if(code == 200):
			self.send_response(200);
			self.end_headers();
			self.wfile.write(payload);			
		elif(code == 401):
			self.send_response(401);
			self.end_headers();
			self.wfile.write(b"         401 - Unauthorized\n\n");
			self.wfile.write(beeASCII);			
		elif(code == 404):
			self.send_response(404);
			self.end_headers();
			self.wfile.write(b"          404 - not found\n\n");
			self.wfile.write(beeASCII);			
		else:
			self.send_response(418);
			self.end_headers();
			self.wfile.write(b"418 - I am a teapot!\n\n");
			self.wfile.write(teapotASCII);

	def do_GET(self):
		try:			
			# root should default to index.html
			if self.path == '/':
				self.path = "/index.html";
			# prevent the user from trying to traverse the file system by
			# utilizing backspaces (..), home (~), macros ($), or wildcards (*)
			# in their request paths
			forbiddenTokens = ["..", "~", "$", "*"];
			allowedRequest = True;
			for token in forbiddenTokens:
				if token in self.path:
					allowedRequest = False;
			if allowedRequest:
				# request is allowed so load OK response in header
				routesFileName = "routes.txt";
				routesFile = open(self.configPATH + routesFileName, "r");
				routes = routesFile.read();
				routesFile.close();

				# Get all the routes in their own list
				routes = routes.split('\n');
				source = "";
				authorizationLevel = 0;
				# iterate over routes to find a match
				for route in routes:
					route = route.split(' ');
					authLevel = int(route[1]);
					route = route[0].split(':');
#					route = route.split(':');
					destination = route[1];
					route = route[0].split(';');
#					route = route.split(';');
					for match in route:
						if(self.path == match):
							source = match;
							authorizationLevel = authLevel;
							break;
					# stop checking other routes if a match has been found already
					if(len(source)):
						break;

				isAuthorized = False;
				if(authorizationLevel == 0):
					isAuthorized = True;
				elif(authorizationLevel > 0):
					ccs = cookies.SimpleCookie(self.headers.get('Cookie'));
					if(len(ccs) > 0):
						username = ccs['py3server_username'].value;
						hashUUID = ccs['py3server_sessionHash'].value;
						clientIP = self.client_address[0];

						# Check with DB if user has authorization to request this asset
						result = self.database.authenticateUserSession(username, hashUUID, clientIP);
						if(result is True):
							authLevel = self.database.getUserAuthorizationLevel(username);
							isAuthorized = (authLevel >= authorizationLevel);

				# file was found
				if(len(source)):
					# user is authorized to get it. 200 - OK
					if(isAuthorized == True):
						file = open(self.viewPATH + source, "rb");
						payload = file.read();
						file.close();
						self.respond(200, payload);
					# user is not authorized to get it! 401 - Unauthorized
					else:
						self.respond(401);
				# file could not be found - 404 not found
				elif(not len(source)):
					self.respond(404);
				# how did this happen? 418 - I'm a teapot
				else:
					self.respond(418);		# I'm a teapot
			# request contained illiegal characters
			else:
				self.respond(404);	# not found
		except FileNotFoundError:
			self.respond(404);		# not found

	def do_POST_login(self):
		content_length = int(self.headers['Content-Length']);
		body = self.rfile.read(content_length);
		params = self.POST_getParams(body);
	
		print("POST_login parameters: ".format(params));
		message = "Response OK! :)";
		numberOfLoginParams = 2;
		username = "";
		password = "";
		# check message length is correct
		if(len(params) == numberOfLoginParams):
			if(len(params[0]) != 2):
				message = ("Username param pair is wrong!");
			elif(len(params[1]) != 2):
				message = ("Password param pair is wrong!");
			else:
				if(len(params[0][1]) < 3):
					message = ("Username parameter was too short!");
				else:
					username = params[0][1];
				if(len(params[1][1]) < 3):
					message = ("Password parameter was too short!");
				else:
					password = params[1][1];
		else:
			message = ("Not enough login parameters!");
		
		readyToAuthenticate = (len(username) and len(password));
		
		print("Ready to authenticate: {}".format(readyToAuthenticate));
		
		authenticated = False;
		
		# Authenticate username and password against database
		if(readyToAuthenticate != 0):
			print("Ready to try and authenticate with the database!");
			clientIP = self.client_address[0];
			result = self.database.authenticateUser(username, password);					
			# TODO: generate a cookie hash for the user to stay logged in
			# To check the hash in the cookie paired with the ip(?) to perform
			# authentication based on that, to have a persistent session.
			if(result == True):
				self.send_response(200);

				# generate hash for cookie
				hashUUID = create_salt();
				print(hashUUID);
				message = hashUUID;
				self.database.updateUserSession(username, hashUUID, clientIP);

				# Do cookie stuff
				expiration = 60 * 60; # 1 hour
				domain = "placeholder.domain";

				cookieHash = cookies.SimpleCookie();
				cookieUsername = cookies.SimpleCookie();
				
				cookieUsername['py3server_username'] = username;
				cookieHash['py3server_sessionHash'] = hashUUID;
				
				cookieUsername['py3server_username']['expires'] = expiration;
				cookieHash['py3server_sessionHash']['expires'] = expiration;
										
				print(cookieUsername.output());
				
				self.send_header("Set-Cookie", cookieHash.output(header='', sep=''))
				self.send_header("Set-Cookie", cookieUsername.output(header='', sep=''))

				self.end_headers();
				
				authenticated = True;

			else:
				message = ("Wrong username / password");
#			message = str(result);
		else:
			message = ("Could not authenticate with the database!");
			
		if(authenticated is False):
			self.send_response(200);
			self.end_headers();
			
		self.wfile.write(bytes(message, 'utf-8'));

	def do_POST(self):	
#		if(self.path == "/createEvent"):
			# handling taking place
#			print("/createEvent");
		if(self.path == "/login"):
			print("Trying to login!");
			self.do_POST_login();
		else:
			self.respond(418);