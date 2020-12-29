from socket import *
import sys
import threading
from _thread import *
import os
from datetime import *
import time
import logging
import shutil
import mimetypes
import random
import base64
from urllib.parse import *
import csv               # using for get and post         
from constants import *

serversocket = socket(AF_INET , SOCK_STREAM)
#s = socket(AF_INET, SOCK_DGRAM)
connection = True
c_get = False              #used in conditional get
clientlist = []
SER_RUN = True             #to stop server
SER_CLOSE = True           #for Closing server 
num= 0                      #will use in err_msg 
cookie_val = 0

types_to_ext = {'.html':'text/html','.txt':'text-plain', '': 'text/plain'}     
ext_to_types = {'text/html':'.html','text/plain':'.txt', 'text/plain': ''}
month_to_dec = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr':4,'May':5,'Jun':6,'Jul':7, 'Aug':8,'Sep': 9 , 'Oct':10,'Nov':11,'Dec':12}
logging.basicConfig(filename = LOG, level = logging.INFO, format = '%(asctime)s:%(filename)s:%(message)s')

Ip = '0.0.0.0'

def lastmodified(element):
	lm = time.ctime(os.path.getmtime(element)).split(' ')
	for j in lm:
		if len(j) == 0:
			lm.remove(j)
	lm[0] = lm[0] + ','
	str1 = (' ').join(lm)
	str1 = 'Last-Modified :' + str1
	return str1
	
def date():
	d = time.ctime().split(' ')
	d[0] = d[0] + ','
	str1 = (' ').join(d)
	str1 = 'Date : ' + str1
	return str1
	
def if_modify(state,element):
	global c_get
	day = state.split(' ')
	if len(day) == 5:
		global month_to_dec
		m = month_to_dec[day[1]]
		date = int(day[2])
		tm = day[3].split(':')
		tm[0] = int(tm[0])
		tm[1] = int(tm[1])
		tm[2] = int(tm[2])	
		z = int(day[4])
		tmi = datetime(z,m,date,tm[0],tm[1],tm[2])
		asecond = int(time.mktime(tmi.timetuple()))
		bsecond = int(os.path.getmtime(element))
		if asecond == bsecond :
			c_get = True
		if asecond < bsecond :
			c_get = False
		
def status_304(connectionsocket,element):
	global Ip
	num = 304
	display = []
	display.append('HTTP/1.1 304 NOT MODIFIED')
	display.append(date())
	display.append(lastmodified(element))
	display.append('Server :' + Ip)
	display.append('\r\n')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)

def post(body, connectionsocket, element,switcher):
	global Ip,num
	display = []
	l = int(switcher['Content-Length'])
	if l > 0:
		pass
	else:
		err_msg(connectionsocket,403) 
	check = os.path.exists(element)
	if check:
		file1 = open(element, "a")
		display.append('HTTP/1.1 200 OK')
		num = 200
		file1.write(body)
	else:
		file1 = open(element, "w")
		display.append('HTTP/1.1 201 CREATED')
		num = 201
		display.append('Location :' + element)
		file1.write(body)
	file1.close()
	display.append('Server :' + Ip)
	display.append(date()) 
	display.append('Content-Language: en-US,en')
	display.append('Content-Type : text/html')
	f1 = open(element, "rb")
	size = os.path.getsize(element)
	str2 = 'Content-Length: ' +str(size) 
	display.append(str2)
	display.append(lastmodified(element))
	display.append('\r\n')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)
	connectionsocket.sendfile(f1)
	
