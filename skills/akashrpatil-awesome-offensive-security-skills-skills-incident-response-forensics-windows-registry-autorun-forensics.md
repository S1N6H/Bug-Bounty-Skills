---
name: windows-registry-autorun-forensics
description: >
  Analyze the Windows Registry to uncover malicious persistence mechanisms. This skill details 
  how to investigate Run keys, Services, Scheduled Tasks registry keys, and Image File Execution 
  Options (IFEO) to locate hidden backdoors.
domain: cybersecurity
subdomain: incident-response
category: Forensics
difficulty: intermediate
estimated_time: "2-3 hours"
mitre_attack:
  tactics: [TA0003]
  techniques: [T1547.001, T1546.012]
platforms: [windows]
tags: [registry, forensics, incident-response, autoruns, dfir, persistence, ifeo]
tools: [regedit, autoruns, regripper]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Windows Registry Autorun Forensics

## When to Use
- During triage of a potentially compromised Windows system to identify how malware survives reboots.
- After extracting the registry hives (SAM, SYSTEM, SOFTWARE, NTUSER.DAT) from a forensic disk image for offline analysis.


## Prerequisites
- Forensic image or live access to the affected system(s)
- Forensic workstation with analysis tools (Autopsy, Volatility, Timeline Explorer)
- Chain of custody documentation initiated for evidence handling
- Write-blocker for disk forensics or memory acquisition tool (e.g., DumpIt, WinPmem)

## Workflow

### Phase 1: Identifying Run / RunOnce Keys

```powershell
# Concept: Windows Registry Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
```

### Phase 2: Detecting IFEO (Image File Execution Options) Injection

```powershell
# Get-ChildItem -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options" | Select-Object Name | Where-Object { $_.Name -match "sethc.exe|utilman.exe" }
# ```

### Phase 3: Inspecting Services Registry Keys

```powershell
# Get-ChildItem -Path "HKLM:\SYSTEM\CurrentControlSet\Services" | Where-Object { (Get-ItemProperty $_.PSPath).ImagePath -match "C:\\Users\\|C:\\ProgramData\\" } | Select-Object Name, @{Name="ImagePath"; Expression={(Get-ItemProperty $_.PSPath).ImagePath}}
```

### Phase 4: Offline Analysis using RegRipper

```bash
# # rip.pl -r /mnt/evidence/Windows/System32/config/SOFTWARE -p run
rip.pl -r /mnt/evidence/Users/Bob/NTUSER.DAT -p userinit
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Extract Hives ] --> B{Parse Keys ]}
    B -->|Yes| C[Identify Anomalies ]
    B -->|No| D[Check Alternate ]
    C --> E[Extract Artifacts ]
```

## 🔵 Blue Team Detection & Defense
- **Sysinternals Autoruns**: **Registry Key Auditing (GPO)**: **Registry Activity Monitoring (Sysmon Event ID 12, 13, 14)**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Windows Registry Autorun Forensics — Assessment Report
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
- SANS: [Windows Registry Forensics](https://www.sans.org/posters/windows-forensic-analysis/)
- Microsoft Sysinternals: [Autoruns](https://docs.microsoft.com/en-us/sysinternals/downloads/autoruns)
