import mysql.connector

from py3server.passwordHashing import *

class MySQLDatabase():
	host = "";
	user = "";
	password = "";
	database = "";
	dbConnection = None;
	cursor = None;
	
	def initDatabase(self):
		self.cursor.execute("SHOW DATABASES LIKE '%s'", self.database);
		result = self.cursor.fetchone();
		if self.database not in result:
			self.cursor.execute("CREATE DATABASE " + self.database);
			self.cursor.execute("COMMIT");
		self.cursor.execute("USE " + self.database);
	
	def initTables(self):
		self.cursor.execute("SHOW TABLES LIKE 'users'");
		result = self.cursor.fetchall();
		if not result:
			# user DB
			self.cursor.execute("CREATE TABLE users (\
			uid INT AUTO_INCREMENT PRIMARY KEY, \
			username VARCHAR(255), \
			password VARCHAR(255),\
			salt VARCHAR(255), \
			email VARCHAR(320), \
			authorizationLevel INT, \
			ip VARCHAR(128), \
			sessionHash VARCHAR(64), \
			attendingEventUIDs VARCHAR(128)\
			)");

		self.cursor.execute("SHOW TABLES LIKE 'events'");
		result = self.cursor.fetchall();
		if not result:
			self.cursor.execute("CREATE TABLE events (\
			uid INT AUTO_INCREMENT PRIMARY KEY, \
			organizer VARCHAR(128), \
			summary NVARCHAR(512),\
			description NVARCHAR(5000),\
			startDate DATE,\
			startTime TIME,\
			endDate DATE,\
			endTime TIME,\
			location NVARCHAR(512),\
			url VARCHAR(512),\
			attendeeUIDs VARCHAR(128)\
			)");
	
	def isUsernameAvailable(self, username):
		self.cursor.execute("SELECT * FROM users WHERE username = '{}'".format(username));
		result = self.cursor.fetchall();
		self.cursor.reset();
		return len(result) <= 0;
	
	def isEmailAvailable(self, email):
		self.cursor.execute("SELECT * FROM users WHERE email = '{}'".format(email));
		result = self.cursor.fetchall();
		return len(result) <= 0;
	
	def addUser(self, username, password, email, authorizationLevel = 1):
		if(self.isUsernameAvailable(username) and self.isEmailAvailable(email)):
			# make a salted hash out of the password
			passwordSalt = create_salt();
			hashedPassword = hash_password(password, passwordSalt);			
			# Verify a password
			password_matched = verify_password(hashedPassword, password, passwordSalt);
			print("Password Matched:", password_matched);
			
			sql = "INSERT INTO users (username, password, salt, email, authorizationLevel) VALUES (%s, %s, %s, %s, %s)";
			val = (username, hashedPassword, passwordSalt, email, authorizationLevel);
			self.cursor.execute(sql, val);
			self.dbConnection.commit();
			print(self.cursor.rowcount, "record inserted.")
	
	def authenticateUser(self, username, password):
		# Check if username is in the database
		if(self.isUsernameAvailable(username) == True):
			return False;
		# Retrieve user salt and hashed password to be checked
		self.cursor.execute("SELECT salt FROM users WHERE username = '{}'".format(username));
		salt = self.cursor.fetchone();
		self.cursor.execute("SELECT password FROM users WHERE username = '{}'".format(username));
		hashedPassword = self.cursor.fetchone();
		# Check if fetched result has contents
		if((len(salt) <= 0) or (len(hashedPassword) <= 0)):
			return False;
		# convert from tuple into simple string
		salt = salt[0];
		hashedPassword = hashedPassword[0];
		# Verify the password
		result = verify_password(hashedPassword, password, salt);
		if(result is True):
			self.cursor.execute("SELECT password FROM users WHERE username = '{}'".format(username));
		return result;

	def authenticateUserSession(self, username, token, ip):
		# Retrieve user token and ip to be checked
		self.cursor.execute("SELECT sessionHash FROM users WHERE username = '{}'".format(username));
		sessionHash = self.cursor.fetchone();
		self.cursor.execute("SELECT ip FROM users WHERE username = '{}'".format(username));
		userIP = self.cursor.fetchone();

		# Check if fetched result has contents
		if((len(sessionHash) <= 0) or (len(userIP) <= 0)):
			return False;
		# convert from tuple into simple string
		sessionHash = sessionHash[0];
		userIP = userIP[0];		
		if(sessionHash == token and userIP == ip):
			print("session authenticated!");
			return True
		return False
	
	def getUserAuthorizationLevel(self, username):
		self.cursor.execute("SELECT authorizationLevel FROM users WHERE username = '{}'".format(username));
		authorizationLevel = self.cursor.fetchone();
		if(len(authorizationLevel) <= 0):
			return -1
		return authorizationLevel[0];
	
	def updateUserSession(self, username, token, ip):
		if(self.isUsernameAvailable(username) == True):
			return False;
		# Retrieve user salt and hashed password to be checked
		self.cursor.execute("UPDATE users SET sessionHash = '{}', ip = '{}' WHERE username = '{}'".format(token, ip, username));
		self.dbConnection.commit();
		print(self.cursor.rowcount, " record(s) affected");
		return True;
		
	def getUsernameFromSessionToken(self, token, ip):
		# Retrieve user salt and hashed password to be checked
		self.cursor.execute("SELECT username FROM users WHERE session = '{}'".format(username));
		salt = self.cursor.fetchone();
		self.cursor.execute("SELECT password FROM users WHERE username = '{}'".format(username));
		hashedPassword = self.cursor.fetchone();
		# Check if fetched result has contents
		if((len(salt) <= 0) or (len(hashedPassword) <= 0)):
			return False;
	
	def addEvent(self, organizer, summary):
		sql = "INSERT INTO events (organizer, summary) VALUES (%s, %s)";
		val = (organizer, summary);
		self.cursor.execute(sql, val);
		self.dbConnection.commit();	
		self.printTable("events");
	
	def deleteUser(self, username):
		if(not self.isUsernameAvailable(username)):
			self.cursor.execute("DELETE * FROM users WHERE username = '{}'".format(username));
			self.dbConnection.commit();
			print(self.cursor.rowcount, "record inserted.")		
	
	def wipeHype(self):
		try:
			# just drop the whole thing
			self.cursor.execute("DROP DATABASE IF EXISTS {}".format(self.database));