def put(connectionsocket, addr, body, filedata, element, switcher, fflag):
	global num
	display = []
	isfilethere = os.path.isfile(element)
	isdirthere = os.path.isdir(element)
	try:
		l = int(switcher['Content-Length'])
	except KeyError:
		err_msg(connectionsocket,411)
	l1 = int( l // SIZE)
	l2 = l % SIZE
	try:
		filedata = filedata + body 
	except TypeError:
		body = body.encode()
		filedata = filedata + body
	n = len(body)
	size = l - n
	while size > 0:
		body = connectionsocket.recv(SIZE)
		try:
			filedata = filedata + body
		except TypeError:
			body = body.encode()
			filedata = filedata + body
		size = size - len(body)
	movp, modef , req201 = False, True, False
	isfilethere = os.path.isfile(element)
	isdirthere = os.path.isdir(element)
	l3 = len(element)
	limit = len(ROOT)
	if l3 >= limit:
		if isdirthere:
			if os.access(element, os.W_OK):
				pass
			else:
				err_msg(connectionsocket, 403)
			movp = True
			locate = ROOT + '/' + str(addr[1])
			try:
				locate = locate + ext_to_types[switcher['Content-Type'].split(';')[0]]
			except:
				err_msg(connectionsocket, 403)
			if fflag == 0:
				f1 = open(locate, "w")
				f1.write(filedata.decode())
			else:
				f1 = open(locate,"wb")
				f1.write(filedata)
			f1.close()
		elif isfilethere:
			if os.access(element, os.W_OK):
				pass
			else:
				err_msg(connectionsocket, 403)
			modef =True
			if fflag == 0:
				f1 = open(element, "w")
				f1.write(filedata.decode())
			else:
				f1 = open(element, "wb")
				f1.write(filedata)
			f1.close()
		else:
			if ROOT in element:
				req201 = True
				element = ROOT + '/' + str(addr[1])
				try:
					element = element + ext_to_types[switcher['Content-Type'].split(';')[0]]
				except:
					err_msg(connectionsocket,403)
				if fflag == 0 :
					f1 = open(element, "w")
					f1.write(filedata.decode())
				else:
					f1 = open(element, "wb")
					f1.write(filedata)
				f1.close()
			else:
				modef = False
	else:
		movp = True
		locate = ROOT + '/' +str(addr[1])		
		try:
			locate = locate + ext_to_types[switcher['Content-Type']]
		except:
			err_msg(connectionsocket,403)
		if fflag ==0:
			f1 = open(locate, "w")
		else:
			f1 = open(locate, "wb")
		f1.write(filedata)
		f1.close()
	if movp:
		num = 301
		display.append('HTTP/1.1 301 MOVED PERMANENTLY')
		display.append('Content-Location: ' + locate)
	elif modef:
		num = 204
		display.append('HTTP/1.1 204 NO CONTENT')
		display.append('Content-Location: ' + element)
	elif req201:
		num = 201
		display.append('HTTP/1.1 201 CREATED')
		display.append('Content-Location: ' + element)
	elif not modef:
		num = 501
		display.append('HTTP/1.1 501 NOT IMPLEMENTED')
	display.append('Connection: keep-alive')
	display.append('\r\n')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)

def	delete(element, connectionsocket, body, switcher):
	global Ip,num
	display = [] 
	options = element.split('/')
	isfilethere = os.path.isfile(element)
	isdirthere = os.path.isdir(element)
	if 'Authorization' in switcher.keys():
		str1 = switcher['Authorization']
		str1 = str1.split(' ')
		str1 = base64.decodebytes(str1[1].encode()).decode()
		str1 = str1.split(':')
		print(switcher['Authorization'])
		if str1[0] == USERNAME and str1[1] == PASSWORD:
			pass
		else:
			num = 401
			display.append('HTTP/1.1 UNAUTHORIZED')
			display.append('WWW-AUTHENTICATE: BASIC')
			display.append('\r\n')
			encoded = '\r\n'.join(display).encode()
			connectionsocket.send(encoded)
			return
	else:
		num =401
		display.append('HTTP/1.1 UNAUTHORIZED')
		display.append('WWW-AUTHENTICATE: BASIC')
		display.append('\r\n')
		encoded = '\r\n'.join(display).encode()
		connectionsocket.send(encoded)
		return
	if len(body) > 1 or 'delete' in options or isdirthere:
		num = 405
		display.append("HTPP/1.1 405 METHOD NOT ALLOWED")
		display.append('ALLOW: GET, PUT, HEAD, POST')
	elif isfilethere:
		b = random.randint(0,1)
		if b == 0:
			num = 200
			display.append('HTTP/1.1 200 OK')
		else:
			num = 204
			display.append('HTTP/1.1 204 NO CONTENT')
		try:
			if(os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				err_msg(connectionsocket,403)
			shutil.move(element, TRASH)
		except shutil.Error:
			os.remove(element)
	else:
		num = 400
		display.append('HTTP/1.1 BAD REQUEST')
	print(display)
	display.append('SERVER: ' + Ip)
	display.append('Connection: keep-alive')
	display.append(date())
	display.append('\r\n')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)
	
			
