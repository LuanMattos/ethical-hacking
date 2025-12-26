import os
import sys
import shlex
import importlib.util
import subprocess
from pathlib import Path
from typing import List, Optional

# --- Dependency Check ---
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.theme import Theme
    from rich import box
except ImportError:
    print("Error: 'rich' library is missing. Please run: pip install rich")
    sys.exit(1)

# --- Configuration ---
console = Console(theme=Theme({
    "title": "bold magenta",
    "option": "bold cyan",
    "desc": "italic dim yellow",
    "warn": "bold red",
    "success": "bold green",
    "info": "bold blue"
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

# Tool Definitions
TOOLS = [
    {"icon": "🌐", "name": "Advanced Scanner",      "path": "advancedscanner.py",           "desc": "Network host discovery and port scanning"},
    {"icon": "🤖", "name": "Backdoor & Persistence","path": "backdoor-and-persistence/main.py","desc": "Persistence & backdoor modules"},
    {"icon": "🔑", "name": "BruteSH",               "path": "brutesh/main.py",               "desc": "SSH brute force attack tool"},
    {"icon": "🔒", "name": "CryptForce",            "path": "cryptforce/main.py",            "desc": "Password/password hash cracking"},
    {"icon": "🔎", "name": "Network Scanners",      "path": "scanner/scanner_line_filter.py","desc": "Live packet capture and filtering"},
    {"icon": "📡", "name": "AICrack Wireless Attack", "path": "aicrack.py",                   "desc": "Automated wireless (WPA deauth) attacks"},
]

# --- Argument Overrides ---

MANUAL_ARG_OVERRIDES = {
    "Advanced Scanner": [
        {"flag": "-H", "desc": "Target Host IP (required)"},
        {"flag": "-P", "desc": "Target Port (required) [Capital P]"},
    ]
}

# --- Helper Functions ---

def clear_screen():
    """Clears the console screen cross-platform."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_logo():
    """Prints the banner and logo."""
    console.print(Panel.fit(ASCII_LOGO, style="title", padding=1, width=75, border_style="magenta"))

def print_description():
    """Prints the tool description."""
    console.print(DESCRIPTION, highlight=True)

def main_menu():
    """Displays the main menu table."""
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

def get_tool_args_info(tool_name: str, module_path: Path) -> List[dict]:
    """
    Retrieves argument info. 
    Priority:
    1. MANUAL_ARG_OVERRIDES (fixes issues in sub-scripts)
    2. module.get_args() (dynamic loading)
    """
    # 1. Check Overrides
    if tool_name in MANUAL_ARG_OVERRIDES:
        return MANUAL_ARG_OVERRIDES[tool_name]

    # 2. Check Module
    try:
        spec = importlib.util.spec_from_file_location("module", module_path)
        if spec is None or spec.loader is None:
            return []
        
        module = importlib.util.module_from_spec(spec)
        # Safely execute module to access attributes
        try:
            spec.loader.exec_module(module)
        except Exception:
            pass

        if hasattr(module, "get_args") and callable(module.get_args):
            return module.get_args()
            
    except Exception as e:
        console.print(f"[warn][!] Failed to inspect module args: {e}[/warn]")
        
    return []

def validate_args(user_args_str: str, args_info: List[dict]) -> bool:
    """
    Checks if required arguments are present.
    """
    missing = []
    # Split user args safely
    user_args_parts = shlex.split(user_args_str)
    
    for arg in args_info:
        flag = arg.get("flag", "")
        desc = arg.get("desc", "").lower()
        
        # Check if argument is marked as required in description
        if "required" in desc:
            if flag not in user_args_parts:
                missing.append(f"{flag} ({arg.get('desc')})")
    
    if missing:
        console.print("\n[warn]⚠️  MISSING REQUIRED ARGUMENTS:[/warn]")
        for m in missing:
            console.print(f"  - [bold red]{m}[/bold red]")
        
        console.print("\n[desc]Running the tool without these may cause it to crash.[/desc]")
        choice = Prompt.ask("[option]Do you want to proceed anyway? (y/n)[/option]", choices=["y", "n"], default="n")
        return choice == "y"
        
    return True

def run_tool(index: int):
    """Handles the execution of a selected tool."""
    tool = TOOLS[index]
    tool_path = NETWORK_TOOLS_PATH / tool["path"]
    
    # 1. Validation
    if not tool_path.exists():
        console.print(f"[warn][!] Module not found: {tool_path}[/warn]")
        input("\nPress Enter to continue...")
        return
    
    # 2. Argument Introspection
    console.print(f"[info]Loading {tool['name']} info...[/info]")
    args_info = get_tool_args_info(tool["name"], tool_path)

    if args_info:
        table = Table(title=f"Arguments for {tool['name']}", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("Flag", style="cyan", justify="center")
        table.add_column("Description", style="yellow")

        for arg in args_info:
            table.add_row(str(arg.get("flag", "?")), str(arg.get("desc", "")))
        console.print(table)
    else:
        console.print("[desc]No specific argument info available.[/desc]\n")

    # 3. User Input Loop
    while True:
        user_args = Prompt.ask("[option]Enter arguments[/option]", default="")
        
        # Validate inputs against requirements
        if args_info:
            if validate_args(user_args, args_info):
                break 
            else:
                console.print("[info]Please enter the arguments again.[/info]\n")
        else:
            break

    console.print(f"\n[desc]Launching [b]{tool['name']}[/b]...[/desc]")
    console.print(f"[desc]Press [bold red]Ctrl+C[/bold red] to stop the tool execution.[/desc]\n")

    # 4. Execution
    try:
        cmd_args = shlex.split(user_args)
        cmd = [sys.executable, str(tool_path)] + cmd_args
        
        # Run subprocess safely
        subprocess.run(cmd, check=False)
        
    except KeyboardInterrupt:
        console.print("\n\n[warn]Execution interrupted by user (Ctrl+C).[/warn]")
    except Exception as e:
        console.print(f"[warn][!] An unexpected error occurred: {e}[/warn]")

def main():
    """Main application loop."""
    try:
        while True:
            clear_screen()
            print_logo()
            print_description()
            main_menu()
            
            choices = [str(i+1) for i in range(len(TOOLS))]
            choice = Prompt.ask(
                "\n[option]Select an option[/option]", 
                choices=choices, 
                show_choices=False
            )
            
            try:
                run_tool(int(choice)-1)
            except (ValueError, IndexError):
                console.print("[warn]Invalid selection.[/warn]")
            
            again = Prompt.ask("\n[option]Back to menu? (y/n)[/option]", choices=["y", "n"], default="y")
            if again == "n":
                console.print("[desc]Goodbye![/desc]")
                break
                
    except KeyboardInterrupt:
        console.print("\n[desc]Exiting ZeroDay...[/desc]")
        sys.exit(0)

if __name__ == "__main__":
    main()
