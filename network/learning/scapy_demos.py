"""Scapy-backed packet builders used by the Learning Network demos.

Each function returns a list of "step" dicts consumed by animator.run_flow:
    {"label": str, "detail": str|None, "direction": "send"|"recv"|"info", "packet_summary": str|None}

Packets are *built* with Scapy (to produce a real, inspectable representation)
but are NEVER sent on the wire unless the user explicitly opts-in via
maybe_send(). This keeps the "Learning Network" module safe to run without
root/admin privileges and without generating unwanted traffic.
"""

try:
    from scapy.all import (
        Ether, ARP, Dot1Q, IP, IPv6, ICMP, ICMPv6EchoRequest, ICMPv6EchoReply,
        TCP, UDP, DNS, DNSQR, DNSRR, BOOTP, DHCP, IGMP, GRE, conf,
    )
    SCAPY_OK = True
except Exception:
    SCAPY_OK = False

try:
    from scapy.layers.vxlan import VXLAN
except Exception:
    VXLAN = None

try:
    from scapy.layers.l2 import STP
except Exception:
    STP = None

try:
    from scapy.contrib.lldp import LLDPDU, LLDPDUChassisID, LLDPDUPortID, LLDPDUTimeToLive, LLDPDUEndOfLLDPDU
except Exception:
    LLDPDU = None

try:
    from scapy.layers.ppp import PPPoE, PPPoED
except Exception:
    PPPoE = None

try:
    from scapy.layers.eap import EAPOL, EAP
except Exception:
    EAPOL = None

try:
    from scapy.contrib.bgp import BGPHeader, BGPOpen
except Exception:
    BGPHeader = None

try:
    from scapy.contrib.ospf import OSPF_Hdr, OSPF_Hello
except Exception:
    OSPF_Hdr = None

try:
    from scapy.contrib.mpls import MPLS
except Exception:
    MPLS = None

try:
    from scapy.contrib.gtp import GTP_U_Header
except Exception:
    GTP_U_Header = None

try:
    from scapy.layers.ntp import NTP
except Exception:
    NTP = None

try:
    from scapy.layers.snmp import SNMP, SNMPget, SNMPvarbind
except Exception:
    SNMP = None

try:
    from scapy.contrib.radius import RADIUS
except Exception:
    RADIUS = None


def maybe_send(console, pkt, prompt_fn):
    """Ask the user (via prompt_fn -> bool) whether to really send `pkt`.
    Only used for demos where sending is harmless (local scope). Off by default.
    """
    if pkt is None:
        return
    try:
        if prompt_fn():
            from scapy.all import send
            send(pkt, verbose=False)
            console.print("[bold red]>> Packet actually sent on the wire.[/bold red]")
    except Exception as exc:
        console.print(f"[warn]Send failed (likely needs admin/root): {exc}[/warn]")


# ---------------------------------------------------------------------------
# L2 — Ethernet / ARP / VLAN / STP / LLDP / PPPoE / EAPOL
# ---------------------------------------------------------------------------

def demo_ethernet_arp():
    steps = []
    if not SCAPY_OK:
        return _fallback("Ethernet + ARP")
    who_has = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="192.168.1.1", psrc="192.168.1.50")
    is_at = Ether(src="aa:bb:cc:dd:ee:ff") / ARP(op=2, hwsrc="aa:bb:cc:dd:ee:ff", psrc="192.168.1.1", pdst="192.168.1.50")
    steps.append({"label": "Host builds an Ethernet frame carrying an ARP request",
                  "direction": "info", "detail": "Ethernet (L2) frames wrap every packet on a LAN segment."})
    steps.append({"label": "Broadcast ARP 'Who has 192.168.1.1?'", "direction": "send",
                  "packet_summary": who_has.summary()})
    steps.append({"label": "Router replies 'I am at aa:bb:cc:dd:ee:ff'", "direction": "recv",
                  "packet_summary": is_at.summary()})
    return steps


def demo_vlan():
    if not SCAPY_OK:
        return _fallback("802.1Q VLAN tagging")
    pkt = Ether() / Dot1Q(vlan=100) / IP(dst="10.0.0.5") / TCP(dport=80, flags="S")
    return [
        {"label": "Switch tags the frame with VLAN ID 100 (802.1Q)", "direction": "info",
         "detail": "A 4-byte tag is inserted between the Ethernet header and the payload."},
        {"label": "Tagged frame forwarded on the trunk link", "direction": "send",
         "packet_summary": pkt.summary()},
    ]


