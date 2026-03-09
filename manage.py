import os
import sys
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme
from rich import box
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
        "enter_target_ip": "Enter target IP address",
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
        "enter_target_ip": "Digite o endereço IP alvo",
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
        "enter_target_ip": "Введите IP-адрес целевого хоста",
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

# Mapeie aqui os módulos. O label mostrado, caminho do script e um ícone/símbolo bonito
# "name" e "desc" agora são dicionários com chaves de idioma para facilitar a tradução
TOOLS = [
    {
        "icon": "🌐",
        "name": {"en": "Advanced Scanner", "pt": "Scanner Avançado", "ru": "Продвинутый сканер"},
        "path": "network/scanners/advancedscanner.py",
        "desc": {
            "en": "Network host discovery and port scanning",
            "pt": "Descoberta de hosts e varredura de portas de rede",
            "ru": "Обнаружение сетевых хостов и сканирование портов",
        },
    },
    {
        "icon": "🤖",
        "name": {"en": "Backdoor & Persistence", "pt": "Backdoor e Persistência", "ru": "Бэкдор и постоянство"},
        "path": "backdoor/backdoor-and-persistence.py",
        "desc": {
            "en": "Persistence & backdoor modules",
            "pt": "Módulos de persistência e backdoor",
            "ru": "Модули постоянства и бэкдора",
        },
    },
    {
        "icon": "🤖",
        "name": {
            "en": "Backdoor & Persistence Generate EXE",
            "pt": "Gerar EXE de Backdoor e Persistência",
            "ru": "Создать EXE бэкдора и постоянства",
        },
        "path": "backdoor/backdoor-and-persistence-generate-exe.py",
        "desc": {
            "en": "Persistence & backdoor modules",
            "pt": "Módulos de persistência e backdoor",
            "ru": "Модули постоянства и бэкдора",
        },
    },
    {
        "icon": "🤖",
        "name": {
            "en": "Backdoor & Persistence (listener)",
            "pt": "Backdoor e Persistência (ouvinte)",
            "ru": "Бэкдор и постоянство (слушатель)",
        },
        "path": "backdoor/listener.py",
        "desc": {
            "en": "Persistence & backdoor server modules",
            "pt": "Módulos de servidor de persistência e backdoor",
            "ru": "Серверные модули постоянства и бэкдора",
        },
    },
    {
        "icon": "📡",
        "name": {"en": "AICrack Wireless Attack", "pt": "AICrack Ataque Wireless", "ru": "AICrack беспроводная атака"},
        "path": "network/attack/wireless/aicrack.py",
        "desc": {
            "en": "Automated wireless (WPA deauth) attacks",
            "pt": "Ataques wireless automatizados (desautenticação WPA)",
            "ru": "Автоматическая беспроводная атака (деаутентификация WPA)",
        },
    },
    {
        "icon": "🔥",
        "name": {"en": "SYN Flood Attack", "pt": "Ataque SYN Flood", "ru": "SYN флуд атака"},
        "path": "network/attack/flags/sf.py",
        "desc": {
            "en": "SYN flood network attack (requires target IP)",
            "pt": "Ataque de inundação SYN (requer IP alvo)",
            "ru": "Сетевая атака SYN флуд (требуется IP цели)",
        },
    },
    {
        "icon": "🌐",
        "name": {"en": "BGP Attack", "pt": "Ataque BGP", "ru": "BGP атака"},
        "path": "network/BGP/simple-bgp-attack.py",
        "desc": {
            "en": "BGP routing attack",
            "pt": "Ataque de roteamento BGP",
            "ru": "Атака на маршрутизацию BGP",
        },
    },
    {
        "icon": "🔓",
        "name": {"en": "Hasher Utility", "pt": "Utilitário de Hash", "ru": "Утилита хэширования"},
        "path": "utils/hasher.py",
        "desc": {
            "en": "Hash generation and verification utility",
            "pt": "Utilitário de geração e verificação de hash",
            "ru": "Утилита генерации и проверки хэша",
        },
    },
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
                ("ICMP Scan on Web Preset", "python manage.py -H 192.168.1.100 -x web -M icmp"),
                ("ICMP Scan on Specific Ports", "python manage.py -H 192.168.1.100 -p 80,443,8080 -M icmp"),
                ("ICMP Scan on Port Range", "python manage.py -H 192.168.1.100 -r 1-100 -M icmp"),
                ("ICMP Scan on Database Preset", "python manage.py -H 192.168.1.50 -x database -M icmp"),
                ("TCP Connect Scan (Default)", "python manage.py -H 192.168.1.100 -x web"),
                ("SYN Stealth Scan (Requires Admin)", "python manage.py -H 192.168.1.100 -x database -M syn"),
                ("UDP Scan for Services", "python manage.py -H 192.168.1.100 -p 53,161,123 -M udp"),
                ("FIN Stealth Scan (Requires Admin)", "python manage.py -H 192.168.1.100 -x web -M fin"),
                ("Interactive Mode", "python manage.py -i"),
                ("Show All Presets", "python manage.py --list"),
            ],
            "note": "⚠️  ICMP/SYN/FIN scans require Admin (Windows) or Root (Linux) privileges",
        },
        "pt": {
            "title": "Exemplos de Uso do Scanner ICMP/TCP",
            "examples": [
                ("Scan ICMP em Preset Web", "python manage.py -H 192.168.1.100 -x web -M icmp"),
                ("Scan ICMP em Portas Específicas", "python manage.py -H 192.168.1.100 -p 80,443,8080 -M icmp"),
                ("Scan ICMP em Range de Portas", "python manage.py -H 192.168.1.100 -r 1-100 -M icmp"),
                ("Scan ICMP em Preset de Database", "python manage.py -H 192.168.1.50 -x database -M icmp"),
                ("Scan TCP Connect (Padrão)", "python manage.py -H 192.168.1.100 -x web"),
                ("Scan SYN Stealth (Requer Admin)", "python manage.py -H 192.168.1.100 -x database -M syn"),
                ("Scan UDP para Serviços", "python manage.py -H 192.168.1.100 -p 53,161,123 -M udp"),
                ("Scan FIN Stealth (Requer Admin)", "python manage.py -H 192.168.1.100 -x web -M fin"),
                ("Modo Interativo", "python manage.py -i"),
                ("Mostrar Todos os Presets", "python manage.py --list"),
            ],
            "note": "⚠️  Scans ICMP/SYN/FIN requerem privilégios de Admin (Windows) ou Root (Linux)",
        },
        "ru": {
            "title": "Примеры использования сканера ICMP/TCP",
            "examples": [
                ("Сканирование ICMP в Web Preset", "python manage.py -H 192.168.1.100 -x web -M icmp"),
                ("Сканирование ICMP на конкретные порты", "python manage.py -H 192.168.1.100 -p 80,443,8080 -M icmp"),
                ("Сканирование ICMP на диапазон портов", "python manage.py -H 192.168.1.100 -r 1-100 -M icmp"),
                ("Сканирование ICMP в Database Preset", "python manage.py -H 192.168.1.50 -x database -M icmp"),
                ("TCP Connect Scan (По умолчанию)", "python manage.py -H 192.168.1.100 -x web"),
                ("SYN Stealth Scan (Требует Admin)", "python manage.py -H 192.168.1.100 -x database -M syn"),
                ("UDP Scan для служб", "python manage.py -H 192.168.1.100 -p 53,161,123 -M udp"),
                ("FIN Stealth Scan (Требует Admin)", "python manage.py -H 192.168.1.100 -x web -M fin"),
                ("Интерактивный режим", "python manage.py -i"),
                ("Показать все presets", "python manage.py --list"),
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

def main_menu(strings, lang):
    table = Table(title=strings['available_modules'], box=box.DOUBLE_EDGE, title_style="bold magenta")
    table.add_column(strings['option'], style="option", justify="center")
    table.add_column(strings['module'], style="option")
    table.add_column(strings['description'], style="desc")
    for idx, tool in enumerate(TOOLS, 1):
        # resolve localized name/description
        name = tool['name'].get(lang, tool['name'].get('en', '')) if isinstance(tool['name'], dict) else tool['name']
        desc = tool['desc'].get(lang, tool['desc'].get('en', '')) if isinstance(tool['desc'], dict) else tool['desc']
        table.add_row(
            f"[bold blue]{tool['icon']} {idx}[/bold blue]",
            f"[bold]{name}[/bold]",
            desc
        )
    # Add Examples option
    table.add_row(
        f"[bold blue]📚 {len(TOOLS) + 1}[/bold blue]",
        f"[bold]{strings['examples']}[/bold]",
        strings.get('examples_desc', strings.get('examples_desc', 'Scanner ICMP/TCP/UDP usage examples'))
    )
    console.print(table)

def run_tool(index, pre_args="", strings=None, lang='en'):
    if strings is None:
        strings = LANGUAGES['en']
    
    tool = TOOLS[index]
    tool_path = SCRIPTS_PATH / tool["path"]
    if not tool_path.exists():
        console.print(f"[warn][!] Module not found: {tool_path}[/warn]")
        return
    
    # Special handling for Backdoor - requires IP and port input
    if "backdoor-and-persistence.py" in tool["path"] and not pre_args:
        console.print("\n[cyan]╔══════════════════════════════════════════╗[/cyan]")
        console.print("[cyan]║  Backdoor Configuration                 ║[/cyan]")
        console.print("[cyan]╚══════════════════════════════════════════╝[/cyan]\n")
        target_ip = Prompt.ask("[option]Enter listener IP address", default="auto")
        target_port = Prompt.ask("[option]Enter listener port", default="4444")
        pre_args = f"-i {target_ip} -p {target_port}"
    
    # Special handling for SYN Flood Attack - requires target IP input
    elif "syn-flood" in tool["path"] and not pre_args:
        target_ip = Prompt.ask(f"[option]{strings.get('enter_target_ip', 'Enter target IP address')}")
        pre_args = target_ip
    
    # --- Load modules ---
    spec = importlib.util.spec_from_file_location("module", tool_path)
    module = importlib.util.module_from_spec(spec)
    # Add the tool's directory to path for imports
    tool_dir = str(tool_path.parent)
    sys.path.insert(0, tool_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        if tool_dir in sys.path:
            sys.path.remove(tool_dir)

    # resolve localized name for display
    name = tool['name'].get(lang, tool['name'].get('en', '') ) if isinstance(tool['name'], dict) else tool['name']

    # Skip argument prompt for specific tools that don't need manual input
    skip_arg_prompt = (
        "backdoor-and-persistence-generate-exe.py" in tool["path"] or
        "listener.py" in tool["path"]
    )

    # --- Has get_args? ---
    if hasattr(module, "get_args") and not skip_arg_prompt:
        args_info = module.get_args()

        # Show nice tables
        title = f"{strings['arguments_for']} {name}"
        table = Table(title=title, box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("Flag", style="cyan", justify="center")
        table.add_column("Description", style="yellow")

        for arg in args_info:
            table.add_row(arg["flag"], arg["desc"])

        console.print(table)
    elif not skip_arg_prompt:
        args_info = []
        console.print(f"[desc]{strings['no_args']}\n")

    # --- Answer args ---
    if pre_args:
        args = pre_args
    elif skip_arg_prompt:
        args = ""  # No arguments needed for these tools
    else:
        prompt_text = f"[option]{strings['enter_arguments']}"
        args = Prompt.ask(prompt_text, default="")

    launching_text = f"[desc]{strings['launching']} [b]{name}[/b]...\n"
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
        main_menu(strings, lang)
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
                detected_lang = lang
                show_examples(strings, detected_lang)
                Prompt.ask(f"\n[option]{strings['press_enter']}", default="")
                continue
            elif 0 <= choice_idx < len(TOOLS):
                run_tool(choice_idx, pre_args, strings, lang)
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
