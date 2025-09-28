#!/usr/bin/python

import socket
import os
import sys
from difflib import SequenceMatcher

def _strip(aaaa):
    return aaaa.strip("\/n").strip("b'").strip("\/r").strip("\/r\/n")

#Recebe o banner do Host através do socket
def retBanner(ip, port):
    try:
        socket.setdefaulttimeout(2)
        s = socket.socket()
        s.connect((ip,port))
        banner = s.recv(1024)
        return banner
    except:
        return
#Obtem a pontuação da similaridade da string do banner    
def similar_strings(str1, str2):
    seq_matcher = SequenceMatcher(None, str1, str2)
    similaridade = seq_matcher.ratio()
    
    return similaridade
    
def checkVulns(banner, filename):
    f = open(filename, "r")
    
    for line in f.readlines():
 
        if similar_strings(line, str(banner)) > 0.5:
            print("     [!] Server is vulnerable: " + str(banner))

def main():
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        if not os.path.isfile(filename):
            print('[-] File Doesnt Exist')
            exit(0)
        if not os.access(filename, os.R_OK):
            print('[-] Access Denied!')
            exit(0)
    else:
        print('[-] Usage: ' + str(sys.argv[0]) + '<vuln filename>')
        exit(0)
    portlist = [21,22,25,80,110,443,445]
    for x in range(41,42):
        ip = "192.168.100." + str(x)
        for port in portlist:
            banner = retBanner(ip, port)
            if banner:
                print('[+] ' + ip + '/' + str(port) + " : " + _strip(str(banner)))
                checkVulns(banner, filename)

main()