def get_head(connectionsocket, element , switcher, query, method):
	global serversocket, types_to_ext, c_get, connection, Ip, num, cookie_val
	display = []
	isfilethere = os.path.isfile(element)
	isdirthere = os.path.isdir(element)

	if isfilethere:		          #here checking if the file requested by user is read/write accessible 
	                                  #if not displaying error msg Forbidden
		if (os.access(element, os.W_OK) and os.access(element , os.R_OK)):
			pass
		else:
			err_msg(connectionsocket , 403)	

		display.append('HTTP/1.1 200 OK')
		num = 200
		
		try:
			f1 = open(element, "rb")              #opening file in binary format and getting the size
			size = os.path.getsize(element)
			data = f1.read(size)
		except:
			err_msg(connectionsocket, 500)        #if not display server error
	
	elif isdirthere:
	
		if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
			pass
		else:
			err_msg(connectionsocket, 403)
		display.append('HTTP/1.1 200 OK')
		num = 200
		dirlist = os.listdir(element)         #This method returns the list of all files and directories in the specified path. 
		                                       #The return type of this method is list. 
		for l in dirlist:
			if l.startswith('.'):
				dirlist.remove(l)	#If a file name starts with . the file is removed startswith function returns true or false.	

	else:
		element = element.rstrip('/')         #This function returns the part of the string before the /
		isfilethere = os.path.isfile(element)      #Now again checking for files and directory	
		isdirthere = os.path.isdir(element)
		if isfilethere:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				err_msg(connectionsocket, 403)
			display.append('HTTP/1.1 200 OK')
			num = 200
			try:
				f1 = open(element, "rb")
				size = os.path.getsize(element)
				data = f1.read(size)
			except:
				err_msg(connectionsocket, 500)

		elif isdirthere:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				err_msg(connectionsocket, 403)
			display.append('HTTP/1.1 200 OK')
			num = 200
			dirlist = os.listdir(element)
			for l in dirlist:
				if l.startswith('.'):
					dirlist.remove(l)
		else:	
			err_msg(connectionsocket, 404)

	display.append(COOKIE + str(cookie_val) + MAXTIME)
	cookie_val += 1                                        #Every time increasing cookie value by 1 for different clients
	
	for state in switcher:
		if state == 'Host':
			pass
		elif state == 'User-Agent':
			if isfilethere:
				display.append('Server: ' + Ip)
				display.append(date())
				display.append(lastmodified(element))
			elif isdirthere:
				display.append('Server: ' + Ip)
		elif state == 'Accept':
			if isdirthere:
				string = 'Content-Type: text/html'
				display.append(string)
			elif isfilethere:
				try:
					file_ext = os.path.splitext(element)
					if file_ext[1] in types_to_ext.keys():
						string = types_to_ext[file_ext[1]]
					else:
						string = 'text/plain'
					string = 'Content-Type: '+ string
					display.append(string)
				except:
					err_msg(connectionsocket, 415)
		elif state == 'Accept-Language':
			if isfilethere:
				string = 'Content-Language: ' + switcher[state]
				display.append(string)
			elif isdirthere:
				string = 'Content-Language: ' + switcher[state]
				display.append(string)
		elif state == 'Accept-Encoding':
			if isfilethere:
				string = 'Content-Length: ' + str(size)
				display.append(string)
		elif state == 'Connection':
			if isfilethere:
				connection = True
				display.append('Connection: keep-alive')
			elif isdirthere:
				connection = False
				display.append('Connection: close')
		elif state == 'If-Modified-Since':
			if_modify(switcher[state], element)
		
		elif state == 'Cookie':
			cookie_val -= 1 
			display.remove(COOKIE + str(cookie_val) + MAXTIME)
		else:
			continue
			
	if isdirthere and method == 'GET':
		display.append('\r\n')
		display.append('<!DOCTYPE html>')
		display.append('<html>\n<head>')
		display.append('<title>Directory listing</title>')
		display.append('<meta http-equiv="Content-type" content="text/html;charset=UTF-8" /></head>')
		display.append('<body><h1>DIRECTORY LIST</h1><ul>')
		for line in dirlist:
			if element == '/':
				link = 'http://' + Ip + ':' + str(serverport) + element + line
				m = '<li><a href ="'+link+'">'+line+'</a></li>'
				display.append(m)
			else:
				link = 'http://' + Ip + ':' + str(serverport) + element + '/'+ line
				m = '<li><a href ="'+link+'">'+line+'</a></li>'
				display.append(m)
		display.append('</ul></body></html>')
		encoded = '\r\n'.join(display).encode()
		connectionsocket.send(encoded)
		connectionsocket.close()	
	elif len(query) > 0 and not isdirthere and not isfilethere: 
		display = []
		element = CSV
		field = []
		row = []
		for x in query:
			field.append(x)
			for j in query[x]:
				row.append(j)
		check = os.path.exists(element)
		if check:
			file1 = open(element, "a")
			display.append('HTTP/1.1 200 OK')
			num = 200
			csvwrite = csv.writer(file1)
			csvwrite.writerow(row)
		else:
			file1 = open(element, "W")
			display.append('HTTP/1.1 210 CREATED')
			num = 201
			display.append('Location :' + element)
			csvwrite = csv.writer(file1)
			csvwrite.writerow(field)
			csvwrite.writerow(row)	
		file1.close()
		display.append('Server :' +Ip)
		display.append(date())
		f1 = open(VAR, "rb")
		display.append('Content-Language: en-US,en')
		size = os.path.getsize(VAR)
		str1 = 'Content-Length: ' + str(size)
		display.append('Content-Type: text/html')
		display.append(str1)
		display.append(lastmodified(element))
		display.append('\r\n')
		encoded = '\r\n'.join(display).encode()
		connectionsocket.send(encoded)
		connectionsocket.sendfile(f1)
	elif isfilethere:
		display.append('\r\n')
		if c_get == False and method == 'GET':
			encoded = '\r\n'.join(display).encode()
			connectionsocket.send(encoded)
			connectionsocket.sendfile(f1)
		elif c_get == False and method == 'HEAD':
			encoded = '\r\n'.join(display).encode()
			connectionsocket.send(encoded)
		elif c_get == True and (method == 'GET' or method == 'HEAD'):
			status_304(connectionsocket, element)
	else:
		err_msg(connectionsocket, 400)				


