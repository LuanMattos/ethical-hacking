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
import argparse

console = Console(theme=Theme({
    "title": "bold magenta",
    "option": "bold cyan",
    "desc": "italic dim yellow",
    "warn": "bold red"
}))

# Language dictionary
LANGUAGES = {
    "en": {
        "welcome": "Welcome to [b]ZeroDay[/b], a hacking tool for all possible scenarios.",
        "tools_list": "Here you'll find scanners, network attacks like ARP spoofing, wireless attacks, persistence, and much more.",
        "instagram": "Follow me on Instagram:",
        "github": "GitHub:",
        "warning": "This tool is for serious cybersecurity professionals only. Practicing unethical hacking is a crime!",
        "available_modules": "Available Modules",
        "option": "Option",
        "module": "Module",
        "description": "Description",
        "select_option": "Select an option (or option + arguments)",
        "back_to_menu": "Back to menu? (y/n)",
        "goodbye": "Goodbye!",
        "invalid_option": "Invalid option number.",
        "arguments_for": "Arguments for",
        "no_args": "This module does not provide argument info.",
        "enter_arguments": "Enter arguments (or leave empty)",
        "launching": "Launching",
        "examples": "Usage Examples",
        "examples_desc": "Scanner ICMP/TCP/UDP usage examples",
        "icmp_examples": "ICMP Scanner Examples",
        "press_enter": "Press Enter to continue...",
    },
    "pt": {
        "welcome": "Bem-vindo ao [b]ZeroDay[/b], uma ferramenta de hacking para todos os cenários possíveis.",
        "tools_list": "Aqui você encontrará scanners, ataques de rede como ARP spoofing, ataques wireless, persistência e muito mais.",
        "instagram": "Me siga no Instagram:",
        "github": "GitHub:",
        "warning": "Esta ferramenta é apenas para profissionais sérios de segurança cibernética. Praticar hacking antiético é crime!",
        "available_modules": "Módulos Disponíveis",
        "option": "Opção",
        "module": "Módulo",
        "description": "Descrição",
        "select_option": "Selecione uma opção (ou opção + argumentos)",
        "back_to_menu": "Voltar ao menu? (s/n)",
        "goodbye": "Até logo!",
        "invalid_option": "Número de opção inválido.",
        "arguments_for": "Argumentos para",
        "no_args": "Este módulo não fornece informações de argumentos.",
        "enter_arguments": "Digite argumentos (ou deixe em branco)",
        "launching": "Iniciando",
        "examples": "Exemplos de Uso",
        "examples_desc": "Exemplos de uso do Scanner ICMP/TCP/UDP",
        "icmp_examples": "Exemplos do Scanner ICMP",
        "press_enter": "Pressione Enter para continuar...",
    },
    "ru": {
        "welcome": "Добро пожаловать в [b]ZeroDay[/b], инструмент для взлома для всех возможных сценариев.",
        "tools_list": "Здесь вы найдете сканеры, сетевые атаки, такие как ARP spoofing, атаки на беспроводные сети, настойчивость и многое другого.",
        "instagram": "Следите за мной в Instagram:",
        "github": "GitHub:",
        "warning": "Этот инструмент предназначен только для серьезных специалистов по кибербезопасности. Практика неэтичного взлома - это преступление!",
        "available_modules": "Доступные модули",
        "option": "Опция",
        "module": "Модуль",
        "description": "Описание",
        "select_option": "Выберите опцию (или опцию + аргументы)",
        "back_to_menu": "Вернуться в меню? (д/н)",
        "goodbye": "До свидания!",
        "invalid_option": "Неверный номер опции.",
        "arguments_for": "Аргументы для",
        "no_args": "Этот модуль не предоставляет информацию об аргументах.",
        "enter_arguments": "Введите аргументы (или оставьте пусто)",
        "launching": "Запуск",
        "examples": "Примеры использования",
        "examples_desc": "Примеры использования сканера ICMP/TCP/UDP",
        "icmp_examples": "Примеры сканера ICMP",
        "press_enter": "Нажмите Enter для продолжения...",
    }
}

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
    {"icon": "🌐", "name": "Advanced Scanner",                  "path": "advancedscanner.py", "desc": "Network host discovery and port scanning"},
    {"icon": "🤖", "name": "Backdoor & Persistence",            "path": "backdoor/backdoor-and-persistence.py","desc": "Persistence & backdoor modules"},
    {"icon": "🤖", "name": "Backdoor & Persistence Generate EXE ", "path": "backdoor/backdoor-and-persistence-generate-exe.py","desc": "Persistence & backdoor modules"},
    {"icon": "🤖", "name": "Backdoor & Persistence (listener)", "path": "backdoor/listener.py","desc": "Persistence & backdoor server modules"},
    {"icon": "🔑", "name": "BruteSH",                           "path": "brutesh/main.py", "desc": "SSH brute force attack tool"},
    {"icon": "🔒", "name": "CryptForce",                        "path": "cryptforce/main.py", "desc": "Password/password hash cracking"},
    {"icon": "🔎", "name": "Network Scanners",                  "path": "scanner/scanner_line_filter.py","desc": "Live packet capture and filtering"},
    {"icon": "📡", "name": "AICrack Wireless Attack",           "path": "aicrack.py", "desc": "Automated wireless (WPA deauth) attacks"},
    # Adicione mais conforme for expandindo...
]

