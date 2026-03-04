from socket import *
import argparse
from threading import *
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich import box
from ports_database import PORTS_DATABASE, get_preset_names, get_preset_ports, get_preset_info

console = Console()
scan_lock = Lock()


def show_presets():
    """Display available port presets with interactive scanning option"""
    table = Table(title="Available Port Presets", box=box.DOUBLE_EDGE, title_style="bold magenta")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Name", style="bold")
    table.add_column("Description", style="yellow")
    table.add_column("Port Count", style="green", justify="center")
    
    preset_names = list(get_preset_names())
    for idx in range(len(preset_names)):
        preset_id = preset_names[idx]
        info = get_preset_info(preset_id)
        table.add_row(
            str(idx + 1),
            f"[cyan]{preset_id}[/cyan]",
            info["name"],
            info["description"],
            str(info["count"])
        )
    
    console.print(table)
    
    # Ask if user wants to scan
    console.print("\n[bold cyan]Press Enter to exit, or follow the prompt to scan:[/bold cyan]")
    user_choice = console.input("[cyan]Enter preset name/ID to scan (e.g., 'web' or '1'), or leave empty to exit: [/cyan]").strip()
    
    if not user_choice:
        return
    
    # Map numeric choice to preset name
    selected_preset = None
    
    try:
        # Try as number
        idx = int(user_choice) - 1
        if 0 <= idx < len(preset_names):
            selected_preset = preset_names[idx]
    except ValueError:
        # Try as name
        if user_choice.lower() in preset_names:
            selected_preset = user_choice.lower()
    
    if not selected_preset:
        console.print(f"[red][✗] Invalid choice: '{user_choice}'[/red]")
        return
    
    # Get target IP
    target = console.input(f"\n[cyan]Enter target IP or hostname to scan with '{selected_preset}' preset: [/cyan]").strip()
    
    if not target:
        console.print("[red][✗] No target provided[/red]")
        return
    
    # Show confirmation
    info = get_preset_info(selected_preset)
    console.print(f"\n[bold green]✓ Scanning {target}[/bold green]")
    console.print(f"[cyan]Preset: {info['name']} ({info['count']} ports)[/cyan]\n")
    
    # Execute scan
    ports = [int(p) for p in get_preset_ports(selected_preset)]
    portScan(target, ports)


def interactive_mode():
    """Interactive menu to select preset and target"""
    console.print(Panel("[bold cyan]Advanced Scanner - Interactive Mode[/bold cyan]", border_style="cyan", padding=1))
    
    # Show available presets
    preset_names = list(get_preset_names())
    
    table = Table(title="Available Port Presets", box=box.DOUBLE_EDGE, title_style="bold magenta")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Name", style="bold")
    table.add_column("Description", style="yellow")
    
    for idx in range(len(preset_names)):
        preset_id = preset_names[idx]
        info = get_preset_info(preset_id)
        table.add_row(
            str(idx + 1),
            f"[cyan]{preset_id}[/cyan]",
            info["name"]
        )
    
    console.print(table)
    
    # Ask user to choose preset
    console.print("\n[bold cyan]Select a preset:[/bold cyan]")
    while True:
        choice = console.input("[cyan]Enter preset name or ID (e.g., 'web' or '1', or 'quit'): [/cyan]").strip().lower()
        if choice == 'quit':
            return
        
        selected_preset = None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(preset_names):
                selected_preset = preset_names[idx]
        except ValueError:
            if choice in preset_names:
                selected_preset = choice
        
        if selected_preset:
            break
        console.print(f"[red]Invalid choice. Available: {', '.join(preset_names)}[/red]")
    
    # Show details
    info = get_preset_info(selected_preset)
    console.print(f"\n[green]✓ Selected: {info['name']}[/green]")
    console.print(f"[dim]{info['description']}[/dim]")
    console.print(f"[cyan]Ports to scan: {info['count']}[/cyan]\n")
    
    # Ask for target
    while True:
        target = console.input("[cyan]Enter target IP or hostname: [/cyan]").strip()
        if target:
            break
        console.print("[red]Please enter a valid target[/red]")
    
    # Confirm and scan
    console.print(f"\n[bold]Starting scan on {target} with {selected_preset} preset...[/bold]\n")
    ports = [int(p) for p in get_preset_ports(selected_preset)]
    portScan(target, ports)