def client_recieve(connectionsocket,addr,start):

	global serversocket, types_to_ext, c_get,connection, SIZE, clientlist, SER_RUN, SER_CLOSE, num
	connection = True              
	c_get = False
	url_flag = 0
	display = []
	filedata = b""          
	fflag = 0             #will be using in put method
	
	#here SER_CLOSE = True is interpreted as server is still running if the conditions in while loop are satisfied 
	#only then go in inside a loop and recieve from the client
	
	while connection and SER_RUN and SER_CLOSE:           
		message = connectionsocket.recv(SIZE)         #SIZE = 4096
		try:
			message = message.decode('utf-8')
			requests = message.split('\r\n\r\n')         #Splitting the message recieved from client
			fflag = 0
		
		except UnicodeDecodeError:
			requests = message.split('\r\n\r\n')        
			requests[0] = requests[0].decode(errors = 'ignore')
			fflag = 1
		
		if len(requests)>1:					
			pass
		else:                                       #Wrong message	
			break	
		try:
			log.write(((addr[0]) + ':' + requests[0] + '\n'))
		except:
			pass
		headers = requests[0].split('\r\n')         #seperating headers from the message
		headerlen = len(headers)
		body = requests[1]                          #seperating body from the message
		req_in_head = headers[0].split(' ')         #Seperating first word in headers
		method_in_req = req_in_head[0]              #getting the name of method in first word
		element = req_in_head[1]                    
		version = req_in_head[2]
		
		if element == favicon:
			element = FAVICON                 #FAVICON = root + favicon
		elif element == '/':
			element = os.getcwd()             #if the element in the request header line is / getting the access to working directory
			
		u = urlparse(element)
		element = unquote(u.path)
		if element == '/':
			element = os.getcwd()
		query = parse_qs(u.query)
		
		if (len(element) > URL_length and url_flag == 0):
			err_msg(connectionsocket, 414)            #If the length of url is longer than max length then 
			break                                    #send message to client"request url too long"
		else:
			url_flag = 1
		try:
			version_num = version.split('/')[1]         #getting version number
			if not (version_num == Myversion):           #if version number doens't match send client the message "version not supported" 
				err_msg(connectionsocket, 505)
		except IndexError:
			err_msg(connectionsocket, 505)              #If couldn't find version ,send same message
		
		switcher = {}
		request_in_head = headers.pop(0)                    #The first header is a request line
		for line in headers :
			line_list = line.split(': ')
			switcher[line_list[0]] = line_list[1]       #line_list[0] contains appropriate label for the respective header line_list[1]
			
		
		
		if method_in_req == 'GET' or method_in_req == 'HEAD':               #now comparing the method in the client request and calling appropriate
			get_head(connectionsocket, element, switcher, query, method_in_req)  #functions
			
		elif method_in_req == 'POST':
			post(body, connectionsocket, element,switcher)
			
		elif method_in_req == 'PUT':
			print(element)
			display = put(connectionsocket, addr, body, filedata, element, switcher, fflag)
			
		elif method_in_req == 'DELETE':
			delete(element, connectionsocket, body, switcher)
			connection = False
			connectionsocket.close()						 
		else:
			method_in_req = ''
			break
		logging.info('	{}	{}	{}	{}	{}\n'.format( req_in_head, element, num, addr[0], addr[1],))
	try:
		connectionsocket.close()
		clientlist.remove(connectionsocket)
	except:
		pass			
			
				
				

