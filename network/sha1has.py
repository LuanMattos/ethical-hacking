from urllib.request import urlopen
import hashlib

sha1hash = input("[*] Enter sha1 Hash Value: ")
passlist = str(urlopen('https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt').read(), 'utf-8')

for password in passlist.split('\n'):
    hashguess = hashlib.sha1(bytes(password, 'utf-8')).hexdigest()
    if hashguess == sha1hash:
        print("[+] The password is: " + str(password))
        quit()
    else:
        print("[-] Password guess" + str(password) + " does not match, tryng next ...")

print("Password not in passwordlist")