def show_preset_details(preset_id):
    """Display detailed information about a preset"""
    info = get_preset_info(preset_id)
    if not info:
        console.print(f"[red][!] Preset '{preset_id}' not found[/red]")
        return
    
    console.print(Panel(f"[bold cyan]{info['name']}[/bold cyan]\n{info['description']}", 
                       border_style="cyan", padding=1))
    
    table = Table(title=f"Ports in {preset_id}", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Port", style="cyan", justify="center")
    table.add_column("Service", style="bold")
    table.add_column("Description", style="yellow")
    
    for port_info in info["ports"][:20]:  # Show first 20
        table.add_row(
            str(port_info["port"]),
            port_info["service"],
            port_info["description"]
        )
    
    if len(info["ports"]) > 20:
        table.add_row("...", "...", f"...and {len(info['ports']) - 20} more ports")
    
    console.print(table)


class ScanStatus:
    """Track scanning status"""
    def __init__(self, total_ports):
        self.total_ports = total_ports
        self.open_ports = []
        self.closed_ports = []
        self.scanning = 0
        self.completed = 0
        
    def add_open(self, port):
        with scan_lock:
            self.open_ports.append(port)
            self.completed += 1
    
    def add_closed(self, port):
        with scan_lock:
            self.closed_ports.append(port)
            self.completed += 1
    
    def get_progress(self):
        return self.completed, self.total_ports


def connScan(tgtHost, tgtPort, status):
    """Connect-based port scanning with status tracking"""
    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect((tgtHost, tgtPort))
        status.add_open(tgtPort)
    except:
        status.add_closed(tgtPort)
    finally:
        try:
            sock.close()
        except:
            pass


def portScan(tgtHost, tgtPorts):
    """Port scanning with progress tracking"""
    try:
        tgtIP = gethostbyname(tgtHost)
    except:
        console.print(f"[red][!] Unknown Host {tgtHost}[/red]")
        return
    
    try:
        tgtName = gethostbyaddr(tgtIP)
        host_display = tgtName[0]
    except:
        host_display = tgtIP
    
    # Create status tracker
    status = ScanStatus(len(tgtPorts))
    
    console.print(Panel(f"[bold cyan]Scanning Target: {host_display}[/bold cyan]", 
                       border_style="cyan", padding=1))
    
    # Launch scan with progress bar
    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[cyan]{task.description}"),
        console=console,
        transient=False
    ) as progress:
        task = progress.add_task(f"[cyan]Scanning {len(tgtPorts)} ports...", total=len(tgtPorts))
        
        threads = []
        setdefaulttimeout(1)
        
        for tgtPort in tgtPorts:
            t = Thread(target=connScan, args=(tgtHost, int(tgtPort), status))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Update progress as threads complete
        while status.completed < len(tgtPorts):
            progress.update(task, completed=status.completed)
            time.sleep(0.1)
        
        # Wait for all threads to finish
        for t in threads:
            t.join(timeout=0.1)
        
        progress.update(task, completed=len(tgtPorts))
    
    # Display results
    print()
    
    # Table for results
    table = Table(title="Scan Results", box=box.DOUBLE_EDGE, title_style="bold magenta")
    table.add_column("Port", style="cyan", justify="center")
    table.add_column("Status", justify="center")
    
    if status.open_ports:
        for port in sorted(status.open_ports):
            table.add_row(f"{port}/tcp", "[green][+] OPEN[/green]")
    
    if status.closed_ports:
        for port in sorted(status.closed_ports):
            table.add_row(f"{port}/tcp", "[dim][-] Closed[/dim]")
    
    console.print(table)
    
    # Summary
    summary_text = f"\n[bold]Summary:[/bold] [green]{len(status.open_ports)} open[/green], [dim]{len(status.closed_ports)} closed[/dim] out of [cyan]{len(tgtPorts)}[/cyan] ports scanned"
    console.print(summary_text)