def demo_stp():
    if not SCAPY_OK or STP is None:
        return _fallback("Spanning Tree Protocol (STP/RSTP/MSTP)")
    pkt = Ether(dst="01:80:c2:00:00:00") / STP(rootid=1, bridgeid=1, pathcost=0)
    return [
        {"label": "Bridge broadcasts a BPDU to elect the root bridge", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "Other switches compare bridge IDs and block redundant links", "direction": "info",
         "detail": "Prevents Layer 2 loops in switched networks."},
    ]


def demo_lldp():
    if not SCAPY_OK or LLDPDU is None:
        return _fallback("LLDP / CDP neighbor discovery")
    pkt = (Ether(dst="01:80:c2:00:00:0e") / LLDPDUChassisID(subtype=4, id=b"\xaa\xbb\xcc\xdd\xee\xff")
           / LLDPDUPortID(subtype=2, id=b"Gi0/1") / LLDPDUTimeToLive(ttl=120) / LLDPDUEndOfLLDPDU())
    return [
        {"label": "Switch multicasts an LLDP frame announcing itself", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "Neighboring device stores chassis/port info in its neighbor table",
         "direction": "info", "detail": "Used for topology discovery (LLDP is vendor-neutral, CDP is Cisco's variant)."},
    ]


def demo_pppoe():
    if not SCAPY_OK or PPPoE is None:
        return _fallback("PPP / PPPoE")
    pkt = Ether() / PPPoED(code=0x09)
    return [
        {"label": "Client broadcasts PADI (PPPoE Active Discovery Initiation)", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "Access Concentrator replies PADO, session negotiated (PADR/PADS)", "direction": "recv"},
        {"label": "PPP LCP/NCP negotiate the link, then IP traffic flows inside PPPoE",
         "direction": "info"},
    ]


def demo_eapol():
    if not SCAPY_OK or EAPOL is None:
        return _fallback("802.1X / EAP / EAPOL")
    pkt = Ether(dst="01:80:c2:00:00:03") / EAPOL(version=2, type=1)
    return [
        {"label": "Supplicant sends EAPOL-Start to the authenticator (switch/AP)", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "Authenticator requests identity (EAP-Request/Identity)", "direction": "recv"},
        {"label": "Credentials validated against a RADIUS server, port unblocked", "direction": "info"},
    ]


# ---------------------------------------------------------------------------
# L3 — IPv4 / IPv6 / ICMP / IGMP
# ---------------------------------------------------------------------------

def demo_ipv4_icmp_ping():
    if not SCAPY_OK:
        return _fallback("IPv4 + ICMP (ping)")
    req = IP(dst="8.8.8.8") / ICMP(type=8, id=1, seq=1)
    reply = IP(src="8.8.8.8") / ICMP(type=0, id=1, seq=1)
    return [
        {"label": "Build an ICMP Echo Request wrapped in an IPv4 packet", "direction": "info"},
        {"label": "Send Echo Request (ping)", "direction": "send", "packet_summary": req.summary()},
        {"label": "Receive Echo Reply", "direction": "recv", "packet_summary": reply.summary()},
    ]


def demo_ipv6_icmpv6():
    if not SCAPY_OK:
        return _fallback("IPv6 + ICMPv6")
    req = IPv6(dst="2001:4860:4860::8888") / ICMPv6EchoRequest()
    reply = IPv6(src="2001:4860:4860::8888") / ICMPv6EchoReply()
    return [
        {"label": "IPv6 uses ICMPv6 for ping, and also NDP (neighbor discovery)", "direction": "info"},
        {"label": "Send ICMPv6 Echo Request", "direction": "send", "packet_summary": req.summary()},
        {"label": "Receive ICMPv6 Echo Reply", "direction": "recv", "packet_summary": reply.summary()},
    ]


def demo_igmp():
    if not SCAPY_OK:
        return _fallback("IGMP (multicast group membership)")
    pkt = IP(dst="224.0.0.1") / IGMP(type=0x11)
    return [
        {"label": "Router sends an IGMP Membership Query to 224.0.0.1", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "Hosts interested in a multicast group send an IGMP Report", "direction": "recv"},
    ]


