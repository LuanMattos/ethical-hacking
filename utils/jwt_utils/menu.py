"""Utils — JWT Decode / Build interactive submenu.

Decode JWT: paste a token, inspect header/payload (no signature verification),
and cache the result. Build JWT: sign a new token; if a decoded JWT is cached,
offers to edit it field-by-field (old value shown as default) before signing.
"""
import sys
import json
import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.theme import Theme
from rich import box

sys.path.insert(0, str(Path(__file__).parent))
from jwt_core import decode_jwt, sign_jwt, ALGORITHMS  # noqa: E402

CACHE_PATH = Path.home() / ".zeroday_jwt_cache.json"

console = Console(theme=Theme({
    "title": "bold magenta",
    "option": "bold cyan",
    "desc": "italic dim yellow",
    "warn": "bold red",
}))

STRINGS = {
    "en": {
        "header": "Utils — JWT Decode / Build",
        "sub": "Decode a JWT to inspect it, or build/sign a new one.",
        "select_option": "Select an option (0 to exit)",
        "opt_decode": "Decode JWT",
        "opt_build": "Build JWT",
        "back": "Back",
        "invalid": "Invalid option.",
        "press_enter": "Press Enter to continue...",
        "enter_token": "Paste the JWT token",
        "decode_error": "Could not decode token",
        "header_title": "Header",
        "payload_title": "Payload",
        "signature_label": "Signature (base64url, not verified)",
        "cached_ok": "Saved to session cache for use in 'Build JWT'.",
        "update_prompt": "A JWT is cached from a previous decode. Update it and generate a new one with modified fields?",
        "editing_section": "Editing {section} fields (press Enter to keep the current value)",
        "fresh_build": "Building a new JWT from scratch.",
        "header_json_prompt": "Header (JSON)",
        "payload_json_prompt": "Payload (JSON)",
        "json_error": "Invalid JSON",
        "algorithm_prompt": f"Algorithm ({'/'.join(list(ALGORITHMS) + ['none'])})",
        "secret_prompt": "Signing secret (blank for 'none' algorithm)",
        "build_error": "Could not build token",
        "new_token_title": "New JWT",
    },
    "pt": {
        "header": "Utils — Decodificar / Criar JWT",
        "sub": "Decodifique um JWT para inspecioná-lo, ou crie/assine um novo.",
        "select_option": "Selecione uma opção (0 para sair)",
        "opt_decode": "Decodificar JWT",
        "opt_build": "Criar JWT",
        "back": "Voltar",
        "invalid": "Opção inválida.",
        "press_enter": "Pressione Enter para continuar...",
        "enter_token": "Cole o token JWT",
        "decode_error": "Não foi possível decodificar o token",
        "header_title": "Header",
        "payload_title": "Payload",
        "signature_label": "Assinatura (base64url, não verificada)",
        "cached_ok": "Salvo no cache da sessão para uso em 'Criar JWT'.",
        "update_prompt": "Há um JWT salvo em cache de uma decodificação anterior. Deseja atualizá-lo e gerar um novo com os campos modificados?",
        "editing_section": "Editando os campos de {section} (pressione Enter para manter o valor atual)",
        "fresh_build": "Criando um novo JWT do zero.",
        "header_json_prompt": "Header (JSON)",
        "payload_json_prompt": "Payload (JSON)",
        "json_error": "JSON inválido",
        "algorithm_prompt": f"Algoritmo ({'/'.join(list(ALGORITHMS) + ['none'])})",
        "secret_prompt": "Segredo de assinatura (em branco para algoritmo 'none')",
        "build_error": "Não foi possível criar o token",
        "new_token_title": "Novo JWT",
    },
    "ru": {
        "header": "Utils — Декодирование / Создание JWT",
        "sub": "Декодируйте JWT для проверки или создайте/подпишите новый.",
        "select_option": "Выберите опцию (0 для выхода)",
        "opt_decode": "Декодировать JWT",
        "opt_build": "Создать JWT",
        "back": "Назад",
        "invalid": "Неверный вариант.",
        "press_enter": "Нажмите Enter для продолжения...",
        "enter_token": "Вставьте JWT токен",
        "decode_error": "Не удалось декодировать токен",
        "header_title": "Header",
        "payload_title": "Payload",
        "signature_label": "Подпись (base64url, не проверяется)",
        "cached_ok": "Сохранено в кэше сессии для использования в 'Создать JWT'.",
        "update_prompt": "В кэше есть JWT из предыдущего декодирования. Обновить его и создать новый с изменёнными полями?",
        "editing_section": "Редактирование полей {section} (нажмите Enter, чтобы оставить текущее значение)",
        "fresh_build": "Создание нового JWT с нуля.",
        "header_json_prompt": "Header (JSON)",
        "payload_json_prompt": "Payload (JSON)",
        "json_error": "Неверный JSON",
        "algorithm_prompt": f"Алгоритм ({'/'.join(list(ALGORITHMS) + ['none'])})",
        "secret_prompt": "Секрет для подписи (пусто для алгоритма 'none')",
        "build_error": "Не удалось создать токен",
        "new_token_title": "Новый JWT",
    },
}


