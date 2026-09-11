---
name: windows-registry-forensics
description: >
  Conduct expert-level incident response analysis of the Windows Registry structure (SAM, SYSTEM, 
  SOFTWARE, NTUSER.DAT). Extract pivotal artifacts detailing threat actor execution (ShimCache, Amcache, UserAssist), 
  persistence mechanisms (RunKeys), and lateral movement activities (RDP connections, mapped drives).
domain: cybersecurity
subdomain: incident-response
category: Forensics
difficulty: expert
estimated_time: "4-6 hours"
mitre_attack:
  tactics: [TA0003, TA0007, TA0008]
  techniques: [T1547.001, T1059, T1021.001]
platforms: [windows]
tags: [forensics, registry, incident-response, shimcache, amcache, userassist, lateral-movement]
tools: [registry-explorer, regripper, kape]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Windows Registry Forensics

## When to Use
- When triaging a compromised Windows workstation during a major incident to determine *exactly* which malicious executables ran, when they ran, and what specific USB devices were inserted.
- To detect long-term, stealthy malware persistence using obscure "Run" keys or Service entries hidden deep within the `SOFTWARE` or `SYSTEM` hives.
- To reconstruct an attacker's lateral movement paths across the domain by parsing their historical RDP connections, MRU (Most Recently Used) jump lists, and typed URLs within `NTUSER.DAT`.


## Prerequisites
- Forensic image or live access to the affected system(s)
- Forensic workstation with analysis tools (Autopsy, Volatility, Timeline Explorer)
- Chain of custody documentation initiated for evidence handling
- Write-blocker for disk forensics or memory acquisition tool (e.g., DumpIt, WinPmem)

## Workflow

### Phase 1: Acquiring the Hives (Live Triage)

```text
# Concept: The Registry hives are strictly locked by the Windows Kernel while the OS is running.
# You cannot simply 'copy' them. You must acquire them via KAPE, Volume Shadow Copies (VSS), 
# or specialized extraction tools.

# System-wide Hives (Located at `C:\Windows\System32\config`):
# - SYSTEM (System config, Network interfaces, Devices)
# - SOFTWARE (Installed applications, Global Run keys)
# - SAM (Local User Accounts & NTLM password hashes)
# - SECURITY (LSA Policies, User Rights)
# - Amcache.hve (Application Execution Cache)

# User-specific Hive (Located at `C:\Users\<Username>\`):
# - NTUSER.DAT (User configuration, Typed Paths, UserAssist, Recent Docs)

# 1. Extraction via KAPE (Kroll Artifact Parser and Extractor):
kape.exe --tsource C: --target RegistryHives --tdest C:\Triage_Data\
```

### Phase 2: Evidence of Execution (Amcache & ShimCache)

```text
# Concept: Did the malware execute? If the attacker deleted `malware.exe`, the Registry 
# still vividly remembers that it *was* there and *ran* months ago via compatibility caches.

# 1. Parsing the Amcache (Amcache.hve)
# This hive meticulously records the SHA1 hash, absolute path, File size, and First Execution Time 
# of virtually every single executable run on Windows 10/11.
# Analysis Tool: Load `Amcache.hve` into Eric Zimmerman's Registry Explorer or run RegRipper.
# Path: Root\InventoryApplicationFile
# Result: Discovery of `C:\Windows\Temp\payload.exe` executed at 2024-03-12 02:45 UTC with SHA1 hash `F8B...`.

# 2. Parsing the ShimCache / AppCompatCache (SYSTEM Hive)
# Tracks executables recently run to ensure OS compatibility. Useful because it survives reboots.
# Path: SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache
# Result: Discovery of an attacker renaming `powershell.exe` to `svchost.exe` and executing it.
```

### Phase 3: Evidence of Lateral Movement & Network Activity

```text
# Concept: An attacker compromises a workstation and then RDPs to the Domain Controller.
# Even if they delete the Windows Event Logs, the RDP client records the IP addresses and usernames
# connected to permanently inside the specific User's Registry (NTUSER.DAT).

# 1. Analyzing RDP Connections (NTUSER.DAT)
# Path: Software\Microsoft\Terminal Server Client\Default
# Result: Lists the IP address `10.1.5.55` and `MRU0` (Most Recently Used).
# Path: Software\Microsoft\Terminal Server Client\Servers\<IP_Address>
# Result: Lists the `UsernameHint` (e.g., `Administrator` or `SVC_Account`), proving exactly WHICH 
# hijacked account they used to leapfrog to the server.

# 2. Analyzing Mapped Network Drives (NTUSER.DAT)
# Path: Software\Microsoft\Windows\CurrentVersion\Explorer\Map Network Drive MRU
# Result: Shows the attacker mapping the `\\Finance-Server\C$` administrative share locally to their `Z:` drive to exfiltrate data.
```

### Phase 4: Proving Persistence Mechanisms (RunKeys)

