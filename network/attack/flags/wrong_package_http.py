import argparse
import socket

from scapy.all import IP, TCP, send


IPV4_GUIDE = {
    "en": {
        "title": "IPv4 Header Fields",
        "diagram": """
┌─────────────────────────────────────────────────────┐
│                    IPv4 Header                      │
├─────────────────────────────────────────────────────┤
│ Version │ IHL │ DSCP/ECN │       Total Length       │
├─────────────────────────────────────────────────────┤
│       Identification       │ Flags │ Fragment Offset │
├─────────────────────────────────────────────────────┤
│ TTL │ Protocol │          Header Checksum            │
├─────────────────────────────────────────────────────┤
│              Source IP Address                      │
├─────────────────────────────────────────────────────┤
│           Destination IP Address                    │
├─────────────────────────────────────────────────────┤
│              Options (optional)                     │
└─────────────────────────────────────────────────────┘
                         ↓
                    Payload
""",
        "fields": [
            ("Version", "IPv4 version field (usually 4)."),
            ("IHL", "Header length in 32-bit words."),
            ("DSCP/ECN", "Traffic class and congestion information."),
            ("Total Length", "Total packet size, including header and payload."),
            ("Identification", "Identifies fragments of the same original packet."),
            ("Flags", "Controls fragmentation behavior."),
            ("Fragment Offset", "Offset of this fragment within the original packet."),
            ("TTL", "Time To Live; decremented by each router."),
            ("Protocol", "Next-layer protocol such as TCP (6) or UDP (17)."),
            ("Header Checksum", "Checks the integrity of the IPv4 header."),
            ("Source IP", "Origin IP address."),
            ("Destination IP", "Target IP address."),
            ("Options", "Optional fields used for advanced routing or security features."),
            ("Payload", "Actual data carried in the packet, for example an HTTP request."),
        ],
    },
    "pt": {
        "title": "Campos do Cabeçalho IPv4",
        "diagram": """
┌─────────────────────────────────────────────────────┐
│                 Cabeçalho IPv4                     │
├─────────────────────────────────────────────────────┤
│ Version │ IHL │ DSCP/ECN │    Comprimento Total    │
├─────────────────────────────────────────────────────┤
│     Identificação      │ Flags │ Offset do Fragmento │
├─────────────────────────────────────────────────────┤
│ TTL │ Protocolo │      Checksum do Cabeçalho       │
├─────────────────────────────────────────────────────┤
│            IP de Origem                             │
├─────────────────────────────────────────────────────┤
│          IP de Destino                              │
├─────────────────────────────────────────────────────┤
│          Opções (opcional)                         │
└─────────────────────────────────────────────────────┘
                         ↓
                    Payload
""",
        "fields": [
            ("Version", "Campo da versão IPv4 (normalmente 4)."),
            ("IHL", "Comprimento do cabeçalho em palavras de 32 bits."),
            ("DSCP/ECN", "Classe de tráfego e informações de congestionamento."),
            ("Total Length", "Tamanho total do pacote, incluindo cabeçalho e payload."),
            ("Identification", "Identifica fragmentos do mesmo pacote original."),
            ("Flags", "Controla o comportamento de fragmentação."),
            ("Fragment Offset", "Posição deste fragmento no pacote original."),
            ("TTL", "Tempo de vida; decrementado em cada roteador."),
            ("Protocol", "Protocolo da camada superior, como TCP (6) ou UDP (17)."),
            ("Header Checksum", "Valida a integridade do cabeçalho IPv4."),
            ("Source IP", "Endereço IP de origem."),
            ("Destination IP", "Endereço IP de destino."),
            ("Options", "Campos opcionais para roteamento ou segurança avançada."),
            ("Payload", "Dados reais transportados, por exemplo uma requisição HTTP."),
        ],
    },
    "ru": {
        "title": "Поля заголовка IPv4",
        "diagram": """
┌─────────────────────────────────────────────────────┐
│                 Заголовок IPv4                     │
├─────────────────────────────────────────────────────┤
│ Version │ IHL │ DSCP/ECN │    Total Length         │
├─────────────────────────────────────────────────────┤
│    Identification    │ Flags │ Fragment Offset     │
├─────────────────────────────────────────────────────┤
│ TTL │ Protocol │         Header Checksum           │
├─────────────────────────────────────────────────────┤
│           Source IP Address                        │
├─────────────────────────────────────────────────────┤
│         Destination IP Address                     │
├─────────────────────────────────────────────────────┤
│           Options (необязательно)                  │
└─────────────────────────────────────────────────────┘
                         ↓
                    Payload
""",
        "fields": [
            ("Version", "Поле версии IPv4 (обычно 4)."),
            ("IHL", "Длина заголовка в словах по 32 бита."),
            ("DSCP/ECN", "Класс трафика и информация о перегрузке."),
            ("Total Length", "Полный размер пакета, включая заголовок и полезную нагрузку."),
            ("Identification", "Идентификатор фрагментов одного исходного пакета."),
            ("Flags", "Управляет фрагментацией."),
            ("Fragment Offset", "Смещение фрагмента внутри исходного пакета."),
            ("TTL", "Time To Live; уменьшается на каждом маршрутизаторе."),
            ("Protocol", "Протокол следующего уровня, например TCP (6) или UDP (17)."),
            ("Header Checksum", "Проверяет целостность заголовка IPv4."),
            ("Source IP", "IP-адрес источника."),
            ("Destination IP", "IP-адрес назначения."),
            ("Options", "Дополнительные поля для маршрутизации и безопасности."),
            ("Payload", "Содержимое пакета, например HTTP-запрос."),
        ],
    },
}


