"""Learning Network — interactive protocol catalogue & animated packet demos.

This is the *second session* launched from ZeroDay's main menu ("Learning
Network"). It lists every protocol category requested, lets the user pick a
protocol, and plays an animated terminal "demo" of how that protocol behaves.

Real packets are crafted with Scapy where a suitable layer exists and can be
sent after an explicit confirmation. For protocols with no meaningful software-only demo
(physical media standards, cellular/Wi-Fi PHY, Bluetooth radio, etc.) a short
conceptual animated explanation is generated instead.
"""
import sys
import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.theme import Theme
from rich import box

sys.path.insert(0, str(Path(__file__).parent))
from data import all_categories          # noqa: E402
from animator import run_flow            # noqa: E402
from scapy_demos import get_demo_steps, BUILDERS, maybe_send  # noqa: E402
from explain import show_source_info     # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LANGUAGE_CACHE = Path.home() / ".zeroday_learning_network_cache.json"

console = Console(theme=Theme({
    "title": "bold magenta",
    "option": "bold cyan",
    "desc": "italic dim yellow",
    "warn": "bold red",
}))

STRINGS = {
    "en": {
        "header": "Learning Network — protocol catalogue with animated demos",
        "sub": "Pick a category, then a protocol, and watch a simulated packet flow.",
        "categories": "Categories",
        "protocols": "Protocols",
        "col_option": "#",
        "col_name": "Name",
        "col_desc": "Description",
        "select_category": "Select a category number (0 to exit)",
        "select_protocol": "Select a protocol number (0 to go back)",
        "invalid": "Invalid option.",
        "press_enter": "Press Enter to continue...",
        "send_packet": "Send this packet to the network?",
        "goodbye": "Goodbye!",
        "back": "back",
    },
    "pt": {
        "header": "Learning Network — catálogo de protocolos com demos animadas",
        "sub": "Escolha uma categoria, depois um protocolo, e veja o fluxo de pacotes simulado.",
        "categories": "Categorias",
        "protocols": "Protocolos",
        "col_option": "#",
        "col_name": "Nome",
        "col_desc": "Descrição",
        "select_category": "Selecione o número da categoria (0 para sair)",
        "select_protocol": "Selecione o número do protocolo (0 para voltar)",
        "invalid": "Opção inválida.",
        "press_enter": "Pressione Enter para continuar...",
        "send_packet": "Enviar este pacote para a rede?",
        "goodbye": "Até logo!",
        "back": "voltar",
    },
    "ru": {
        "header": "Learning Network — каталог протоколов с анимированными демонстрациями",
        "sub": "Выберите категорию, затем протокол, и посмотрите симуляцию потока пакетов.",
        "categories": "Категории",
        "protocols": "Протоколы",
        "col_option": "#",
        "col_name": "Имя",
        "col_desc": "Описание",
        "select_category": "Выберите номер категории (0 для выхода)",
        "select_protocol": "Выберите номер протокола (0 назад)",
        "invalid": "Неверный вариант.",
        "press_enter": "Нажмите Enter для продолжения...",
        "send_packet": "Отправить этот пакет в сеть?",
        "goodbye": "До свидания!",
        "back": "назад",
    },
}


def conceptual_steps(entry, lang):
    """Generic 3-step animated explanation for protocols without a Scapy demo."""
    name = entry["name"]
    desc = entry["desc"].get(lang, entry["desc"].get("en", ""))
    layer = entry.get("layer", "")
    overview = {
        "en": f"{name}: {desc}",
        "pt": f"{name}: {desc}",
        "ru": f"{name}: {desc}",
    }.get(lang)
    step1 = {
        "en": f"{name} typically requires dedicated hardware/software support ({layer or 'see category'})",
        "pt": f"{name} geralmente requer suporte dedicado de hardware/software ({layer or 'ver categoria'})",
        "ru": f"{name} обычно требует специальной поддержки оборудования/ПО",
    }.get(lang)
    step2 = {
        "en": f"Simulated unit of {name} traffic exchanged between two peers",
        "pt": f"Unidade simulada de tráfego {name} trocada entre dois pares",
        "ru": f"Смоделированная единица трафика {name} между узлами",
    }.get(lang)
    return [
        {"label": overview, "direction": "info", "wireshark_filter": "frame"},
        {"label": step1, "direction": "info", "wireshark_filter": "frame"},
        {"label": step2, "direction": "send", "packet_summary": f"{name} PDU",
         "wireshark_filter": "frame"},
    ]


