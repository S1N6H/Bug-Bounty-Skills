---
name: sysmon-process-creation-analysis
description: >
  Analyze Sysmon Event ID 1 (Process Creation) logs to identify malicious executions, living-off-the-land 
  binaries (LOLBins), command-line obfuscation, and suspicious parent-child process relationships.
domain: cybersecurity
subdomain: incident-response
category: Forensics
difficulty: intermediate
estimated_time: "2 hours"
mitre_attack:
  tactics: [TA0002, TA0005]
  techniques: [T1059, T1036, T1218]
platforms: [windows]
tags: [sysmon, dfir, process-creation, event-id-1, threat-hunting, blue-teaming, lolbins]
tools: [event-viewer, powershell, splunk, elastic]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Sysmon Process Creation Analysis (Event ID 1)

## When to Use
- During proactive threat hunting or reactive incident response to trace the execution flow of malware, scripts, or attacker activity.
- To detect the use of LOLBins (like PowerShell, cmd, certutil) and identify obfuscated command-line arguments indicating malicious intent.


## Prerequisites
- Forensic image or live access to the affected system(s)
- Forensic workstation with analysis tools (Autopsy, Volatility, Timeline Explorer)
- Chain of custody documentation initiated for evidence handling
- Write-blocker for disk forensics or memory acquisition tool (e.g., DumpIt, WinPmem)

## Workflow

### Phase 1: Understanding Event ID 1 Fields

```text
# Concept: Sysmon Event ID 1 ```

### Phase 2: Hunting for Suspicious Parent-Child Relationships

```powershell
# Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational" | Where-Object { 
  $_.Id -eq 1 -and $_.Message -match "ParentImage:.*winword.exe" -and $_.Message -match "Image:.*(?:powershell\.exe|cmd\.exe|wscript\.exe|cscript\.exe)" 
} | Select-Object TimeCreated, Message | Format-List
```

### Phase 3: Detecting Command-Line Obfuscation and Encoding

```splunk
# index=sysmon EventCode=1 (CommandLine="*-e*" OR CommandLine="*-enc*" OR CommandLine="*-EncodedCommand*") Image="*\\powershell.exe"
| table _time, User, ParentImage, Image, CommandLine
```

### Phase 4: Hunting for Known LOLBins (Living Off The Land)

```spl
# index=sysmon EventCode=1 (Image="*\\certutil.exe" AND (CommandLine="*-urlcache*" OR CommandLine="*-f*" OR CommandLine="*-split*"))
| stats count by CommandLine, User, Computer
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Analyze Event ] --> B{Suspicious Indicator? ]}
    B -->|Yes| C[Investigate Context ]
    B -->|No| D[Log as Benign ]
    C --> E[Extract Artifacts ]
```

## 🔵 Blue Team Detection & Defense
- **Filter Tuning**: **Contextual Baselines**: - **Correlation Rules**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Sysmon Process Creation Analysis — Assessment Report
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
- Microsoft: [Sysmon Setup and Configuration](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)
- JPCERT: [Tool Analysis Result Sheet](https://jpcertcc.github.io/ToolAnalysisResultSheet/)