def demo_traceroute():
    if not SCAPY_OK:
        return _fallback("traceroute (TTL exceeded)")
    steps = [{"label": "Traceroute sends packets with increasing TTL", "direction": "info"}]
    for ttl in (1, 2, 3):
        pkt = IP(dst="8.8.8.8", ttl=ttl) / ICMP()
        steps.append({"label": f"TTL={ttl} expires at hop {ttl}", "direction": "send",
                      "packet_summary": pkt.summary()})
        steps.append({"label": f"Hop {ttl} replies 'Time Exceeded' (ICMP type 11)", "direction": "recv"})
    return steps


# ---------------------------------------------------------------------------
# L4 — TCP / UDP handshake style demos
# ---------------------------------------------------------------------------

def demo_tcp_handshake():
    if not SCAPY_OK:
        return _fallback("TCP 3-way handshake")
    syn = IP(dst="93.184.216.34") / TCP(sport=51000, dport=80, flags="S", seq=1000)
    synack = IP(src="93.184.216.34") / TCP(sport=80, dport=51000, flags="SA", seq=5000, ack=1001)
    ack = IP(dst="93.184.216.34") / TCP(sport=51000, dport=80, flags="A", seq=1001, ack=5001)
    fin = IP(dst="93.184.216.34") / TCP(sport=51000, dport=80, flags="FA", seq=1001, ack=5001)
    return [
        {"label": "Client -> Server: SYN (open connection)", "direction": "send", "packet_summary": syn.summary()},
        {"label": "Server -> Client: SYN-ACK", "direction": "recv", "packet_summary": synack.summary()},
        {"label": "Client -> Server: ACK (connection established)", "direction": "send", "packet_summary": ack.summary()},
        {"label": "Data can now flow reliably, in order, with congestion control", "direction": "info"},
        {"label": "Client -> Server: FIN (graceful close)", "direction": "send", "packet_summary": fin.summary()},
    ]


def demo_udp_dns():
    if not SCAPY_OK:
        return _fallback("UDP + DNS query")
    query = IP(dst="8.8.8.8") / UDP(sport=33445, dport=53) / DNS(rd=1, qd=DNSQR(qname="example.com"))
    answer = IP(src="8.8.8.8") / UDP(sport=53, dport=33445) / DNS(qr=1, an=DNSRR(rrname="example.com", rdata="93.184.216.34"))
    return [
        {"label": "UDP is connectionless: no handshake, just send", "direction": "info"},
        {"label": "Client asks 'A record for example.com?'", "direction": "send", "packet_summary": query.summary()},
        {"label": "DNS server answers with the IP address", "direction": "recv", "packet_summary": answer.summary()},
    ]


def demo_dhcp():
    if not SCAPY_OK:
        return _fallback("DHCP DORA flow")
    discover = (Ether(dst="ff:ff:ff:ff:ff:ff") / IP(src="0.0.0.0", dst="255.255.255.255")
                / UDP(sport=68, dport=67) / BOOTP(chaddr=b"\xaa\xbb\xcc\xdd\xee\xff") / DHCP(options=[("message-type", "discover"), "end"]))
    offer = DHCP(options=[("message-type", "offer"), "end"])
    request = DHCP(options=[("message-type", "request"), "end"])
    ack = DHCP(options=[("message-type", "ack"), "end"])
    return [
        {"label": "DISCOVER: client broadcasts looking for a DHCP server", "direction": "send",
         "packet_summary": discover.summary()},
        {"label": "OFFER: server proposes an IP lease", "direction": "recv", "packet_summary": offer.summary()},
        {"label": "REQUEST: client formally requests that lease", "direction": "send", "packet_summary": request.summary()},
        {"label": "ACK: server confirms, client configures its interface", "direction": "recv", "packet_summary": ack.summary()},
    ]


# ---------------------------------------------------------------------------
# Tunneling / routing / misc protocols with native Scapy layers
# ---------------------------------------------------------------------------

def demo_gre():
    if not SCAPY_OK:
        return _fallback("GRE tunneling")
    pkt = IP(dst="203.0.113.1") / GRE() / IP(dst="10.10.10.10") / ICMP()
    return [
        {"label": "Original packet is encapsulated inside a GRE header + new IP header",
         "direction": "info"},
        {"label": "Tunnel endpoint forwards the encapsulated packet", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "Remote endpoint decapsulates and delivers the inner packet", "direction": "recv"},
    ]


