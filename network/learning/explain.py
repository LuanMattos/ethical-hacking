"""Shows where a demo's code lives (file + function), so the user can jump
straight to the Scapy builder (or the conceptual template) that produced
what they just saw.
"""
import inspect
from pathlib import Path

from rich.panel import Panel
from rich import box

STRINGS = {
    "en": {"where": "Where this demo lives", "file": "File", "function": "Function", "line": "Line",
           "kind": "Kind", "catalogue": "Catalogue entry"},
    "pt": {"where": "Onde esta demo esta definida", "file": "Arquivo", "function": "Funcao", "line": "Linha",
           "kind": "Tipo", "catalogue": "Entrada no catalogo"},
    "ru": {"where": "Где находится эта демонстрация", "file": "Файл", "function": "Функция", "line": "Строка",
           "kind": "Тип", "catalogue": "Запись в каталоге"},
}

KIND_LABELS = {
    "scapy": {"en": "Scapy packet-builder function", "pt": "Funcao construtora de pacotes Scapy",
              "ru": "Функция построения пакетов Scapy"},
    "conceptual": {"en": "Conceptual demo template function", "pt": "Funcao de template de demo conceitual",
                   "ru": "Функция шаблона концептуальной демонстрации"},
}


def catalogue_reference(protocol_name, project_root):
    """Find the line in data.py where this protocol entry is declared."""
    data_path = Path(__file__).parent / "data.py"
    try:
        lines = data_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    needle = f'P("{protocol_name}"'
    for i, line in enumerate(lines, 1):
        if needle in line:
            try:
                rel = data_path.resolve().relative_to(project_root)
            except ValueError:
                rel = data_path
            return rel, i
    return None


def _safe_print(console, renderable, plain_fallback):
    """Print a rich renderable, degrading to ASCII text on legacy consoles
    that cannot encode certain characters (e.g. accented letters on cp1252)."""
    try:
        console.print(renderable)
    except UnicodeEncodeError:
        console.print(plain_fallback.encode("ascii", "replace").decode("ascii"))


def show_source_info(console, fn, project_root, lang, kind, protocol_name=None):
    """Print the file/function location where the demo's code is defined."""
    strings = STRINGS.get(lang, STRINGS["en"])
    kind_label = KIND_LABELS.get(kind, KIND_LABELS["scapy"]).get(lang, KIND_LABELS["scapy"]["en"])

    try:
        _, start_line = inspect.getsourcelines(fn)
        filepath = Path(inspect.getsourcefile(fn)).resolve()
    except (TypeError, OSError):
        return
    try:
        rel = filepath.relative_to(project_root)
    except ValueError:
        rel = filepath

    header = (
        f"{strings['file']}: {rel}\n"
        f"{strings['function']}: {fn.__name__}()  ({strings['line']} {start_line})\n"
        f"{strings['kind']}: {kind_label}"
    )
    _safe_print(console, Panel.fit(header, title=strings["where"], border_style="green", box=box.ROUNDED), header)

    if kind == "conceptual" and protocol_name:
        ref = catalogue_reference(protocol_name, project_root)
        if ref:
            rel_path, lineno = ref
            console.print(f"[dim]{strings['catalogue']}: {rel_path}:{lineno}[/dim]")
    console.print()
