"""
capture.py

Wrapper simples em torno de AsyncSniffer que mantém um Counter thread-safe
com os nomes das camadas/protocolos observados.
"""

from scapy.all import AsyncSniffer
from collections import Counter
import threading

# Estado compartilhado
PROTOCOL_COUNTER = Counter()
_LOCK = threading.Lock()
_SNIFFER = None

def _layer_names_from_pkt(pkt):
    """
    Extrai nomes das camadas de um pacote Scapy percorrendo a cadeia de payload.
    Retorna uma lista de nomes distintos (ordem preservada).
    """
    names = []
    current = pkt
    seen = set()
    while current:
        try:
            name = current.__class__.__name__
        except Exception:
            name = str(type(current))
        if name not in seen:
            names.append(name)
            seen.add(name)
        try:
            current = current.payload
            if current is None or current.__class__.__name__ == "NoPayload":
                break
        except Exception:
            break
    return names

def _packet_callback(pkt):
    names = _layer_names_from_pkt(pkt)
    if not names:
        return
    with _LOCK:
        for n in names:
            PROTOCOL_COUNTER[n] += 1

def start_sniff(interface=None, bpf_filter=None, store=False):
    """
    Inicia captura em background. Se já estiver rodando, não faz nada.
    interface: nome da interface (ou None)
    bpf_filter: string de filtro pcap/BPF
    store: armazenar pacotes na memória (padrão False)
    """
    global _SNIFFER
    if _SNIFFER and getattr(_SNIFFER, "running", False):
        return
    _SNIFFER = AsyncSniffer(iface=interface, filter=bpf_filter, prn=_packet_callback, store=store)
    _SNIFFER.start()

def stop_sniff():
    global _SNIFFER
    if _SNIFFER:
        try:
            _SNIFFER.stop()
        except Exception:
            pass
        _SNIFFER = None

def get_counts():
    """
    Retorna um snapshot (dict) das contagens de protocolos.
    """
    with _LOCK:
        return dict(PROTOCOL_COUNTER)

def clear_counts():
    with _LOCK:
        PROTOCOL_COUNTER.clear()