def main():
    parser = argparse.ArgumentParser(
        description='Professional Network Port Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
╔═══════════════════════════════════════════════════════════════════╗
║                      QUICK START EXAMPLES                        ║
╚═══════════════════════════════════════════════════════════════════╝

[PRESET MODE - Recommended for beginners]
  python advancedscanner.py -H 192.168.1.1 -x web
  python advancedscanner.py -H example.com -x ssh
  python advancedscanner.py -H 192.168.1.1 -x database
  python advancedscanner.py -H 192.168.1.1 -x mail
  python advancedscanner.py -H 192.168.1.1 -x common
  python advancedscanner.py -H 192.168.1.1 -x all

[LIST & INFO COMMANDS]
  python advancedscanner.py --list              # Show all presets
  python advancedscanner.py --info web          # Details about 'web' preset
  python advancedscanner.py --info database     # Details about 'database'
  python advancedscanner.py -i                  # Interactive mode

[MANUAL MODE]
  python advancedscanner.py -H 192.168.1.1 -p 80,443,22,3306
  python advancedscanner.py -H example.com -p 80,443,8080-8090
  python advancedscanner.py -H 192.168.1.1 -r 1-1000

[AVAILABLE PRESETS]
  web       → HTTP, HTTPS, Node.js, Flask, etc (8 ports)
  ssh       → SSH, Telnet, RDP, VNC (4 ports)
  database  → MySQL, PostgreSQL, MongoDB, Redis (7 ports)
  mail      → SMTP, POP3, IMAP (6 ports)
  dns       → DNS Server (1 port)
  directory → LDAP, Kerberos, SMB (5 ports)
  monitoring→ SNMP, Netdata (4 ports)
  ntp       → NTP Time (1 port)
  vpn       → OpenVPN, IKE, PPTP (3 ports)
  common    → Top 20 most used ports
  all       → Comprehensive scan (ports 1-10000)

[WHAT EACH PRESET SCANS]
  -x web        → 80(HTTP), 443(HTTPS), 3000, 5000, 8080, 8443...
  -x ssh        → 22(SSH), 23(Telnet), 3389(RDP), 5900(VNC)
  -x database   → 3306(MySQL), 5432(PostgreSQL), 1433(MSSQL)...
  -x mail       → 25(SMTP), 110(POP3), 143(IMAP), 587, 993, 995
  -x common     → Top 20 - 22, 25, 53, 80, 110, 143, 443, 445...
  -x all        → All ports 1-10000 (comprehensive scan)

        """
    )
    
    parser.add_argument('-H', '--host', dest='tgtHost', type=str, 
                        help='Target host/IP address')
    parser.add_argument('-p', '--ports', dest='tgtPort', type=str, 
                        help='Specific ports: 80,443,22,3306 or 80,443,8080-8090')
    parser.add_argument('-r', '--range', dest='portRange', type=str,
                        help='Port range: 1-1000 or 1000-2000')
    parser.add_argument('-x', '--preset', dest='preset', type=str,
                        help='Use preset: web, ssh, database, mail, common, all, etc')
    parser.add_argument('-i', '--interactive', dest='interactive', action='store_true',
                        help='Interactive mode - choose preset from menu')
    parser.add_argument('--list', dest='list_presets', action='store_true',
                        help='List all available presets with info')
    parser.add_argument('--info', dest='preset_info', type=str,
                        help='Show detailed ports for a preset: --info web')
    
    args = parser.parse_args()
    
    # Handle interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Handle list presets
    if args.list_presets:
        show_presets()
        return
    
    # Handle preset info
    if args.preset_info:
        show_preset_details(args.preset_info)
        return
    
    # Determine which ports to scan
    tgtPorts = []
    
    if args.preset:
        ports = get_preset_ports(args.preset)
        if ports is None:
            console.print(f"[red][✗] Preset '{args.preset}' not found[/red]")
            console.print("[yellow]Use: python advancedscanner.py --list[/yellow]")
            return
        tgtPorts = [int(p) for p in ports]
    elif args.portRange:
        try:
            start, end = map(int, args.portRange.split('-'))
            tgtPorts = list(range(start, end + 1))
        except:
            console.print("[red][✗] Invalid port range format[/red]")
            return
    elif args.tgtPort:
        tgtPorts = []
        for port_spec in args.tgtPort.split(','):
            if '-' in port_spec:
                try:
                    start, end = map(int, port_spec.split('-'))
                    tgtPorts.extend(range(start, end + 1))
                except:
                    pass
            else:
                try:
                    tgtPorts.append(int(port_spec))
                except:
                    pass
    else:
        console.print("[red][✗] Specify ports with -p, -r, or -x[/red]")
        console.print("[cyan]Examples:[/cyan]")
        console.print("  python advancedscanner.py -H 192.168.1.1 -x web")
        console.print("  python advancedscanner.py -H 192.168.1.1 -x common")
        console.print("  python advancedscanner.py -H 192.168.1.1 -p 80,443,22")
        return
    
    if not tgtPorts:
        console.print("[red][✗] No valid ports specified[/red]")
        return
    
    if not args.tgtHost:
        console.print("[red][✗] Target host (-H) is required[/red]")
        console.print("[cyan]Example:[/cyan]")
        console.print("  python advancedscanner.py -H 192.168.1.1 -x web")
        return
    
    portScan(args.tgtHost, tgtPorts)


def get_args():
    return [
        {"flag": "-H, --host", "desc": "Target IP or hostname"},
        {"flag": "-x, --preset", "desc": "Quick preset: web, ssh, database, mail, common, all"},
        {"flag": "-p, --ports", "desc": "Manual ports: 80,443,22 or 8080-8090"},
        {"flag": "-r, --range", "desc": "Port range: 1-1000"},
        {"flag": "-i, --interactive", "desc": "Interactive mode - choose from menu"},
        {"flag": "--list", "desc": "List all presets"},
        {"flag": "--info PRESET", "desc": "Details of preset"},
    ]

if __name__ == '__main__':
    main()    


