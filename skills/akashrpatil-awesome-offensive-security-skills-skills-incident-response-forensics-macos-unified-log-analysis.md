---
name: macos-unified-log-analysis
description: >
  Perform forensic analysis of the macOS Unified Logging System (ULS) to investigate system 
  events, application crashes, kernel panics, and potential indicators of compromise (IoCs) 
  such as persistence mechanisms or unauthorized access.
domain: cybersecurity
subdomain: incident-response
category: Forensics
difficulty: intermediate
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0008, TA0005]
  techniques: [T1078, T1059.004]
platforms: [macos]
tags: [forensics, macos, unified-log, incident-response, log-analysis]
tools: [log, console]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# macOS Unified Log Analysis

## When to Use
- When investigating a security incident on a macOS endpoint and needing to trace attacker activity, malware execution, or system anomalies.
- To diagnose deep system issues, application crashes, or kernel panics using Apple's centralized logging architecture.
- When traditional log files (`/var/log/*`) do not contain sufficient information, as macOS has migrated most logging to the Unified Logging System (in memory and binary formats).


## Prerequisites
- Forensic image or live access to the affected system(s)
- Forensic workstation with analysis tools (Autopsy, Volatility, Timeline Explorer)
- Chain of custody documentation initiated for evidence handling
- Write-blocker for disk forensics or memory acquisition tool (e.g., DumpIt, WinPmem)

## Workflow

### Phase 1: Understanding the Unified Logging System (ULS)

```text
# Concept: Introduced in macOS Sierra (10.12), the ULS replaced traditional text-based logs 
# (like system.log) with a high-performance, centralized system. Logs are stored in a compressed, 
# proprietary binary format.
# 
# Key Locations:
# - In-Memory: Recent, volatile logs are held in memory.
# - On-Disk: `/var/db/diagnostics/` and `/var/db/uuidtext/` (Requires severe privileges to access directly).
# 
# Because the logs are binary, you cannot just `cat` or `grep` the raw files. You MUST use 
# the built-in `log` command-line utility or the macOS Console app.
```

### Phase 2: Live System Triage (Using the `log` command)

```bash
# Concept: Use the `log show` command to query the ULS. Filtering is critical, as the ULS 
# generates an overwhelming amount of data (thousands of events per second).

# 1. View logs from the last 1 hour
log show --last 1h

# 2. Filtering by Subsystem and Category (Crucial for noise reduction)
# Example: Look only for authentication events (OpenDirectory/Authentication)
log show --predicate 'subsystem == "com.apple.opendirectoryd" AND category == "System"' --last 24h

# 3. Search for specific keywords (e.g., suspicious processes or IP addresses)
log show --predicate 'eventMessage CONTAINS "sudo"' --last 2h
```

### Phase 3: Offline Forensics (Analyzing Log Archives)

```bash
# Concept: During IR, you rarely want to analyze logs on the live system. Instead, collect a 
# `logarchive` (a bundle of the binary logs) and analyze it on your forensic workstation.

# 1. Collect the log archive on the compromised Mac (requires root)
sudo log collect --last 3d --output /tmp/compromised_mac.logarchive

# 2. Analyze the archive on your forensic Mac
log show --archive /path/to/compromised_mac.logarchive --predicate 'eventMessage CONTAINS "malware"'

# 3. Export to JSON for integration into SIEM or Python scripts
log show --archive /path/to/compromised_mac.logarchive --style json > export.json
```

### Phase 4: Hunting for Indicators of Compromise (IoCs)

```text
# Concept: To find evil, you must know what subsystem generates the relevant logs.

# 1. Investigating Persistence (LaunchDaemons / LaunchAgents)
# Subsystem: com.apple.xpc.launchd
log show --predicate 'subsystem == "com.apple.xpc.launchd" AND eventMessage CONTAINS "SubmitJob"' --last 24h

# 2. Investigating Terminal / Shell Execution
log show --predicate 'process == "Terminal" OR process == "bash" OR process == "zsh"'

# 3. Investigating Gatekeeper/XProtect (Apple's built-in AV)
log show --predicate 'subsystem == "com.apple.syspolicy" OR subsystem == "com.apple.xprotect"'
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Isolate macOS Endpoint] --> B{Live Analysis or Offline Triage?}
    B -->|Offline (Preferred)| C[Run `sudo log collect` to generate `.logarchive`]
    B -->|Live| D[Use `log show` or Console.app directly]
    C --> E[Transfer `.logarchive` to Forensic Workstation]
    E --> F[Construct precise Predicate filters]
    D --> F
    F --> G{Are relevant events found?}
    G -->|Yes| H[Export to JSON, timeline the events, correlate with file system artifacts e.g. fseventsd]
    G -->|No| I[Broaden predicate filters, check timestamps, or pivot to alternative artifacts like Browser History or Spotlight]
```

## 🔵 Blue Team Detection & Defense
- **Centralized Forwarding**: The macOS ULS is notoriously difficult to forward to standard SIEMs natively because it's binary. Utilize endpoint agents (like CrowdStrike Falcon, Jamf Protect, or specifically engineered forwarders like Splunk Universal Forwarder with ULS support) to parse and send critical ULS events (like authentication failures or `launchd` modifications) to your centralized logging platform.
- **Log Retention Policies**: By default, macOS rotates out high-volume volatile logs quickly (often within days or hours depending on disk space). Ensure systems are configured (via MDM profiles) to retain critical security logs for a longer duration to facilitate effective retrospective incident response.
- **Private Data Obfuscation**: Understand that macOS natively redacts "private" data from the ULS (showing `<private>` in the logs instead of filenames/IPs) unless a specific configuration profile is installed. During an active incident on a managed device, deploying a profile to enable private data logging can be crucial for full visibility.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Unified Logging System (ULS) | Apple's centralized, high-performance, binary-formatted logging architecture replacing traditional text logs |
| Predicate | A highly specific, C-style filtering syntax used by the `log` command to query the ULS database efficiently |
| `.logarchive` | A portable directory bundle containing a snapshot of the ULS binary tracev3 files, perfect for offline forensic analysis |


## Output Format
```
Macos Unified Log Analysis — Assessment Report
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
- Apple Developer: [Logging in macOS](https://developer.apple.com/documentation/os/logging)
- SANS: [macOS Unified Log Analysis](https://www.sans.org/blog/macos-unified-log-analysis/)
- Objective-See: [The macOS Unified Logging System](https://objective-see.org/blog/blog_0x33.html)
