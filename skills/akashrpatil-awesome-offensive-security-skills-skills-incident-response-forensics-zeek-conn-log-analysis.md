---
name: zeek-conn-log-analysis
description: >
  Analyze Zeek (formerly Bro) `conn.log` files to hunt for malicious network behaviors, 
  including C2 beaconing, long-lived anomalous connections, and data exfiltration patterns.
domain: cybersecurity
subdomain: incident-response
category: Forensics
difficulty: intermediate
estimated_time: "2 hours"
mitre_attack:
  tactics: [TA0011, TA0010]
  techniques: [T1071, T1043]
platforms: [network, linux]
tags: [zeek, network-forensics, threat-hunting, dfir, c2-beaconing, packet-analysis]
tools: [zeek, awk, zeek-cut, jq]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Zeek conn.log Analysis

## When to Use
- During network forensics investigations or active threat hunting to identify compromised hosts communicating with Command and Control (C2) infrastructure.
- To detect unusual network baseline deviations without relying entirely on deep packet inspection or payload signatures.


## Prerequisites
- Forensic image or live access to the affected system(s)
- Forensic workstation with analysis tools (Autopsy, Volatility, Timeline Explorer)
- Chain of custody documentation initiated for evidence handling
- Write-blocker for disk forensics or memory acquisition tool (e.g., DumpIt, WinPmem)

## Workflow

### Phase 1: Understanding conn.log Structure

```bash
# head conn.log | zeek-cut -c ts uid id.orig_h id.orig_p id.resp_h id.resp_p proto service duration orig_bytes resp_bytes conn_state
```

### Phase 2: Hunting for C2 Beaconing (Frequency Analysis)

```bash
# cat conn.log | zeek-cut id.orig_h id.resp_h id.resp_p duration | \
awk '{print $1, $2, $3}' | sort | uniq -c | sort -nr | head -n 20
```

### Phase 3: Identifying Long-Connections (Data Exfil / Interactive Shells)

```bash
# cat conn.log | zeek-cut id.orig_h id.resp_h id.resp_p duration orig_bytes resp_bytes | \
awk '$4 > 3600 {print $0}' | sort -nrk 4
```

### Phase 4: Detecting Odd Port-Service Mismatches

```bash
# cat conn.log | zeek-cut id.resp_p service | grep -E '^443\s+http$' | less

# cat conn.log | zeek-cut id.resp_p service | grep -E '^80\s+ssl$' | less
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Parse conn.log ] --> B{Anomalies Found ]}
    B -->|Yes| C[Correlate Logs ]
    B -->|No| D[Tune Heuristics ]
    C --> E[Isolate Host ]
```

## 🔵 Blue Team Detection & Defense
- **Automate Beacon Tracking (RITA / Zeek Detect)**: **Threat Intelligence Feeds**: **Baseline Internal Traffic**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Zeek Conn Log Analysis — Assessment Report
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
- Zeek Documentation: [Logging Framework](https://docs.zeek.org/en/current/frameworks/logging.html)
- Active Countermeasures: [RITA (Real Intelligence Threat Analytics)](https://github.com/activecm/rita)
