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

# build a simple lookup mapping port -> (service, description)
PORT_INFO = {}
for preset in PORTS_DATABASE.values():
    for p in preset.get("ports", []):
        try:
            portnum = int(p.get("port", 0))
        except Exception:
            continue
        PORT_INFO[portnum] = (p.get("service", ""), p.get("description", ""))

console = Console()
scan_lock = Lock()

# global flag to enable banner grabbing after open-port detection
BANNER_MODE = False


def grab_banner(host, port):
    """Attempt to retrieve a service banner from an open TCP port.

    A simple connect + recv(1024). Returns a decoded string or None if
    nothing was received or the attempt failed.
    """
    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((host, port))
        data = sock.recv(1024)
        if not data:
            return None
        # decode gracefully and strip newline/NULLs
        return data.decode('utf-8', errors='ignore').strip('\r\n\x00')
    except Exception:
        return None
    finally:
        try:
            sock.close()
        except Exception:
            pass



def show_presets(scan_method="tcp"):
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
    portScan(target, ports, scan_method)


def interactive_mode(scan_method="tcp", banner=False):
    """Interactive menu to select preset, method, and optional banner grabbing."""
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
    
    # Ask for method if not provided
    if not scan_method:
        scan_method = console.input("[cyan]Scan method (tcp/syn/icmp/udp/fin) [tcp]: [/cyan]").strip().lower() or "tcp"
    else:
        # allow user to override default method
        override = console.input(f"[cyan]Use default method '{scan_method}'? (y/n): [/cyan]").strip().lower()
        if override == 'n':
            scan_method = console.input("[cyan]New scan method (tcp/syn/icmp/udp/fin): [/cyan]").strip().lower() or "tcp"
    
    # Banner option
    if not banner:
        use_banner = console.input("[cyan]Grab banners for open ports? (y/n) [n]: [/cyan]").strip().lower()
        if use_banner == 'y':
            banner = True
    
    # apply banner setting globally
    global BANNER_MODE
    BANNER_MODE = banner
    
    # Confirm and scan
    console.print(f"\n[bold]Starting scan on {target} with {selected_preset} preset using {scan_method.upper()} scan{' with banners' if banner else ''}...[/bold]\n")
    ports = [int(p) for p in get_preset_ports(selected_preset)]
    portScan(target, ports, scan_method)


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
    """TCP Connect Scan - Full connection handshake"""
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


def synScan(tgtHost, tgtPort, status):
    """SYN Scan (Half-open) - Requires elevated privileges (Windows/Linux)"""
    console.print("[yellow][!] Note: SYN Scan requires elevated privileges - falling back to TCP Connect[/yellow]")
    # Fallback to TCP Connect on non-Linux or non-admin
    connScan(tgtHost, tgtPort, status)


def icmpPingScan(tgtHost, status):
    """ICMP Ping Scan - Check if host is alive"""
    try:
        sock = socket(AF_INET, SOCK_RAW, 1)
    except PermissionError:
        console.print("[yellow][!] ICMP requires elevated privileges - checking with TCP instead[/yellow]")
        # Try simple TCP connection as fallback
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.settimeout(1)
            s.connect((tgtHost, 80))
            s.close()
            status.add_open(80)
        except:
            status.add_closed(80)
        return
    
    # Send simple ICMP echo request (simplified)
    try:
        sock.settimeout(1)
        sock.connect((tgtHost, 1))
        status.add_open(80)
    except:
        status.add_closed(80)
    finally:
        try:
            sock.close()
        except:
            pass


def udpScan(tgtHost, tgtPort, status):
    """UDP Scan - For UDP-based services"""
    try:
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.settimeout(1)
        sock.sendto(b"", (tgtHost, tgtPort))
        try:
            data, addr = sock.recvfrom(1024)
            status.add_open(tgtPort)
        except timeout:
            # Open|Filtered
            status.add_open(tgtPort)
    except:
        status.add_closed(tgtPort)
    finally:
        try:
            sock.close()
        except:
            pass


def finNullXmasScan(tgtHost, tgtPort, status):
    """FIN/NULL/Xmas Scan - Requires elevated privileges (Windows/Linux)"""
    console.print("[yellow][!] FIN/NULL/Xmas Scan requires elevated privileges - falling back to TCP Connect[/yellow]")
    # Fallback to TCP Connect
    connScan(tgtHost, tgtPort, status)


