---
name: nmap-advanced-network-scanning
description: >
  Perform advanced network scanning and service enumeration using Nmap for penetration testing and
  security assessments. Use this skill when conducting network reconnaissance, port scanning, service
  version detection, OS fingerprinting, and vulnerability scanning. Covers stealth scanning, firewall
  evasion, NSE script usage, and network mapping for infrastructure penetration tests.
domain: cybersecurity
subdomain: penetration-testing
category: Network
difficulty: beginner
estimated_time: "1-3 hours"
mitre_attack:
  tactics: [TA0043, TA0007]
  techniques: [T1046, T1595.001]
platforms: [linux, windows, macos]
tags: [nmap, network-scanning, port-scanning, service-enumeration, os-fingerprinting, vulnerability-scanning, pentest]
tools: [nmap, masscan, rustscan]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Nmap Advanced Network Scanning

## When to Use
- As the first step in network penetration tests
- When mapping network topology and identifying live hosts
- When enumerating services and versions running on targets
- When performing OS fingerprinting for exploit selection
- When running vulnerability scripts via NSE


## Prerequisites
- Network access to the target subnet (VPN, pivot, or direct connection)
- Nmap and relevant network scanning tools installed
- Understanding of TCP/IP, common protocols, and network segmentation
- Root/admin access on the attack machine for raw socket operations

## Workflow

### Phase 1: Host Discovery

```bash
# Ping sweep (find live hosts)
nmap -sn 10.10.10.0/24 -oA host_discovery

# ARP scan (same subnet, most reliable)
nmap -PR -sn 10.10.10.0/24

# Without ping (bypass ICMP blocking)
nmap -Pn -sn 10.10.10.0/24

# TCP SYN ping on common ports
nmap -PS22,80,443,445 -sn 10.10.10.0/24

# Multiple ranges
nmap -sn 10.10.10.0/24 192.168.1.0/24 172.16.0.0/16
```

### Phase 2: Port Scanning

```bash
# Quick top 100 ports
nmap -F 10.10.10.100

# Full TCP scan (all 65535 ports)
nmap -p- 10.10.10.100

# Common pentest scan (SYN scan + version + scripts + OS)
sudo nmap -sS -sV -sC -O -p- 10.10.10.100 -oA full_scan

# UDP scan (slow but important)
sudo nmap -sU --top-ports 200 10.10.10.100

# Speed-optimized full scan
nmap -p- --min-rate 10000 -T4 10.10.10.100

# Stealth SYN scan (default with root)
sudo nmap -sS -p- 10.10.10.100

# Connect scan (without root)
nmap -sT -p- 10.10.10.100

# Masscan for ultra-fast initial scan (then Nmap for details)
masscan 10.10.10.0/24 -p1-65535 --rate=10000 -oJ masscan_results.json
# Parse results and feed to Nmap for service detection
```

### Phase 3: Service & Version Detection

```bash
# Version detection
nmap -sV -p 22,80,443,445,3306,8080 10.10.10.100

# Aggressive version detection
nmap -sV --version-intensity 5 -p- 10.10.10.100

# OS detection
sudo nmap -O 10.10.10.100

# Combined scan (version + OS + default scripts)
sudo nmap -A -p- 10.10.10.100 -oA aggressive_scan
```

### Phase 4: NSE Vulnerability Scripts

```bash
# Run default scripts
nmap -sC -p 22,80,445 10.10.10.100

# Vulnerability scanning
nmap --script vuln -p 22,80,445 10.10.10.100

# Specific vulnerability checks
nmap --script smb-vuln-ms17-010 -p 445 10.10.10.100  # EternalBlue
nmap --script ssl-heartbleed -p 443 10.10.10.100       # Heartbleed
nmap --script http-shellshock -p 80 10.10.10.100       # Shellshock

# SMB enumeration
nmap --script smb-enum-shares,smb-enum-users,smb-os-discovery -p 445 10.10.10.100

# HTTP enumeration
nmap --script http-enum,http-headers,http-methods,http-title -p 80,443 10.10.10.100

# DNS enumeration
nmap --script dns-brute -p 53 ns1.target.com

# Banner grab
nmap --script banner -p 21,22,25,80,110,143,443 10.10.10.100
```

### Phase 5: Firewall Evasion

```bash
# Fragment packets
nmap -f -p 80,443 10.10.10.100

# Specify MTU
nmap --mtu 24 -p 80,443 10.10.10.100

# Decoy scan
nmap -D RND:10 -p 80 10.10.10.100

# Source port manipulation
nmap --source-port 53 -p 80 10.10.10.100

# Append random data
nmap --data-length 200 -p 80 10.10.10.100

# MAC address spoofing
nmap --spoof-mac 0 -p 80 10.10.10.100

# Idle zombie scan
nmap -sI zombie_host:port target_host
```

## 🔵 Blue Team Detection
- **IDS rules**: Detect SYN scans, version probes, and NSE script activity
- **Rate limiting**: Alert on rapid port scanning from single source
- **Firewall logging**: Monitor for sequential port connection attempts
- **Honeypots**: Deploy network honeypots on unused IPs to detect scanning

## Key Concepts
| Concept | Description |
|---------|-------------|
| SYN scan (-sS) | Half-open scan, stealthier, requires root |
| Connect scan (-sT) | Full TCP connection, no root needed |
| UDP scan (-sU) | Scans UDP ports, very slow |
| NSE | Nmap Scripting Engine for extended functionality |
| OS fingerprinting | Identifying the target's operating system |

## Output Format
```
Network Scan Report
====================
Target: 10.10.10.0/24
Live Hosts: 42/254
Open Ports Summary:
  22/tcp (SSH): 15 hosts
  80/tcp (HTTP): 23 hosts  
  443/tcp (HTTPS): 18 hosts
  445/tcp (SMB): 8 hosts (2 vulnerable to MS17-010!)
  3389/tcp (RDP): 5 hosts

Critical Findings:
1. 10.10.10.50 - MS17-010 (EternalBlue) vulnerable
2. 10.10.10.100 - Anonymous FTP access enabled
3. 10.10.10.75 - Outdated OpenSSH 7.2 (CVE-2016-6515)
```

## 🛡️ Remediation & Mitigation Strategy
- **Input Validation:** Sanitize and strictly type-check all inputs.
- **Least Privilege:** Constrain component execution bounds.


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- Nmap: [Official Reference Guide](https://nmap.org/book/man.html)
- NSE: [Script Documentation](https://nmap.org/nsedoc/)
- HackTricks: [Pentesting Network](https://book.hacktricks.xyz/generic-methodologies-and-resources/pentesting-network)