def get_args():
    return [
        {"flag": "url", "desc": "URL ou host alvo (posicional)"},
        {"flag": "-s, --src", "desc": "IP de origem do pacote (default: 192.168.1.10)"},
        {"flag": "-p, --port", "desc": "Porta de destino (default: 80)"},
        {"flag": "--sport", "desc": "Porta de origem (default: 12345)"},
        {"flag": "-H, --host", "desc": "Valor do cabeçalho Host (default: localhost)"},
        {"flag": "-m, --method", "desc": "Método HTTP (default: GET)"},
        {"flag": "-P, --path", "desc": "Path da requisição HTTP (default: /)"},
        {"flag": "-V, --version", "desc": "Versão HTTP (default: HTTP/1.1)"},
        {"flag": "-n, --count", "desc": "Quantidade de envios (default: 1)"},
        {"flag": "--lang", "desc": "Idioma da documentação IPv4 (en, pt, ru)"},
    ]


def print_ipv4_guide(lang: str = "en") -> None:
    data = IPV4_GUIDE.get(lang, IPV4_GUIDE["en"])
    print(f"\n{'=' * 78}")
    print(f"{data['title']:^78}")
    print(f"{'=' * 78}")
    print(data["diagram"])
    print("\nCampos principais:")
    for name, desc in data["fields"]:
        print(f"  - {name}: {desc}")
    print(f"{'=' * 78}\n")


def build_http_request(
    host: str = "localhost",
    path: str = "/",
    method: str = "GET",
    version: str = "HTTP/1.1",
    extra_headers: str = "",
) -> bytes:
    headers = (
        f"{method} {path} {version}\r\n"
        f"Host: {host}\r\n"
        "User-Agent: WrongPackageHTTP/1.0\r\n"
        "Connection: close\r\n"
    )
    if extra_headers:
        headers += f"{extra_headers}\r\n"
    headers += "\r\n"
    return headers.encode("utf-8")


def build_malformed_http_packet(
    target_ip: str,
    src_ip: str = "192.168.1.10",
    port: int = 80,
    sport: int = 12345,
    host: str = "localhost",
    path: str = "/",
    method: str = "GET",
    version: str = "HTTP/1.1",
    extra_headers: str = "",
) -> IP:
    http_payload = build_http_request(host, path, method, version, extra_headers)
    return IP(dst=target_ip, src=src_ip) / TCP(
        sport=sport,
        dport=port,
        seq=1,
        ack=0,
        flags="PA",
        window=64240,
    ) / http_payload


