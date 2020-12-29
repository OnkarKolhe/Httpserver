import webbrowser
import os
import sys
from socket import *
root = os.getcwd()
client = socket(AF_INET, SOCK_DGRAM)
port = 1234
IP = '127.0.0.1'
client.close()
URL = "http://" + IP + ":" + str(port) + root
def startTAB(url = (URL)):
    webbrowser.open_new_tab(url)
    
startTAB(URL + "/index.html")
startTAB(URL + "/execution.html")
startTAB(URL + "/prog2.sh")