#Function to give the respective messages
def err_msg(connectionsocket,i):
	
	global Ip,clientlist, num
	num = i
	display = []           
	
	if i == 500:
		display.append('HTTP/1.1 500 INTERNAL SERVER ERROR')                       #Respective error messages to display to client
	elif i == 505:
		display.append('HTTP/1.1 505 HTTP VERSION NOT SUPPORTED')
	elif i == 404:
		display.append('HTTP/1.1 404 NOT FOUND')
	elif i == 403:
		display.append('HTTP/1.1 403 FORBIDDEN')
	elif i == 503:
		display.append('HTTP/1.1 503 SERVER UNAVAILABLE')
	elif i == 414:
		display.append('HTTP/1.1 414 REQUEST URL IS TOO LARGE')	

	display.append('Server: ' + Ip)
	display.append(date())                                                               #Other information along with err_msg
	display.append('\r\n')
	if i == 505:
		dispaly.append('SUPPORTED VERSION _ HTTP/1.1 REST UNSUPPORTED')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)
	try:
		clientlist.remove(connectionsocket)                                          #Closing the connection with client and removing thread
		connectionsocket.close()
	except:
		pass
	server_accept()                                                                      #Accepting other client connection if any

def server_status():

	global SER_RUN, SER_CLOSE, connection
	
	while True:
		todo = input()
		if todo == 'stop':
			SER_RUN = False      #And initially assigned SER_CLOSE = True and connection = True
		elif todo == 'start':
			SER_RUN = True       #SER_CLOSE = True  and connection= True
		elif todo == 'close':
			SER_CLOSE = False     #SER_RUN = True
			connection = False
			break
		
def server_accept():

	global SER_RUN, SER_CLOSE, clientlist
	while SER_CLOSE:
		while SER_RUN:
			if not SER_CLOSE:			#if close input given then directly break connectionsocket
				break
			start = 0
			connectionsocket, addr = serversocket.accept()
			clientlist.append(connectionsocket)									
			if(len(clientlist) < Thread_requests):                     #If the clientlist has space to accomodate new connection socket
			
				start_new_thread(client_recieve,(connectionsocket,addr,start))
			else:                                                      #If not then setting the status of connection as unavailable and closing
										  #the socket  
				err_msg(connectionsocket, 503)
				connectionsocket.close()
	serversocket.close()					

if __name__ == '__main__':

	Ip = '127.0.0.1'
	
	serverport = 1234
	try:
		serversocket.bind(('',serverport))
	except:
		print('SERVER DOES NOT CONNECT')
		sys.exit()
	serversocket.listen(40)
	print('Server listening on '+ 'Port :'+ str(serverport) + ' host :' + Ip +' Website : http://'+ Ip +':'+str(serverport)+'/')	
	start_new_thread(server_status , ()) 
	server_accept()
	sys.exit()			
