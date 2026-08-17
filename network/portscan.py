#!/usr/bin/python

import socket
from termcolor import colored

# prompt the user for the host to scan
host = input("[*] Enter Host to scan: ")


def portscanner(port):
    """Attempt a TCP connection to the given port and print status.

    If the standard services database knows the port, include the service
    name in the output (e.g. 23 → telnet).
    """
    # look up the well‑known service name for this port (tcp)
    try:
        service = socket.getservbyport(port, "tcp")
    except OSError:
        service = None

    # create a fresh socket for each attempt to avoid reuse issues
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
    except Exception:
        result = 1
    finally:
        sock.close()

    status_text = "open" if result == 0 else "closed"
    if service:
        message = f"Port {port} is {status_text} ({service})"
    else:
        message = f"Port {port} is {status_text}"

    color = 'green' if status_text == 'open' else 'red'
    prefix = '[+] ' if status_text == 'open' else '[!!] '
    print(colored(prefix + message, color))


for port in range(1, 65535):
    portscanner(port)