def load_cache():
    try:
        with CACHE_PATH.open("r", encoding="utf-8") as cache_file:
            data = json.load(cache_file)
        if isinstance(data, dict) and "header" in data and "payload" in data:
            return data
    except (OSError, ValueError):
        pass
    return None


def save_cache(header, payload, algorithm, token):
    try:
        with CACHE_PATH.open("w", encoding="utf-8") as cache_file:
            json.dump(
                {"header": header, "payload": payload, "algorithm": algorithm, "token": token},
                cache_file, indent=2,
            )
            cache_file.write("\n")
    except OSError:
        pass


def render_claims_table(title, claims):
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan")
    table.add_column("Field", style="option")
    table.add_column("Value", style="desc")
    for key, value in claims.items():
        display = value if isinstance(value, str) else json.dumps(value)
        table.add_row(key, display)
    console.print(table)


def decode_flow(lang):
    strings = STRINGS[lang]
    token = Prompt.ask(f"[option]{strings['enter_token']}")
    try:
        header, payload, signature = decode_jwt(token)
    except Exception as exc:
        console.print(f"[warn]{strings['decode_error']}: {exc}[/warn]")
        return

    render_claims_table(strings["header_title"], header)
    render_claims_table(strings["payload_title"], payload)
    console.print(f"[desc]{strings['signature_label']}:[/desc] {signature or '(none)'}")

    algorithm = str(header.get("alg", "HS256"))
    save_cache(header, payload, algorithm, token)
    console.print(f"[desc]{strings['cached_ok']}[/desc]")


def parse_value(new_str, old_value):
    old_str = old_value if isinstance(old_value, str) else json.dumps(old_value)
    if new_str == old_str:
        return old_value
    try:
        return json.loads(new_str)
    except ValueError:
        return new_str


def prompt_fields(fields, strings, section_label):
    console.print(f"[option]{strings['editing_section'].format(section=section_label)}[/option]")
    result = {}
    for key, old_value in fields.items():
        default_str = old_value if isinstance(old_value, str) else json.dumps(old_value)
        new_str = Prompt.ask(f"  {key}", default=default_str)
        result[key] = parse_value(new_str, old_value)
    return result


def build_flow(lang):
    strings = STRINGS[lang]
    cache = load_cache()
    header = None
    payload = None
    algorithm = "HS256"

    if cache and Confirm.ask(f"[option]{strings['update_prompt']}", default=True):
        header = prompt_fields(cache["header"], strings, strings["header_title"])
        payload = prompt_fields(cache["payload"], strings, strings["payload_title"])
        algorithm = cache.get("algorithm", "HS256")

    if header is None:
        console.print(f"[desc]{strings['fresh_build']}[/desc]")
        header_json = Prompt.ask(
            f"[option]{strings['header_json_prompt']}",
            default=json.dumps({"alg": "HS256", "typ": "JWT"}),
        )
        payload_json = Prompt.ask(f"[option]{strings['payload_json_prompt']}", default=json.dumps({}))
        try:
            header = json.loads(header_json)
            payload = json.loads(payload_json)
        except ValueError as exc:
            console.print(f"[warn]{strings['json_error']}: {exc}[/warn]")
            return
        algorithm = header.get("alg", "HS256")

    algorithm = Prompt.ask(f"[option]{strings['algorithm_prompt']}", default=str(algorithm))
    secret = Prompt.ask(f"[option]{strings['secret_prompt']}", default="", password=True)

    try:
        token = sign_jwt(header, payload, secret, algorithm)
    except Exception as exc:
        console.print(f"[warn]{strings['build_error']}: {exc}[/warn]")
        return

    console.print(Panel.fit(token, title=strings["new_token_title"], border_style="green"))
    save_cache(header, payload, algorithm, token)
    console.print(f"[desc]{strings['cached_ok']}[/desc]")


def main():
    parser = argparse.ArgumentParser(description="Utils — JWT decode/build")
    parser.add_argument("--lang", dest="language", type=str, default="en",
                         choices=["en", "pt", "ru"], help="Language: en, pt, ru")
    args = parser.parse_args()
    lang = args.language if args.language in STRINGS else "en"
    strings = STRINGS[lang]

    console.print(Panel.fit(f"[bold cyan]{strings['header']}[/bold cyan]\n[desc]{strings['sub']}[/desc]",
                             box=box.ROUNDED, border_style="magenta"))

    while True:
        table = Table(box=box.DOUBLE_EDGE, title_style="bold magenta")
        table.add_column("#", style="option", justify="center")
        table.add_column("Option", style="bold")
        table.add_row("1", strings["opt_decode"])
        table.add_row("2", strings["opt_build"])
        table.add_row("0", strings["back"])
        console.print(table)

        choice = Prompt.ask(f"\n[option]{strings['select_option']}", default="0")
        if choice == "0":
            break
        elif choice == "1":
            decode_flow(lang)
        elif choice == "2":
            build_flow(lang)
        else:
            console.print(f"[warn]{strings['invalid']}[/warn]")
            continue
        Prompt.ask(f"[option]{strings['press_enter']}", default="")


if __name__ == "__main__":
    main()
