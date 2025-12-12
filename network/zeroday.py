import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme
from rich import box
from pathlib import Path
import importlib.util

console = Console(theme=Theme({
    "title": "bold magenta",
    "option": "bold cyan",
    "desc": "italic dim yellow",
    "warn": "bold red"
}))

ASCII_LOGO = r"""
    ░██████╗███████╗██████╗░░█████╗░██████╗░░█████╗░██╗░░░██╗
    ██╔═══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗╚██╗░██╔╝
    ██║██╗██║█████╗░░██████╔╝███████║██████╔╝███████║░╚████╔╝░
    ╚██████╔╝██╔══╝░░██╔══██╗██╔══██║██╔═══╝░██╔══██║░░╚██╔╝░░
    ░╚═██╔═╝░███████╗██║░░██║██║░░██║██║░░░░░██║░░██║░░░██║░░░
    ░░░╚═╝░░░╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝░░╚═╝░░░╚═╝░░░
    (Skull - ZeroDay)
"""

DESCRIPTION = """
[desc]Welcome to [b]ZeroDay[/b], a hacking tool for all possible scenarios.
Here you'll find scanners, network attacks like ARP spoofing, wireless attacks, persistence, and much more.

[desc]Follow me on Instagram: [b cyan]@zero_s_day[/b cyan]
[desc]GitHub: [cyan]https://github.com/LuanMattos/[/cyan]

[desc]⚠️ [warn]This tool is for serious cybersecurity professionals only. Practicing unethical hacking is a crime![/warn]
"""

SCRIPTS_PATH = Path(__file__).parent
NETWORK_TOOLS_PATH = SCRIPTS_PATH

# Mapeie aqui os módulos. O label mostrado, caminho do script e um ícone/símbolo bonito
TOOLS = [
    {"icon": "🌐", "name": "Advanced Scanner",      "path": "advancedscanner.py",           "desc": "Network host discovery and port scanning"},
    {"icon": "🤖", "name": "Backdoor & Persistence","path": "backdoor-and-persistence/main.py","desc": "Persistence & backdoor modules"},
    {"icon": "🔑", "name": "BruteSH",               "path": "brutesh/main.py",               "desc": "SSH brute force attack tool"},
    {"icon": "🔒", "name": "CryptForce",            "path": "cryptforce/main.py",            "desc": "Password/password hash cracking"},
    {"icon": "🔎", "name": "Network Scanners",      "path": "scanner/scanner_line_filter.py","desc": "Live packet capture and filtering"},
    {"icon": "📡", "name": "AICrack Wireless Attack", "path": "aicrack.py",                   "desc": "Automated wireless (WPA deauth) attacks"},
    # Adicione mais conforme for expandindo...
]

def print_logo():
    console.print(Panel.fit(ASCII_LOGO, style="title", padding=1, width=75, border_style="magenta"))

def print_description():
    console.print(DESCRIPTION, highlight=True)

def main_menu():
    table = Table(title="Available Modules", box=box.DOUBLE_EDGE, title_style="bold magenta")
    table.add_column("Option", style="option", justify="center")
    table.add_column("Module", style="option")
    table.add_column("Description", style="desc")
    for idx, tool in enumerate(TOOLS, 1):
        table.add_row(
            f"[bold blue]{tool['icon']} {idx}[/bold blue]",
            f"[bold]{tool['name']}[/bold]",
            tool['desc']
        )
    console.print(table)

def run_tool(index):
    tool = TOOLS[index]
    tool_path = NETWORK_TOOLS_PATH / tool["path"]
    if not tool_path.exists():
        console.print(f"[warn][!] Module not found: {tool_path}[/warn]")
        return
    
    # --- Load modules ---
    spec = importlib.util.spec_from_file_location("module", tool_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


    # --- Has get_args? ---
    if hasattr(module, "get_args"):
        args_info = module.get_args()

        # Show nice tables
        table = Table(title=f"Arguments for {tool['name']}", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("Flag", style="cyan", justify="center")
        table.add_column("Description", style="yellow")

        for arg in args_info:
            table.add_row(arg["flag"], arg["desc"])

        console.print(table)
    else:
        args_info = []
        console.print("[desc]This module does not provide argument info.\n")

    # --- Answaer args ---
    args = Prompt.ask("[option]Enter arguments (or leave empty)", default="")

    console.print(f"[desc]Launching [b]{tool['name']}[/b]...\n")

    import subprocess
    cmd = [sys.executable, str(tool_path)] + args.split()
    subprocess.run(cmd)

def main():
    print_logo()
    print_description()
    while True:
        main_menu()
        choice = Prompt.ask("\n[option]Select an option", choices=[str(i+1) for i in range(len(TOOLS))], default="1")
        run_tool(int(choice)-1)
        again = Prompt.ask("[option]Back to menu? (y/n)", choices=["y", "n"], default="y")
        if again == "n":
            console.print("[desc]Goodbye!")
            break

if __name__ == "__main__":
    main()