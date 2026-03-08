#!/usr/bin/python

import socket
import argparse


# simple banner grabber utility

def retBanner(ip, port):
    try:
        socket.setdefaulttimeout(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        banner = s.recv(1024)
        return banner
    except Exception:
        return None
    finally:
        try:
            s.close()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="Basic banner grabbing tool")
    parser.add_argument('-t', '--target', required=True,
                        help='Target host or IP')
    parser.add_argument('-p', '--ports', default='1-65535',
                        help='Port range (e.g. 1-1024 or 22,80,443)')
    args = parser.parse_args()

    ip = args.target
    ports = []
    for spec in args.ports.split(','):
        if '-' in spec:
            a, b = spec.split('-')
            try:
                start, end = int(a), int(b)
                ports.extend(range(start, end + 1))
            except ValueError:
                pass
        else:
            try:
                ports.append(int(spec))
            except ValueError:
                pass

    for port in ports:
        banner = retBanner(ip, port)
        if banner:
            try:
                service = socket.getservbyport(port, 'tcp')
            except OSError:
                service = None
            svc_text = f" ({service})" if service else ''
            print(f"[+] {ip}/{port}{svc_text}: {banner.decode('utf-8', errors='ignore').strip()}")

if __name__ == '__main__':
    main()