def portScan(tgtHost, tgtPorts, scan_method="tcp"):
    """Port scanning with progress tracking

    If :pyvar:`BANNER_MODE` is True, perform a banner grab for every open
    port after the scan and append the banner text to the description
    column in the results table.
    """
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
    
    console.print(Panel(f"[bold cyan]Scanning Target: {host_display}[/bold cyan]\n[cyan]Method: {scan_method.upper()}[/cyan]", 
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
        task = progress.add_task(f"[cyan]Scanning {len(tgtPorts)} ports with {scan_method.upper()}...", total=len(tgtPorts))
        
        threads = []
        setdefaulttimeout(1)
        
        # Select scan method
        if scan_method.lower() == "tcp":
            scan_func = connScan
        elif scan_method.lower() == "syn":
            scan_func = synScan
        elif scan_method.lower() == "icmp":
            scan_func = lambda host, status: icmpPingScan(host, status)
        elif scan_method.lower() == "udp":
            scan_func = udpScan
        elif scan_method.lower() == "fin":
            scan_func = finNullXmasScan
        else:
            scan_func = connScan
        
        for tgtPort in tgtPorts:
            if scan_method.lower() == "icmp":
                # ICMP is special - scan host once
                t = Thread(target=scan_func, args=(tgtHost, status))
            else:
                t = Thread(target=scan_func, args=(tgtHost, int(tgtPort), status))
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
    
    # Determine if we should hide closed ports (large/full-range scans)
    show_closed = True
    if len(tgtPorts) >= 10000:
        show_closed = False
        if status.open_ports:
            console.print("[yellow]Note: suppressing closed ports for large scan, only showing open ports[/yellow]")
        else:
            console.print("[yellow]Note: suppressing closed ports for large scan; no open ports detected[/yellow]")
    
    # Table for results (include service/description when available)
    table = Table(title="Scan Results", box=box.DOUBLE_EDGE, title_style="bold magenta")
    table.add_column("Port", style="cyan", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Description", style="yellow")
    
    if status.open_ports:
        for port in sorted(status.open_ports):
            svc, desc = PORT_INFO.get(port, ("", ""))
            desc_text = desc or svc
            if BANNER_MODE:
                banner = grab_banner(tgtHost, port)
                if banner:
                    desc_text = f"{desc_text} | banner: {banner}"
            table.add_row(f"{port}/tcp", "[green][+] OPEN[/green]", desc_text)
    elif not show_closed:
        # no open ports in large scan; don't print anything else
        console.print("[green]No open ports found.[/green]")
    
    if show_closed and status.closed_ports:
        for port in sorted(status.closed_ports):
            svc, desc = PORT_INFO.get(port, ("", ""))
            desc_text = desc or svc
            table.add_row(f"{port}/tcp", "[dim][-] Closed[/dim]", desc_text)
    
    if status.open_ports or show_closed:
        console.print(table)
    
    # Summary
    if show_closed:
        summary_text = f"\n[bold]Summary:[/bold] [green]{len(status.open_ports)} open[/green], [dim]{len(status.closed_ports)} closed[/dim] out of [cyan]{len(tgtPorts)}[/cyan] ports scanned"
    else:
        summary_text = f"\n[bold]Summary:[/bold] [green]{len(status.open_ports)} open[/green] out of [cyan]{len(tgtPorts)}[/cyan] ports scanned (closed ports hidden)"
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
  all       → Comprehensive scan (ports 1-65535)

[WHAT EACH PRESET SCANS]
  -x web        → 80(HTTP), 443(HTTPS), 3000, 5000, 8080, 8443...
  -x ssh        → 22(SSH), 23(Telnet), 3389(RDP), 5900(VNC)
  -x database   → 3306(MySQL), 5432(PostgreSQL), 1433(MSSQL)...
  -x mail       → 25(SMTP), 110(POP3), 143(IMAP), 587, 993, 995
  -x common     → Top 20 - 22, 25, 53, 80, 110, 143, 443, 445...
  -x all        → All ports 1-65535 (comprehensive scan)

# new section for banner
[ADDITIONAL FLAGS]
  -M method    → Scan method: tcp/syn/icmp/udp/fin
  -B           → Grab banners from open ports (slows scan)

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
    parser.add_argument('-M', '--method', dest='scanMethod', type=str, default='tcp',
                        choices=['tcp', 'syn', 'icmp', 'udp', 'fin'],
                        help='Scan method: tcp (TCP Connect), syn (SYN/Half-open), icmp (ICMP Ping), udp (UDP), fin (FIN/NULL/Xmas) - default: tcp')
    parser.add_argument('-B', '--banner', dest='banner', action='store_true',
                        help='Grab a banner from each open port (slow)')
    parser.add_argument('-i', '--interactive', dest='interactive', action='store_true',
                        help='Interactive mode - choose preset from menu')
    parser.add_argument('--list', dest='list_presets', action='store_true',
                        help='List all available presets with info')
    parser.add_argument('--info', dest='preset_info', type=str,
                        help='Show detailed ports for a preset: --info web')
    
    args = parser.parse_args()
    
    # Handle interactive mode
    if args.interactive:
        # pass both scan method and banner preference into interactive mode
        interactive_mode(args.scanMethod, banner=args.banner)
        return

    # set global banner flag early so portScan can use it
    global BANNER_MODE
    if args.banner:
        BANNER_MODE = True

    
    # Handle list presets
    if args.list_presets:
        show_presets(args.scanMethod)
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
    
    portScan(args.tgtHost, tgtPorts, args.scanMethod)


def get_args():
    return [
        {"flag": "-H, --host", "desc": "Target IP or hostname"},
        {"flag": "-x, --preset", "desc": "Quick preset: web, ssh, database, mail, common, all"},
        {"flag": "-p, --ports", "desc": "Manual ports: 80,443,22 or 8080-8090"},
        {"flag": "-r, --range", "desc": "Port range: 1-1000"},
        {"flag": "-M, --method", "desc": "Scan method: tcp/syn/icmp/udp/fin"},
        {"flag": "-B, --banner", "desc": "Grab banner from open ports"},
        {"flag": "-i, --interactive", "desc": "Interactive mode - choose from menu"},
        {"flag": "--list", "desc": "List all presets"},
        {"flag": "--info PRESET", "desc": "Details of preset"},
    ]

if __name__ == '__main__':
    main()    


