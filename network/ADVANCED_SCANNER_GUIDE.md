Advanced Scanner - Usage Guide
================================

This is a professional network port scanner with preset support, interactive mode, and visual progress tracking.

## Quick Start

### For Beginners - Use Interactive Mode
```bash
python advancedscanner.py -i
```
This opens a menu where you can:
1. Choose a preset (web, ssh, database, etc)
2. Enter your target IP/hostname
3. See results in a nice table

### Common Examples

**Scan for Web Services**
```bash
python advancedscanner.py -H 192.168.1.1 -x web
```
Scans: 80 (HTTP), 443 (HTTPS), 3000, 5000, 8080, 8443...

**Scan for Databases**
```bash
python advancedscanner.py -H 192.168.1.1 -x database
```
Scans: 3306 (MySQL), 5432 (PostgreSQL), 1433 (MSSQL), 1521 (Oracle), 27017 (MongoDB), 6379 (Redis)...

**Scan for SSH/Remote Access**
```bash
python advancedscanner.py -H 192.168.1.1 -x ssh
```
Scans: 22 (SSH), 23 (Telnet), 3389 (RDP), 5900 (VNC)

**Scan for Mail Services**
```bash
python advancedscanner.py -H 192.168.1.1 -x mail
```
Scans: 25 (SMTP), 110 (POP3), 143 (IMAP), 587, 993, 995

**Scan Top 20 Most Common Ports**
```bash
python advancedscanner.py -H 192.168.1.1 -x common
```
Quick scan of the most frequently used ports

**Full Comprehensive Scan (ports 1-10000)**
```bash
python advancedscanner.py -H 192.168.1.1 -x all
```
Warning: This will take longer as it scans 10,000 ports

## Available Presets

| Preset | Ports Scanned | Use Case |
|--------|---------------|----------|
| **web** | 8 ports | Web servers, Node.js, Flask apps |
| **ssh** | 4 ports | Remote access services |
| **database** | 7 ports | Database servers (MySQL, PostgreSQL, MongoDB, etc) |
| **mail** | 6 ports | Email services (SMTP, POP3, IMAP) |
| **dns** | 1 port | DNS servers |
| **directory** | 5 ports | LDAP, Kerberos, SMB file sharing |
| **monitoring** | 4 ports | SNMP, Netdata monitoring |
| **ntp** | 1 port | NTP time sync |
| **vpn** | 3 ports | VPN services (OpenVPN, IKE, PPTP) |
| **common** | 20 ports | Top 20 most used ports |
| **all** | 10000 ports | Comprehensive scan 1-10000 |

## Getting More Info

**List all presets with details**
```bash
python advancedscanner.py --list
```

**See detailed ports for a specific preset**
```bash
python advancedscanner.py --info web
python advancedscanner.py --info database
python advancedscanner.py --info mail
```

## Manual Port Selection

If presets don't match your needs, you can specify ports manually:

**Specific ports**
```bash
python advancedscanner.py -H 192.168.1.1 -p 80,443,22,3306
```

**Port range**
```bash
python advancedscanner.py -H 192.168.1.1 -r 1-1000
```

**Mixed ports and ranges**
```bash
python advancedscanner.py -H 192.168.1.1 -p 80,443,8080-8090,3306
```

## Understanding the Output

Once the scan completes, you'll see:
- **Colored progress bar** showing scan progress
- **Results table** listing each port and whether it's OPEN or CLOSED
- **Summary** showing total open/closed ports

### Output Example
```
[✓] 200 ports scanned
[green][+] 8 OPEN[/green]
[dim][-] 192 CLOSED[/dim]
```

## Tips & Tricks

1. **For quick vulnerability assessment**: Use `-x common` (top 20 ports)
2. **For thorough scanning**: Use `-x all` (10,000 ports)
3. **For specific services**: Use targeted presets (database, ssh, web, etc)
4. **For custom scans**: Manually specify ports with `-p` or `-r`
5. **Not sure what to do?**: Run with `-i` for interactive mode

## Examples with Different Targets

```bash
# Scan a website (external)
python advancedscanner.py -H example.com -x web

# Scan a database server
python advancedscanner.py -H db.company.local -x database

# Scan a whole subnet (just first machine for demo)
python advancedscanner.py -H 192.168.1.1 -x common

# Full scan on an internal server
python advancedscanner.py -H 10.0.0.50 -x all

# Custom ports for specific testing
python advancedscanner.py -H 192.168.1.1 -p 9200,5601,9300
```

## Troubleshooting

**Error: "Preset 'xyz' not found"**
- Use `--list` to see available presets

**Slow scanning**
- This is normal! The scanner uses threading but wait times ensure accuracy
- For faster results, use `-x common` instead of `-x all`

**Timeout errors**
- Some services might not respond - this is expected
- Try increasing your network timeout or checking the target's firewall

Enjoy scanning!