def run_demo(entry, lang):
    steps = None
    builder_key = entry.get("builder")
    if builder_key:
        steps = get_demo_steps(builder_key)
    if not steps:
        steps = conceptual_steps(entry, lang)
        builder_key = None
    run_flow(console, entry["name"], steps)

    for step in steps:
        packet = step.get("packet")
        if packet is not None and step.get("direction") == "send":
            maybe_send(
                console,
                packet,
                lambda: Confirm.ask(STRINGS[lang]["send_packet"], default=True),
            )

    if builder_key and builder_key in BUILDERS:
        show_source_info(console, BUILDERS[builder_key], PROJECT_ROOT, lang, kind="scapy")
    else:
        show_source_info(console, conceptual_steps, PROJECT_ROOT, lang, kind="conceptual",
                          protocol_name=entry["name"])


def show_categories(lang):
    strings = STRINGS[lang]
    table = Table(title=strings["categories"], box=box.DOUBLE_EDGE, title_style="bold magenta")
    table.add_column(strings["col_option"], style="option", justify="center")
    table.add_column(strings["col_name"], style="bold")
    categories = all_categories()
    for idx, cat in enumerate(categories, 1):
        title = cat["title"].get(lang, cat["title"]["en"])
        table.add_row(str(idx), title)
    console.print(table)
    return categories


def show_protocols(category, lang):
    strings = STRINGS[lang]
    title = category["title"].get(lang, category["title"]["en"])
    table = Table(title=f"{title} — {strings['protocols']}", box=box.ROUNDED, title_style="bold cyan")
    table.add_column(strings["col_option"], style="option", justify="center")
    table.add_column(strings["col_name"], style="bold")
    table.add_column(strings["col_desc"], style="desc")
    protocols = category["protocols"]
    for idx, proto in enumerate(protocols, 1):
        desc = proto["desc"].get(lang, proto["desc"].get("en", ""))
        marker = " [scapy]" if proto.get("builder") else ""
        table.add_row(str(idx), f"{proto['name']}{marker}", desc)
    console.print(table)
    return protocols


def load_language_cache():
    try:
        with LANGUAGE_CACHE.open("r", encoding="utf-8") as cache_file:
            language = json.load(cache_file).get("language")
        return language if language in STRINGS else None
    except (OSError, ValueError, TypeError):
        return None


def save_language_cache(language):
    try:
        with LANGUAGE_CACHE.open("w", encoding="utf-8") as cache_file:
            json.dump({"language": language}, cache_file, ensure_ascii=True, indent=2)
            cache_file.write("\n")
    except OSError:
        pass


def main():
    parser = argparse.ArgumentParser(description="Learning Network — protocol demos")
    parser.add_argument("--lang", dest="language", type=str, default=None,
                         choices=["en", "pt", "ru"], help="Language: en, pt, ru")
    args = parser.parse_args()
    cached_language = load_language_cache()
    if args.language in STRINGS:
        lang = args.language
    else:
        lang = Prompt.ask(
            "Select language / Selecione o idioma / Выберите язык",
            choices=list(STRINGS),
            default=cached_language or "en",
        )
    save_language_cache(lang)
    strings = STRINGS[lang]

    console.print(Panel.fit(f"[bold cyan]{strings['header']}[/bold cyan]\n[desc]{strings['sub']}[/desc]",
                             box=box.ROUNDED, border_style="magenta"))

    while True:
        categories = show_categories(lang)
        choice = Prompt.ask(f"\n[option]{strings['select_category']}", default="0")
        try:
            idx = int(choice)
        except ValueError:
            console.print(f"[warn]{strings['invalid']}[/warn]")
            continue
        if idx == 0:
            console.print(f"[desc]{strings['goodbye']}[/desc]")
            break
        if not (1 <= idx <= len(categories)):
            console.print(f"[warn]{strings['invalid']}[/warn]")
            continue

        category = categories[idx - 1]
        while True:
            protocols = show_protocols(category, lang)
            choice = Prompt.ask(f"\n[option]{strings['select_protocol']}", default="0")
            try:
                pidx = int(choice)
            except ValueError:
                console.print(f"[warn]{strings['invalid']}[/warn]")
                continue
            if pidx == 0:
                break
            if not (1 <= pidx <= len(protocols)):
                console.print(f"[warn]{strings['invalid']}[/warn]")
                continue

            entry = protocols[pidx - 1]
            run_demo(entry, lang)
            Prompt.ask(f"[option]{strings['press_enter']}", default="")


if __name__ == "__main__":
    main()
