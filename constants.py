import os

SIZE = 4096                             #Max size of the message server can receive
ROOT = os.getcwd()                      #To help server to identify current working directory 
favicon = '/favicon.ico'
FAVICON = ROOT + favicon
Myversion = '1.1'                       #Supported version by server
Thread_requests = 100                   #Max no of threads handled by the server
URL_length = 150                        #Max url_length supported by server
VAR = ROOT + '/execution.html'              #html file gives response to the client once they use get or post method using query
w = open(VAR, "w")
body = '<html><head></head><body> Response saved</body></html>'
w.write(body)
w.close()
CSV = ROOT + '/action.csv'                        #CSV file for storing the data entered by user
w = open(CSV,"a")
w.close()
TRASH = ROOT + '/trash'                 #This directory contains all the files deleted by users using delete request

try:
	os.mkdir(TRASH)
except:
	pass
	
COOKIE = 'set-cookie: id='
MAXTIME = ';max-age=1800' 

USERNAME = 'Server'
PASSWORD = 'Server@123'

LOG = ROOT + '/server.log'
w = open(LOG, "a")
w.close()
CSV = ROOT + '/action.csv'                        #CSV file for storing the data entered by user
w = open(CSV,"a")
w.close()
