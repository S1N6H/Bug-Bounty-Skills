---
name: windows-prefetch-analysis
description: >
  Analyze Windows prefetch files (.pf) to determine evidence of program execution. This skill 
  details how to extract execution times, run counts, and the paths of files accessed 
  by a program, which is critical for incident response and malware timeline reconstruction.
domain: cybersecurity
subdomain: incident-response
category: Forensics
difficulty: intermediate
estimated_time: "1-2 hours"
mitre_attack:
  tactics: [TA0002, TA0003]
  techniques: [T1204]
platforms: [windows]
tags: [forensics, dfir, prefetch, incident-response, program-execution, evidence]
tools: [PECmd, wmic, powershell]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Windows Prefetch Analysis

## When to Use
- When investigating a compromised Windows system to answer the question: "Did the attacker actually run this tool/malware?"
- To build a timeline of threat actor activities by examining execution timestamps and accessed files.
- When an attacker has deleted their malware, but the prefetch file remains as evidence.


## Prerequisites
- Forensic image or live access to the affected system(s)
- Forensic workstation with analysis tools (Autopsy, Volatility, Timeline Explorer)
- Chain of custody documentation initiated for evidence handling
- Write-blocker for disk forensics or memory acquisition tool (e.g., DumpIt, WinPmem)

## Workflow

### Phase 1: Locating and Understanding Prefetch Files

Prefetch files are typically located at `C:\Windows\Prefetch`. 
They are named ending with `.pf` (e.g., `CMD.EXE-4A81B364.pf`).

*Note: Prefetch is enabled by default on Windows Client OS architectures but may be disabled on Windows Servers.*

### Phase 2: Offline Analysis with PECmd (Eric Zimmerman's Tools)

```cmd
# Concept: Parse a single prefetch file PECmd.exe -f "C:\Windows\Prefetch\MIMIKATZ.EXE-53D22409.pf"

# PECmd.exe -d "C:\Windows\Prefetch\" -q --csv "C:\Forensics\Output" --csvf "prefetch_timeline.csv"
```

### Phase 3: Interpreting the Output

When examining the parsed output, focus on:
- **Run Count**: How many times was the binary executed?
- **Execution Times**: Up to 8 previous execution timestamps (depending on OS version). Last execution time is crucial for timeline building.
- **Files/Directories Accessed**: The directories and files the program loaded (e.g., DLLs, configuration files, text files the attacker interacted with).

### Phase 4: Basic Live System Check (Powershell)

```powershell
# Get-ChildItem -Path "C:\Windows\Prefetch" | Where-Object { $_.Name -match "MIMIKATZ|PSEXEC|NC.EXE" } | Select-Object Name, LastWriteTime
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Locate Prefetch Folder ] --> B{Prefetch Enabled? ]}
    B -->|Yes| C[Extract .pf Files ]
    B -->|No| D[Check ShimCache/Amcache ]
    C --> E[Parse with PECmd ]
```

## 🔵 Blue Team Detection & Defense
- **Monitor Deletion of Prefetch Files**: **Centralized Forensics Collection**: **Threat Hunting via File Paths**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Windows Prefetch Analysis — Assessment Report
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
- SANS InfoSec Reading Room: [Prefetch Forensics](https://www.sans.org/white-papers/36972/)
- Eric Zimmerman Tools: [PECmd](https://ericzimmerman.github.io/#!index.md)