#			self.cursor.execute("DELETE FROM users");
#			self.cursor.execute("DELETE FROM events");
#			self.cursor.execute("ALTER TABLE users AUTO_INCREMENT = 1");
#			self.cursor.execute("ALTER TABLE events AUTO_INCREMENT = 1");
			self.dbConnection.commit();
		except:
			print("Something went wrong while wiping database");
	
	def printDatabases(self):
		self.cursor.execute("SHOW DATABASES")
		print("Databases:")
		for x in self.cursor:
			# filter out MySQL meta-databases
			if('information_schema' not in x and 'performance_schema' not in x):
				print("\t{}".format(x));
	
	def printTables(self):
		self.cursor.execute("SHOW TABLES");
		print("Tables:");
		for x in self.cursor:
			print("\t{}".format(x));
	
	def printTable(self, table):
		self.cursor.execute("SELECT * FROM {}".format(table));
		result = self.cursor.fetchall();
		print("[{}]:".format(table));
		for x in result:
		  print("\t{}".format(x));

	def __init__(self, host, user, password, database=''):		
		# initialize variables
		self.host = host;
		self.user = user;
		self.password = password;
		
		print("Connecting to MySQL as " + user + "@" + host);
		
		if(len(database) == 0):
			self.database = "database";
		else:
			self.database = database;
		
		# Connect to database
		self.dbConnection = mysql.connector.connect(
		  host = self.host,
		  user = self.user,
		  password = self.password
		)
		
		self.cursor = self.dbConnection.cursor(buffered=True);

		# wipe everything for testing
		self.wipeHype();
		
		# Create the database if it doesn't already exist
		self.initDatabase();
		# Create database tables if they don't already exist
		self.initTables();

		# initialize users
		self.addUser("root", "root", "root@placeholder.com", 99);
		self.addUser("user", "password", "user@placeholder.com", 1);
		
#		self.addEvent();
		
		self.printDatabases();
		self.printTables();
		
		self.printTable("users");
		self.printTable("events");
