import argparse
import socket

from scapy.all import IP, TCP, RandShort, send


def get_args():
	"""Return argument information for the launcher"""
	return [
		{"flag": "url", "desc": "URL ou host alvo (posicional)"},
		{"flag": "-p, --port", "desc": "Porta de destino (default: 80)"},
{"flag": "-n, --count", "desc": "Quantidade de ciclos de envio (default: 1)"},
	{"flag": "-s, --syn-per-burst", "desc": "Quantidade de SYNs enviados por ciclo (default: 2)"},
	]


def send_simple_syn(url: str, port: int = 80, count: int = 1, syn_per_burst: int = 2) -> None:
	ip = socket.gethostbyname(url)
	print(f"[*] URL: {url}")
	print(f"[*] IP resolvido: {ip}")
	print(f"[*] Enviando {syn_per_burst} SYNs por ciclo, em {count} ciclo(s)")

	for i in range(count):
		packets = [
			IP(dst=ip) / TCP(sport=RandShort(), dport=port, flags="S")
			for _ in range(syn_per_burst)
		]
		send(packets, verbose=0)
		print(f"[+] {syn_per_burst} SYN enviados no ciclo {i + 1}/{count} para {ip}:{port}")


def main() -> None:
	parser = argparse.ArgumentParser(description="Envio simples de pacote SYN com Scapy")
	parser.add_argument("url", help="URL ou host alvo (ex: example.com)")
	parser.add_argument("-p", "--port", type=int, default=80, help="Porta de destino")
	parser.add_argument("-n", "--count", type=int, default=1, help="Quantidade de ciclos de envio")
	parser.add_argument("-s", "--syn-per-burst", type=int, default=2, help="Quantidade de SYNs enviados por ciclo")
	args = parser.parse_args()

	send_simple_syn(args.url, args.port, args.count, args.syn_per_burst)


if __name__ == "__main__":
	main()