```text
# Concept: Malware must survive a reboot. It writes an entry telling Windows "Every time you boot, run me."

# 1. Analyzing Standard Run / RunOnce Keys (SOFTWARE and NTUSER.DAT)
# System-wide (Affecting all users): SOFTWARE\Microsoft\Windows\CurrentVersion\Run
# User-specific: NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Run
# Result: Discovered an entry named `Windows_Updater` pointing to `C:\ProgramData\svchost.exe`.

# 2. Obscure Persistence (SYSTEM Hive Services)
# Path: SYSTEM\CurrentControlSet\Services
# Attackers create hidden malicious Services executing DLLs. Analyze the `ImagePath` and `ErrorControl` values 
# to determine if the payload boots via ServiceHost.
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Acquire Locked Registry Hives] --> B{What is the analytical goal?}
    B -->|Prove Execution| C[Parse Amcache.hve & ShimCache in SYSTEM]
    B -->|Find Persistance| D[Parse Run Keys in NTUSER.DAT & SOFTWARE, Services in SYSTEM]
    B -->|Track User Actions| E[Parse UserAssist & TypedURLs in NTUSER.DAT]
    C --> F[Recover SHA1 Hashes & Compile Timestamps of deleted malware]
    D --> G[Identify malicious DLLs or PowerShell loaders launching quietly at boot]
    E --> H[Prove attacker accessed specific confidential PDF files or directories (`RecentDocs`)]
    F --> I[Upload Hash to VirusTotal / Write YARA Rule for sweeping network]
```

## 🔵 Blue Team Detection & Defense
- **Automated Artifact Parsing**: Traditional IT departments respond to an incident by imaging an entire 1TB hard drive over the network (taking 24 hours). Elite IR teams deploy KAPE or Velociraptor rapidly across thousands of endpoints to target and extract *only* the Registry Hives and Event Logs (averaging 50MB) returning forensic data and execution evidence across the organization in seconds.
- **Sysmon Integration**: The registry is deeply complex. Deploy Microsoft Sysmon (System Monitor) prioritizing Event ID 12, 13, and 14 (Registry Object Creation, Modification, and Deletion) specifically monitoring paths like `\CurrentVersion\Run` or `\Services\`. Sysmon converts obscure Registry hex modifications into easily parsable JSON strings instantly injected into the SIEM.
- **Limit Administrator Execution**: The vast majority of deeply ingrained attacker persistence requires modifying the `SYSTEM` or `SOFTWARE` hives. Implementing Endpoint Privilege Management (EPM), heavily restricting standard users from attaining Local Administrator privileges, forces attackers to on `NTUSER.DAT` persistence, simplifying the triage process identically.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Registry Hive | A logical group of keys, subkeys, and values in the Windows Registry permanently backed by a set of files residing on the disk |
| Amcache | A hive explicitly tracking the execution profile of applications, providing analysts with the exact First Run timestamp and SHA-1 algorithmic hash of deleted executables |
| ShimCache / AppCompatCache | An OS component monitoring compatibility issues with older software. It perfectly records the absolute path and precisely when a file was last modified/executed |
| MRU | Most Recently Used; a pervasive tracking concept utilized across the Registry identifying the exact files, folders, and applications a user interacted with chronologically |

## Output Format
```
Forensics Triage Brief: Incident #899 - Ransomware Precursor Activity
=====================================================================
Target Endpoint: `FIN-WORKSTATION-02`
Artifact Evaluated: `Amcache.hve`, `NTUSER.DAT`, `SYSTEM`

Description:
Digital forensics triage was initiated on `FIN-WORKSTATION-02` following a suspicious Antivirus flag. The endpoint's primary Registry hives were extracted utilizing KAPE for offline parsing utilizing Registry Explorer.

Analysis of the `Amcache.hve` immediately confirmed the execution of a deleted binary located at `C:\Users\Public\svchost.exe` occurring at `2024-03-24 07:12:44Z`. The recovered SHA-1 hash (`8A2B...`) corresponded directly with the Cobalt Strike executable beacon platform. 

Reviewing the `NTUSER.DAT` hive for the compromised user account mapped lateral movement activities; specifically, the Terminal Server Client subkeys indicated a successful Remote Desktop Protocol (RDP) authentication utilizing the `Admin` account pivoting toward the Domain Controller (`10.0.0.5`) exactly 18 minutes post-initial execution.

Conclusion:
The attacker established initial access via a disguised payload, circumvented local protections, and definitively pivoted to core infrastructure. Immediate containment of the Domain Controller and wide-scale password resets are required. 
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
- SANS Institute: [Windows Registry Forensics Cheat Sheet](https://www.sans.org/posters/windows-registry-forensics/)
- Eric Zimmerman Tools: [Registry Explorer/RECmd](https://ericzimmerman.github.io/#!index.md)
- Harlan Carvey: [Windows Registry Forensics Book](https://www.amazon.com/Windows-Registry-Forensics-Advanced-Digital/)
