# accept and use command line arguments
import sys
# SSL certificate to serve HTTPS
import ssl
import socket
# multithreading
import threading
import time

# Imports PIL module
import PIL.Image
from random import randrange

# creating a image object (new image object) with
# RGB mode and size 200x200

img = PIL.Image.new(mode="RGB", size=(4, 4));

pixels = img.load() # create the pixel map

r = randrange(255);
g = randrange(255);
b = randrange(255);
for i in range(img.size[0]): # for every pixel:
	for j in range(img.size[1]):
		hasColor = randrange(2);
		if(hasColor > 0):
			pixels[i,j] = (r,g ,b);
		else:
			pixels[i,j] = (255,255,255);
img = img.resize((200, 200), resample=PIL.Image.BOX);

img.save("test.png");

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# default server arguments
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
ip = None;
port = None;

version = "0.1-alpha";

def printHelpText():
	print("\033[1mBasic syntax:\033[0m" + " python3 " + sys.argv[0] + " <ip> <port>");
	print("\033[1m  - ip\033[0m to set the ip to serve on");
	print("\033[1m  - port\033[0m to set the port number to serve on");
	print("\033[1mOther arguments:\033[0m");
	print("\033[1m  - -v\033[0m to see the current version");
	print("\033[1m  - --version\033[0m to see the current version");
	print("\033[1m  - help\033[0m to see syntax");

# look for command line arguments (ip and port)
argc = len(sys.argv);
if(argc == 3):
	try:
		ip = sys.argv[1];
		port = int(sys.argv[2]);
	except ValueError:
		print("\033[91mEntered incorrect value! Exiting ...\033[0m");
		exit();
	except:
		print("\033[91mEntered incorrect data! Exiting ...\033[0m");
		exit();
elif(argc == 2):
	if(sys.argv[1] == "-v" or sys.argv[1] == "--version"):
		print("Py3Server backend version: " + version);
		exit();
	if(sys.argv[1] == "help"):
		printHelpText();
		exit();
	else:
		print("\033[91mIncorrect syntax!\033[0m");
		printHelpText();
		exit();
else:
	print("\033[91mnot enough parameters!\033[0m");
	printHelpText();
	exit();

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Starting banner
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
bannerText = "Starting Python3 backend!";
bannerLength = len(bannerText);
print("");
print((bannerLength+4)*"*");
print('* ' + '\033[1m\033[92m' + bannerText + '\033[0m' + ' *');
print((bannerLength+4)*"*");
print("");

isRunning = True;

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# backend concurrent command line
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def commandLine():	
	while(isRunning):
		arg = input("\033[1m\033[92mPy3Server\033[0m$ ");
#		print(arg);
		
		confirmationPrompt = "Are you sure? [yes/no] : ";
		
		if(arg == "help"):
			print("Help is on the way");
			print("Commands:");
			print("  [] \033[1mreload\033[0m\n   - Reload routes");
			print("  [] \033[1mshutdown / exit\033[0m\n   - shutdown server");
			print("  [] \033[1mbackup\033[0m\n   - Create a backup of the MySQL database. This can take a while");
		elif(arg == "reload"):
			print("Reloading routes ...");
			# do reloading here
			print("Reloading done!");
		elif(arg == "shutdown" or arg == "exit"):
			arg2 = input(confirmationPrompt);
			if(arg2 == "yes"):
				print("Shutting down server ...");
				server.shutdown();
				exit();
		elif(arg == "backup"):
			arg2 = input("This can take a while. " + confirmationPrompt);
			if(arg2 == "yes"):
				print("Backing up the MySQL database...");
				# do backup here
				print("Back up of MySQL database done!");
		else:
			print("\"" + arg + "\" is not a recognized command. type \"help\" a the list of commands.");

# local modules
from py3server.httpRequestHandler import *
from http.server import ThreadingHTTPServer

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Web scraper
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# webScraper = WebScraper();
# webScraper.scrape_visitBrussels(printContents = False, writeToFile = True);

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# HTTP server
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
print("Creating threaded http server...");
server = ThreadingHTTPServer((ip, port), Py3ServerHTTPRequestHandler);

# Add SSL certificate when on HTTPS port (443)
if(port == 443):
	print("Wrapping socket in SSL cert ...");
	hostname = 'www.yourdomain.extension'
	context = ssl.create_default_context()
	context.load_cert_chain(certfile='../config/ssl.crt', keyfile="../config/ssl.key");	
	server.socket = context.wrap_socket(server.socket, server_hostname=hostname);

# Start listening for connections
print("\nServing @ " + ip + ":" + str(port));

print("\nstarting server command line ...\n");
thread = threading.Thread(target=commandLine);
thread.start();

server.serve_forever();
	
print("Server shutting down!");

exit();
