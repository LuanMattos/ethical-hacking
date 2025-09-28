#!/usr/bin/python

import socket
from termcolor import colored
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#socket.setdefaulttimeout(1)

host = input("[*] Enter Host to scan: ")

def portscanner(port):
	if sock.connect_ex((host,port)):
		print(colored("[!!] Port %d is closed" % (port), 'red'))
	else:
		print(colored("[+] Port %d is opened" % (port), 'green'))


for port in range(1,65535):
	portscanner(port)
