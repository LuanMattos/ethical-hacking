import crypt
from termcolor import colored

def crackPass(cryptWord):
    salt = cryptWord[0:2]
    dictionary = open("dictionary.txt", "r")
    for word in dictionary.readlines():
        word = word.strip('\n')
        cryptPass = crypt.crypt(word, salt)
        if (cryptWord == cryptPass):
            print(colored("[+] Found password: " + word, 'green'))
        else:
            print( colored("[-] Not Found password: " + word, 'red'))


def main():
    passFile = open('pass2.txt', 'r')
    for line in passFile.readlines():
        if ":" in line:
            user = line.split(':')[0]
            cryptWord = line.split(':')[1].strip( ).strip('\n')
            print("[*] Cracking password for: " + user)
            crackPass(cryptWord)


main()