def print_logo():
    console.print(Panel.fit(ASCII_LOGO, style="title", padding=1, width=75, border_style="magenta"))

def print_description(strings):
    description_text = f"""
[desc]{strings['welcome']}
{strings['tools_list']}

[desc]{strings['instagram']} [b cyan]@zero_s_day[/b cyan]
[desc]{strings['github']} [cyan]https://github.com/LuanMattos/[/cyan]

[desc]⚠️ [warn]{strings['warning']}[/warn]
"""
    console.print(description_text, highlight=True)

def show_examples(strings, lang="en"):
    """Show ICMP and other scanner usage examples"""
    examples = {
        "en": {
            "title": "ICMP/TCP Scanner Usage Examples",
            "examples": [
                ("ICMP Scan on Web Preset", "python advancedscanner.py -H 192.168.1.100 -x web -M icmp"),
                ("ICMP Scan on Specific Ports", "python advancedscanner.py -H 192.168.1.100 -p 80,443,8080 -M icmp"),
                ("ICMP Scan on Port Range", "python advancedscanner.py -H 192.168.1.100 -r 1-100 -M icmp"),
                ("ICMP Scan on Database Preset", "python advancedscanner.py -H 192.168.1.50 -x database -M icmp"),
                ("TCP Connect Scan (Default)", "python advancedscanner.py -H 192.168.1.100 -x web"),
                ("SYN Stealth Scan (Requires Admin)", "python advancedscanner.py -H 192.168.1.100 -x database -M syn"),
                ("UDP Scan for Services", "python advancedscanner.py -H 192.168.1.100 -p 53,161,123 -M udp"),
                ("FIN Stealth Scan (Requires Admin)", "python advancedscanner.py -H 192.168.1.100 -x web -M fin"),
                ("Interactive Mode", "python advancedscanner.py -i"),
                ("Show All Presets", "python advancedscanner.py --list"),
            ],
            "note": "⚠️  ICMP/SYN/FIN scans require Admin (Windows) or Root (Linux) privileges",
        },
        "pt": {
            "title": "Exemplos de Uso do Scanner ICMP/TCP",
            "examples": [
                ("Scan ICMP em Preset Web", "python advancedscanner.py -H 192.168.1.100 -x web -M icmp"),
                ("Scan ICMP em Portas Específicas", "python advancedscanner.py -H 192.168.1.100 -p 80,443,8080 -M icmp"),
                ("Scan ICMP em Range de Portas", "python advancedscanner.py -H 192.168.1.100 -r 1-100 -M icmp"),
                ("Scan ICMP em Preset de Database", "python advancedscanner.py -H 192.168.1.50 -x database -M icmp"),
                ("Scan TCP Connect (Padrão)", "python advancedscanner.py -H 192.168.1.100 -x web"),
                ("Scan SYN Stealth (Requer Admin)", "python advancedscanner.py -H 192.168.1.100 -x database -M syn"),
                ("Scan UDP para Serviços", "python advancedscanner.py -H 192.168.1.100 -p 53,161,123 -M udp"),
                ("Scan FIN Stealth (Requer Admin)", "python advancedscanner.py -H 192.168.1.100 -x web -M fin"),
                ("Modo Interativo", "python advancedscanner.py -i"),
                ("Mostrar Todos os Presets", "python advancedscanner.py --list"),
            ],
            "note": "⚠️  Scans ICMP/SYN/FIN requerem privilégios de Admin (Windows) ou Root (Linux)",
        },
        "ru": {
            "title": "Примеры использования сканера ICMP/TCP",
            "examples": [
                ("Сканирование ICMP в Web Preset", "python advancedscanner.py -H 192.168.1.100 -x web -M icmp"),
                ("Сканирование ICMP на конкретные порты", "python advancedscanner.py -H 192.168.1.100 -p 80,443,8080 -M icmp"),
                ("Сканирование ICMP на диапазон портов", "python advancedscanner.py -H 192.168.1.100 -r 1-100 -M icmp"),
                ("Сканирование ICMP в Database Preset", "python advancedscanner.py -H 192.168.1.50 -x database -M icmp"),
                ("TCP Connect Scan (По умолчанию)", "python advancedscanner.py -H 192.168.1.100 -x web"),
                ("SYN Stealth Scan (Требует Admin)", "python advancedscanner.py -H 192.168.1.100 -x database -M syn"),
                ("UDP Scan для служб", "python advancedscanner.py -H 192.168.1.100 -p 53,161,123 -M udp"),
                ("FIN Stealth Scan (Требует Admin)", "python advancedscanner.py -H 192.168.1.100 -x web -M fin"),
                ("Интерактивный режим", "python advancedscanner.py -i"),
                ("Показать все presets", "python advancedscanner.py --list"),
            ],
            "note": "⚠️  Сканы ICMP/SYN/FIN требуют привилегий Admin (Windows) или Root (Linux)",
        },
    }
    
    example_data = examples.get(lang, examples["en"])
    
    console.print(f"\n[bold magenta]{example_data['title']}[/bold magenta]\n")
    
    table = Table(box=box.ROUNDED, title_style="bold cyan")
    table.add_column("Example", style="cyan")
    table.add_column("Command", style="yellow")
    
    for example_name, command in example_data["examples"]:
        table.add_row(example_name, f"[code]{command}[/code]")
    
    console.print(table)
    console.print(f"\n[warn]{example_data['note']}[/warn]\n")

