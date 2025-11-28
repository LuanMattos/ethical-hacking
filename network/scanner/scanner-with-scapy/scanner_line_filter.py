import argparse
from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import Ether

def scapy_filter(pkt, expression):
    """Avalia se um pacote confere com a expressão de filtro."""
    # Expressões básicas: "proto.field == value"
    # Exemplo: "ip.dst == 192.168.0.1"
    try:
        if "==" in expression:
            left, right = expression.split("==", 1)
            left = left.strip()
            right = right.strip()
            if "." in left:
                proto, field = left.split(".", 1)
            else:
                proto, field = left, ""
            proto = proto.lower()
            # Identifique o protocolo
            scapy_layer = {
                'ip': IP,
                'tcp': TCP,
                'udp': UDP,
                'icmp': ICMP,
                'ether': Ether,
            }.get(proto)
            if not scapy_layer or not pkt.haslayer(scapy_layer):
                return False
            scapy_pkt = pkt[scapy_layer]
            if hasattr(scapy_pkt, field):
                value = getattr(scapy_pkt, field)
                return str(value) == right
        # Default: Tudo passa se não reconhecer o filtro
        return True
    except Exception:
        return False

def format_pkt(pkt):
    """Formata o pacote em linha única, estilo Wireshark."""
    summary = pkt.summary()
    return summary

def main():
    parser = argparse.ArgumentParser(description="Scanner with filters like Wireshark (simple)")
    parser.add_argument("-i", "--interface", help="Network interface", default=None)
    parser.add_argument("-f", "--filter", help="Filter, ex: 'ip.dst == 192.168.1.1'", default="")
    parser.add_argument("-c", "--count", type=int, help="Number of packets to capture (Ctrl+C to stop)", default=0)
    args = parser.parse_args()

    print(f"[*] Capturing in interface: {args.interface or 'wlan0'}")
    if args.filter:
        print(f"[*] Active filter: {args.filter}")

    def pkt_callback(pkt):
        if not args.filter or scapy_filter(pkt, args.filter):
            print(format_pkt(pkt))

    sniff(prn=pkt_callback, iface=args.interface, count=args.count)

if __name__ == "__main__":
    main()