def demo_vxlan():
    if VXLAN is None or not SCAPY_OK:
        return _fallback("VXLAN overlay networking")
    inner = Ether(dst="aa:bb:cc:00:00:01") / IP(dst="10.1.1.5") / ICMP()
    pkt = Ether() / IP(dst="192.0.2.10") / UDP(dport=4789) / VXLAN(vni=100) / inner
    return [
        {"label": "Original Ethernet frame is wrapped: VXLAN header + UDP + outer IP", "direction": "info",
         "detail": "VNI 100 identifies the virtual L2 segment across the underlay network."},
        {"label": "VTEP sends the encapsulated frame over UDP/4789", "direction": "send",
         "packet_summary": pkt.summary()},
    ]


def demo_mpls():
    if MPLS is None or not SCAPY_OK:
        return _fallback("MPLS label switching")
    pkt = Ether() / MPLS(label=1000, ttl=64) / IP(dst="198.51.100.1")
    return [
        {"label": "Label Edge Router pushes an MPLS label instead of a full IP lookup", "direction": "info"},
        {"label": "Labeled packet forwarded hop-by-hop using label swapping", "direction": "send",
         "packet_summary": pkt.summary()},
    ]


def demo_bgp():
    if BGPHeader is None or not SCAPY_OK:
        return _fallback("BGP-4 peering")
    pkt = IP(dst="198.51.100.1") / TCP(dport=179) / BGPHeader(type=1) / BGPOpen(AS=65001, hold_time=180, bgp_id="192.0.2.1")
    return [
        {"label": "BGP peers establish a TCP session on port 179", "direction": "info"},
        {"label": "OPEN message exchanged (AS number, hold time, router ID)", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "UPDATE messages then advertise/withdraw routes between Autonomous Systems", "direction": "info"},
    ]


def demo_ospf():
    if OSPF_Hdr is None or not SCAPY_OK:
        return _fallback("OSPF Hello / adjacency")
    pkt = IP(dst="224.0.0.5", proto=89) / OSPF_Hdr() / OSPF_Hello(router=1)
    return [
        {"label": "Router multicasts a Hello packet to 224.0.0.5 (AllSPFRouters)", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "Neighbors matching Hello/Dead intervals form an adjacency and exchange the link-state database",
         "direction": "info"},
    ]


def demo_gtp():
    if GTP_U_Header is None or not SCAPY_OK:
        return _fallback("GTP (mobile core tunneling)")
    pkt = IP() / UDP(dport=2152) / GTP_U_Header() / IP(dst="10.20.30.1")
    return [
        {"label": "User plane traffic is tunneled between mobile core nodes over GTP-U/UDP 2152",
         "direction": "send", "packet_summary": pkt.summary()},
    ]


# ---------------------------------------------------------------------------
# Application layer with raw/manual construction (no dedicated scapy layer,
# or scapy layer available only for read/parsing)
# ---------------------------------------------------------------------------

