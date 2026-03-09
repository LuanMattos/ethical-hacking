import hashlib

hashvalue = input("Enter a string to hash: ")

hashobj1 = hashlib.md5()
hashobj1.update(hashvalue.encode())
print('md5: \n' + hashobj1.hexdigest())

hashobj2 = hashlib.sha1()
hashobj2.update(hashvalue.encode())
print('sha1: \n' + hashobj2.hexdigest())

hashobj3 = hashlib.sha224()
hashobj3.update(hashvalue.encode())
print('sha224: \n' + hashobj3.hexdigest())

hashobj4 = hashlib.sha256()
hashobj4.update(hashvalue.encode())
print('sha256: \n' +hashobj4.hexdigest())

hashobj5 = hashlib.sha512()
hashobj5.update(hashvalue.encode())
print('sha512: \n' + hashobj5.hexdigest())