def print_server_response(response: bytes, lang: str = "en") -> None:
    text = response.decode("utf-8", errors="replace").strip()
    title = {
        "en": "SERVER RESPONSE",
        "pt": "RESPOSTA DO SERVIDOR",
        "ru": "ОТВЕТ СЕРВЕРА",
    }.get(lang, "SERVER RESPONSE")
    empty = {
        "en": "No response received from the server.",
        "pt": "Nenhuma resposta recebida do servidor.",
        "ru": "Ответ от сервера не получен.",
    }.get(lang, "No response received from the server.")

    print("\n" + "=" * 70)
    print(f"{title:^70}")
    print("=" * 70)
    if text:
        print(text)
    else:
        print(f"[!] {empty}")
    print("=" * 70)


def send_and_capture_response(
    target_ip: str,
    port: int = 80,
    src_ip: str = "192.168.1.10",
    sport: int = 12345,
    host: str = "localhost",
    path: str = "/",
    method: str = "GET",
    version: str = "HTTP/1.1",
    extra_headers: str = "",
    lang: str = "en",
) -> bytes:
    request = build_http_request(host, path, method, version, extra_headers)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        try:
            if src_ip:
                sock.bind((src_ip, sport))
        except OSError:
            bind_msg = {
                "en": "Could not bind to",
                "pt": "Não foi possível vincular a",
                "ru": "Не удалось привязать",
            }.get(lang, "Could not bind to")
            print(f"[!] {bind_msg} {src_ip}:{sport}; using automatic port.")
        try:
            sock.connect((target_ip, port))
            sock.sendall(request)

            chunks = []
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                    chunks.append(data)
                except socket.timeout:
                    break
        except OSError as exc:
            print(f"[!] Connection error: {exc}")
            return b""

    response = b"".join(chunks)
    print_server_response(response, lang)
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description="Simula um pacote HTTP sobre TCP com Scapy")
    parser.add_argument("url", help="URL ou host alvo")
    parser.add_argument("-s", "--src", type=str, default="192.168.1.10", help="IP de origem do pacote")
    parser.add_argument("-p", "--port", type=int, default=80, help="Porta de destino")
    parser.add_argument("--sport", type=int, default=12345, help="Porta de origem")
    parser.add_argument("-H", "--host", type=str, default="localhost", help="Valor do cabeçalho Host")
    parser.add_argument("-m", "--method", type=str, default="GET", help="Método HTTP")
    parser.add_argument("-P", "--path", type=str, default="/", help="Path da requisição HTTP")
    parser.add_argument("-V", "--version", type=str, default="HTTP/1.1", help="Versão HTTP")
    parser.add_argument("--extra-headers", type=str, default="", help="Cabeçalhos extras em formato 'Header: value'")
    parser.add_argument("-n", "--count", type=int, default=1, help="Quantidade de envios a serem feitos")
    parser.add_argument("--lang", choices=["en", "pt", "ru"], default="en", help="Idioma da documentação IPv4")
    args = parser.parse_args()

    print_ipv4_guide(args.lang)

    ip = socket.gethostbyname(args.url)

    print(f"[*] URL: {args.url}")
    print(f"[*] IP resolvido: {ip}")
    print(f"[*] Origem: {args.src}:{args.sport}")
    print(f"[*] Destino: {ip}:{args.port}")
    print(f"[*] Total de envios: {args.count}")

    for i in range(1, args.count + 1):
        packet = build_malformed_http_packet(
            target_ip=ip,
            src_ip=args.src,
            port=args.port,
            sport=args.sport,
            host=args.host,
            path=args.path,
            method=args.method,
            version=args.version,
            extra_headers=args.extra_headers,
        )

        print(f"\n[*] Envio {i}/{args.count} ...")
        send(packet, verbose=0)
        print(f"[+] Pacote HTTP {i}/{args.count} enviado com sucesso")

        print("[*] Capturando resposta do servidor...")
        send_and_capture_response(
            target_ip=ip,
            port=args.port,
            src_ip=args.src,
            sport=args.sport,
            host=args.host,
            path=args.path,
            method=args.method,
            version=args.version,
            extra_headers=args.extra_headers,
            lang=args.lang,
        )


if __name__ == "__main__":
    main()