def demo_http():
    if not SCAPY_OK:
        return _fallback("HTTP request/response")
    from scapy.all import Raw
    req = IP(dst="93.184.216.34") / TCP(dport=80, flags="PA") / Raw(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
    resp = IP(src="93.184.216.34") / TCP(sport=80, flags="PA") / Raw(b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n")
    return [
        {"label": "After the TCP handshake, client sends an HTTP GET request", "direction": "send",
         "packet_summary": req.summary()},
        {"label": "Server replies with a status line + headers (+ body)", "direction": "recv",
         "packet_summary": resp.summary()},
    ]


def demo_tls():
    if not SCAPY_OK:
        return _fallback("TLS handshake")
    from scapy.all import Raw
    hello = IP() / TCP(dport=443) / Raw(b"\x16\x03\x01ClientHello...")
    return [
        {"label": "TCP connects on port 443, then the TLS handshake begins", "direction": "info"},
        {"label": "ClientHello: proposes TLS version, cipher suites, SNI", "direction": "send",
         "packet_summary": hello.summary()},
        {"label": "ServerHello + Certificate + key exchange, then Finished", "direction": "recv"},
        {"label": "Symmetric session keys derived, application data now encrypted", "direction": "info"},
    ]


def demo_sip():
    if not SCAPY_OK:
        return _fallback("SIP call signaling")
    from scapy.all import Raw
    invite = IP(dst="198.51.100.20") / UDP(dport=5060) / Raw(b"INVITE sip:bob@example.com SIP/2.0")
    return [
        {"label": "Caller sends SIP INVITE to set up a call", "direction": "send", "packet_summary": invite.summary()},
        {"label": "Callee replies 180 Ringing, then 200 OK when answered", "direction": "recv"},
        {"label": "ACK confirms, then RTP media flows directly between endpoints", "direction": "info"},
    ]


def demo_rtp():
    if not SCAPY_OK:
        return _fallback("RTP media transport")
    from scapy.all import Raw
    pkt = IP() / UDP(dport=10000) / Raw(b"\x80\x00seqtimestampSSRC...")
    return [
        {"label": "Audio/video samples are packetized with sequence number + timestamp", "direction": "info"},
        {"label": "RTP packet streamed over UDP", "direction": "send", "packet_summary": pkt.summary()},
        {"label": "RTCP periodically reports jitter/loss statistics", "direction": "info"},
    ]


def demo_ntp():
    if NTP is None or not SCAPY_OK:
        return _fallback("NTP time synchronization")
    pkt = IP(dst="pool.ntp.org") / UDP(dport=123) / NTP(version=4, mode=3)
    return [
        {"label": "Client sends an NTP request (mode=client) with its transmit timestamp", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "Server replies with 4 timestamps used to compute offset and round-trip delay", "direction": "recv"},
    ]


def demo_snmp():
    if SNMP is None or not SCAPY_OK:
        return _fallback("SNMP monitoring")
    pkt = IP() / UDP(dport=161) / SNMP(community="public", PDU=SNMPget(varbindlist=[SNMPvarbind(oid="1.3.6.1.2.1.1.1.0")]))
    return [
        {"label": "Manager sends a GET request for an OID using a community string", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "Agent replies with the requested value (e.g. sysDescr)", "direction": "recv"},
    ]


def demo_radius():
    if RADIUS is None or not SCAPY_OK:
        return _fallback("RADIUS AAA")
    pkt = IP() / UDP(dport=1812) / RADIUS(code=1)
    return [
        {"label": "NAS sends Access-Request with username/password (or EAP)", "direction": "send",
         "packet_summary": pkt.summary()},
        {"label": "RADIUS server replies Access-Accept / Access-Reject", "direction": "recv"},
    ]


def demo_mqtt():
    if not SCAPY_OK:
        return _fallback("MQTT publish/subscribe")
    from scapy.all import Raw
    connect = IP() / TCP(dport=1883) / Raw(b"\x10CONNECT")
    publish = IP() / TCP(dport=1883) / Raw(b"\x30PUBLISH topic=sensor/temp")
    return [
        {"label": "Client connects to the MQTT broker", "direction": "send", "packet_summary": connect.summary()},
        {"label": "Broker forwards PUBLISH messages to subscribers of the topic", "direction": "send",
         "packet_summary": publish.summary()},
    ]


def demo_coap():
    if not SCAPY_OK:
        return _fallback("CoAP for constrained IoT devices")
    from scapy.all import Raw
    pkt = IP() / UDP(dport=5683) / Raw(b"CoAP GET /sensors/temp")
    return [
        {"label": "Lightweight REST-like request over UDP, ideal for constrained devices", "direction": "send",
         "packet_summary": pkt.summary()},
    ]


BUILDERS = {
    "ethernet_arp": demo_ethernet_arp,
    "vlan": demo_vlan,
    "stp": demo_stp,
    "lldp": demo_lldp,
    "pppoe": demo_pppoe,
    "eapol": demo_eapol,
    "ipv4_icmp": demo_ipv4_icmp_ping,
    "ipv6_icmpv6": demo_ipv6_icmpv6,
    "igmp": demo_igmp,
    "traceroute": demo_traceroute,
    "tcp_handshake": demo_tcp_handshake,
    "udp_dns": demo_udp_dns,
    "dhcp": demo_dhcp,
    "gre": demo_gre,
    "vxlan": demo_vxlan,
    "mpls": demo_mpls,
    "bgp": demo_bgp,
    "ospf": demo_ospf,
    "gtp": demo_gtp,
    "http": demo_http,
    "tls": demo_tls,
    "sip": demo_sip,
    "rtp": demo_rtp,
    "ntp": demo_ntp,
    "snmp": demo_snmp,
    "radius": demo_radius,
    "mqtt": demo_mqtt,
    "coap": demo_coap,
}


def _fallback(name):
    return [
        {"label": f"Scapy layer unavailable in this environment for {name}", "direction": "info",
         "detail": "Showing a conceptual flow instead. Try `pip install --upgrade scapy`."},
    ]


def get_demo_steps(builder_key):
    fn = BUILDERS.get(builder_key)
    if fn is None:
        return None
    try:
        return fn()
    except Exception as exc:
        return [{"label": f"Demo failed to build ({exc})", "direction": "info"}]