def main_menu(strings):
    table = Table(title=strings['available_modules'], box=box.DOUBLE_EDGE, title_style="bold magenta")
    table.add_column(strings['option'], style="option", justify="center")
    table.add_column(strings['module'], style="option")
    table.add_column(strings['description'], style="desc")
    for idx, tool in enumerate(TOOLS, 1):
        table.add_row(
            f"[bold blue]{tool['icon']} {idx}[/bold blue]",
            f"[bold]{tool['name']}[/bold]",
            tool['desc']
        )
    # Add Examples option
    table.add_row(
        f"[bold blue]📚 {len(TOOLS) + 1}[/bold blue]",
        f"[bold]{strings['examples']}[/bold]",
        strings.get('examples_desc', 'Scanner ICMP/TCP/UDP usage examples')
    )
    console.print(table)

def run_tool(index, pre_args="", strings=None):
    if strings is None:
        strings = LANGUAGES['en']
    
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
        title = f"{strings['arguments_for']} {tool['name']}"
        table = Table(title=title, box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("Flag", style="cyan", justify="center")
        table.add_column("Description", style="yellow")

        for arg in args_info:
            table.add_row(arg["flag"], arg["desc"])

        console.print(table)
    else:
        args_info = []
        console.print(f"[desc]{strings['no_args']}\n")

    # --- Answer args ---
    if pre_args:
        args = pre_args
    else:
        prompt_text = f"[option]{strings['enter_arguments']}"
        args = Prompt.ask(prompt_text, default="")

    launching_text = f"[desc]{strings['launching']} [b]{tool['name']}[/b]...\n"
    console.print(launching_text)

    import subprocess
    cmd = [sys.executable, str(tool_path)] + args.split()
    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(
        description='ZeroDay - Comprehensive Hacking & Security Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--lang', dest='language', type=str, default='en',
                        choices=['en', 'pt', 'ru'],
                        help='Language: en (English), pt (Português), ru (Русский) - default: en')
    
    args = parser.parse_args()
    lang = args.language if args.language in LANGUAGES else 'en'
    strings = LANGUAGES[lang]
    
    print_logo()
    print_description(strings)
    
    while True:
        main_menu(strings)
        prompt_text = f"\n[option]{strings['select_option']}"
        user_input = Prompt.ask(prompt_text, default="1")
        
        # Parse input: first token is choice, rest are args
        tokens = user_input.strip().split()
        if not tokens:
            choice = "1"
            pre_args = ""
        else:
            choice = tokens[0]
            pre_args = " ".join(tokens[1:])
        
        try:
            choice_idx = int(choice) - 1
            if choice_idx == len(TOOLS):  # Examples option
                # Detect language from strings
                detected_lang = "en"
                if "iniciando" in strings.get("launching", "").lower():
                    detected_lang = "pt"
                elif "запуск" in strings.get("launching", "").lower():
                    detected_lang = "ru"
                show_examples(strings, detected_lang)
                Prompt.ask(f"\n[option]{strings['press_enter']}", default="")
                continue
            elif 0 <= choice_idx < len(TOOLS):
                run_tool(choice_idx, pre_args, strings)
            else:
                console.print(f"[warn]{strings['invalid_option']}[/warn]")
                continue
        except ValueError:
            console.print("[warn]Please enter a valid option number.[/warn]")
            continue
        
        back_prompt = f"[option]{strings['back_to_menu']}"
        again = Prompt.ask(back_prompt, choices=["y", "n"], default="y")
        if again == "n":
            console.print(f"[desc]{strings['goodbye']}[/desc]")
            break

if __name__ == "__main__":
    main()