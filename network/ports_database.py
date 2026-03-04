"""
Port Database - Common services and protocols
Contains well-known port numbers with descriptions
"""

PORTS_DATABASE = {
    "web": {
        "name": "Web Services",
        "description": "Common web and HTTP services",
        "ports": [
            {"port": 80, "service": "HTTP", "description": "HyperText Transfer Protocol - unencrypted web traffic"},
            {"port": 443, "service": "HTTPS", "description": "HyperText Transfer Protocol Secure - encrypted web traffic"},
            {"port": 8080, "service": "HTTP-ALT", "description": "Alternative HTTP port, commonly used by proxies and web servers"},
            {"port": 8443, "service": "HTTPS-ALT", "description": "Alternative HTTPS port"},
            {"port": 3000, "service": "Node.js", "description": "Common Node.js development server port"},
            {"port": 5000, "service": "Flask/Python", "description": "Common Python development server port"},
            {"port": 9000, "service": "SonarQube", "description": "Code quality and analysis platform"},
        ]
    },
    
    "ssh": {
        "name": "SSH & Remote Access",
        "description": "Secure shell and remote access protocols",
        "ports": [
            {"port": 22, "service": "SSH", "description": "Secure Shell - encrypted remote command execution and terminal"},
            {"port": 23, "service": "Telnet", "description": "Telnet - unencrypted remote terminal (deprecated)"},
            {"port": 3389, "service": "RDP", "description": "Remote Desktop Protocol - Windows remote desktop"},
            {"port": 5900, "service": "VNC", "description": "Virtual Network Computing - remote desktop sharing"},
        ]
    },
    
    "database": {
        "name": "Databases",
        "description": "Database server and management ports",
        "ports": [
            {"port": 3306, "service": "MySQL", "description": "MySQL relational database server"},
            {"port": 5432, "service": "PostgreSQL", "description": "PostgreSQL advanced relational database"},
            {"port": 1433, "service": "MSSQL", "description": "Microsoft SQL Server database"},
            {"port": 1521, "service": "Oracle", "description": "Oracle Database server"},
            {"port": 27017, "service": "MongoDB", "description": "MongoDB NoSQL document database"},
            {"port": 6379, "service": "Redis", "description": "Redis in-memory data store"},
            {"port": 5984, "service": "CouchDB", "description": "Apache CouchDB NoSQL database"},
        ]
    },
    
    "mail": {
        "name": "Mail Services",
        "description": "Email and mail server protocols",
        "ports": [
            {"port": 25, "service": "SMTP", "description": "Simple Mail Transfer Protocol - email transmission"},
            {"port": 110, "service": "POP3", "description": "Post Office Protocol v3 - email retrieval"},
            {"port": 143, "service": "IMAP", "description": "Internet Message Access Protocol - email access"},
            {"port": 587, "service": "SMTP-TLS", "description": "SMTP with STARTTLS encryption"},
            {"port": 993, "service": "IMAPS", "description": "IMAP with SSL/TLS encryption"},
            {"port": 995, "service": "POP3S", "description": "POP3 with SSL/TLS encryption"},
        ]
    },
    
    "dns": {
        "name": "DNS Services",
        "description": "Domain Name System services",
        "ports": [
            {"port": 53, "service": "DNS", "description": "Domain Name System - hostname to IP resolution"},
        ]
    },
    
    "directory": {
        "name": "Directory Services",
        "description": "Directory and authentication services",
        "ports": [
            {"port": 389, "service": "LDAP", "description": "Lightweight Directory Access Protocol - user directory"},
            {"port": 636, "service": "LDAPS", "description": "LDAP with SSL/TLS encryption"},
            {"port": 88, "service": "Kerberos", "description": "Network authentication protocol"},
            {"port": 445, "service": "SMB", "description": "Server Message Block - Windows file sharing"},
            {"port": 139, "service": "NetBIOS", "description": "NetBIOS Session Service - Windows networking"},
        ]
    },
    
    "monitoring": {
        "name": "Monitoring & Management",
        "description": "System monitoring and network management",
        "ports": [
            {"port": 161, "service": "SNMP", "description": "Simple Network Management Protocol - device monitoring"},
            {"port": 162, "service": "SNMP-Trap", "description": "SNMP Trap - event notifications"},
            {"port": 51413, "service": "Transmission", "description": "Transmission BitTorrent client web interface"},
            {"port": 19999, "service": "Netdata", "description": "Netdata real-time performance monitoring"},
        ]
    },
    
    "ntp": {
        "name": "Time Services",
        "description": "Network time synchronization",
        "ports": [
            {"port": 123, "service": "NTP", "description": "Network Time Protocol - time synchronization"},
        ]
    },
    
    "vpn": {
        "name": "VPN Services",
        "description": "Virtual Private Network protocols",
        "ports": [
            {"port": 500, "service": "IKE", "description": "Internet Key Exchange - VPN key negotiation"},
            {"port": 1194, "service": "OpenVPN", "description": "OpenVPN - open-source VPN protocol"},
            {"port": 1723, "service": "PPTP", "description": "Point-to-Point Tunneling Protocol - legacy VPN"},
        ]
    },
    
    "common": {
        "name": "Top 20 Common Ports",
        "description": "Most frequently scanned ports",
        "ports": [
            {"port": 22, "service": "SSH", "description": "Secure Shell"},
            {"port": 25, "service": "SMTP", "description": "Email"},
            {"port": 53, "service": "DNS", "description": "Domain Name"},
            {"port": 80, "service": "HTTP", "description": "Web"},
            {"port": 110, "service": "POP3", "description": "Email"},
            {"port": 143, "service": "IMAP", "description": "Email"},
            {"port": 443, "service": "HTTPS", "description": "Secure Web"},
            {"port": 445, "service": "SMB", "description": "File Sharing"},
            {"port": 1433, "service": "MSSQL", "description": "Database"},
            {"port": 1521, "service": "Oracle", "description": "Database"},
            {"port": 3306, "service": "MySQL", "description": "Database"},
            {"port": 3389, "service": "RDP", "description": "Windows Remote"},
            {"port": 5432, "service": "PostgreSQL", "description": "Database"},
            {"port": 5900, "service": "VNC", "description": "Remote Desktop"},
            {"port": 8080, "service": "HTTP-ALT", "description": "Web Alt"},
            {"port": 8443, "service": "HTTPS-ALT", "description": "Web Alt"},
            {"port": 27017, "service": "MongoDB", "description": "NoSQL Database"},
            {"port": 6379, "service": "Redis", "description": "Cache/Data Store"},
            {"port": 9200, "service": "Elasticsearch", "description": "Search Engine"},
            {"port": 5000, "service": "Flask", "description": "Development"},
        ]
    },
    
    "all": {
        "name": "All Common Ports (1-10000)",
        "description": "Scan first 10000 ports for discovery",
        "ports": [
            {"port": f"{i}", "service": f"Port {i}", "description": ""} 
            for i in range(1, 10001)
        ]
    }
}


def get_preset_names():
    """Get list of available presets"""
    return list(PORTS_DATABASE.keys())


def get_preset_ports(preset_name):
    """Get ports for a specific preset"""
    if preset_name not in PORTS_DATABASE:
        return None
    return [p["port"] for p in PORTS_DATABASE[preset_name]["ports"]]


def get_preset_info(preset_name):
    """Get detailed info about a preset"""
    if preset_name not in PORTS_DATABASE:
        return None
    preset = PORTS_DATABASE[preset_name]
    return {
        "name": preset["name"],
        "description": preset["description"],
        "count": len(preset["ports"]),
        "ports": preset["ports"]
    }
