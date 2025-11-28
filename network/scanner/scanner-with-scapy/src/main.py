"""
main.py

Entrypoint: inicia o sniffer e lança a GUI.
"""

import argparse
import sys
import os

# Tentativa de importar como pacote ou como módulo direto (para execução flexível)
try:
    from . import capture
    from .gui import ProtocolVisualizer
except Exception:
    import capture
    from gui import ProtocolVisualizer

def parse_args():
    parser = argparse.ArgumentParser(description="Simple Scanner — Network Protocol Visualizer (Scapy + Tkinter)")
    parser.add_argument("-i", "--interface", help="Interface to sniff (default: system default)")
    parser.add_argument("-f", "--filter", help="pcap/BPF filter expression (e.g. 'port 53')")
    return parser.parse_args()

def check_privileges():
    # Em POSIX, sniffing geralmente exige root.
    if os.name != "nt":
        try:
            if os.geteuid() != 0:
                print("Aviso: sniffing geralmente requer privilégios root. Execute com sudo se não aparecerem pacotes.", file=sys.stderr)
        except AttributeError:
            pass

def main():
    args = parse_args()
    check_privileges()

    try:
        capture.start_sniff(interface=args.interface, bpf_filter=args.filter)
    except Exception as e:
        print("Falha ao iniciar sniffer:", e, file=sys.stderr)

    app = ProtocolVisualizer()
    app.mainloop()

if __name__ == "__main__":
    main()