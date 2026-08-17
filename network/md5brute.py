from termcolor import colored
import hashlib



def tryOpen(wordlist):
    global pass_file
    try:
        pass_file = open(wordlist, "r")
    except:
        print("[!!] No such File at that path")


pass_hash = input("[+] Enter MD5 Hash value: ")
wordlist = input("[+] Enter Path To the password File: ")

tryOpen(wordlist)

for word in pass_file:
    print(colored("[-] Trying:" + word.strip("\n"), 'red'))
    enc_wrd = word.encode('utf-8')
    md5digest = hashlib.md5(enc_wrd.strip()).hexdigest()

    if md5digest == pass_hash:
        print(colored("[+] Password Found: " + word, 'green'))
        exit(0)

print("[!!] Password Not In List!")
