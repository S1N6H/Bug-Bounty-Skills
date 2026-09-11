---
name: volatility-memory-forensics
description: >
  Analyze full RAM captures (memory dumps) to extract forensic artifacts, detect stealthy malware,
  recover injected shellcode, and identify rootkits that bypass traditional disk-based antivirus
  scanning. Use this skill during Incident Response and advanced threat hunting engagements to
  identify what was actively running on a compromised system at a specific point in time.
domain: cybersecurity
subdomain: forensics-ir
category: Memory Analysis
difficulty: advanced
estimated_time: "4-8 hours"
mitre_attack:
  tactics: [TA0005]
  techniques: [T1055, T1014, T1140]
platforms: [windows, linux, macos]
tags: [volatility, memory-forensics, incident-response, malware-analysis, rootkit, process-injection, ram-dump]
tools: [volatility3, volatility2, python, strings, grep]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Volatility Memory Forensics (RAM Analysis)

## When to Use
- Following a critical incident where a machine is isolated, and a RAM dump (`.dmp`, `.raw`, `.vmem`) is acquired before shutdown.
- When hunting for Fileless Malware, Advanced Persistent Threats (APTs), or In-Memory execution (e.g., Cobalt Strike Beacons, Meterpreter).
- To recover decrypted passwords, registry keys, or historical command lines that were stored in RAM and never written to disk.
- When analyzing systems suspected of harboring Kernel-level Rootkits.


## Prerequisites
- Memory dump or forensic image acquired from the compromised system
- Volatility 2/3 framework installed with appropriate OS profiles
- Chain of custody documentation maintained for legal admissibility
- Understanding of the target OS memory management and process architecture

## Workflow

### Phase 1: Environment Setup and Profile Identification

```bash
# Concept: Volatility 3 (Python 3) doesn't require "profiles" like Volatility 2,
# it automatically downloads symbol tables based on the OS kernel structure.

# Ensure Volatility 3 is updated
python3 vol.py -h

# 1. Identify the Operating System and Architecture of the Memory Dump
python3 vol.py -f suspicious_machine.raw windows.info

# Output will confirm if it is Windows 10, Windows 7, Linux, etc., and list
# crucial kernel pointers (KDBG, PsActiveProcessHead) needed for deep analysis.
```

### Phase 2: Process Enumeration & Anomaly Hunting

```bash
# Concept: We need to see what programs were running. Malware often
# pretends to be legitimate Windows processes (e.g., svchost.exe) or hides entirely.

# 1. List all active processes (equivalent to Task Manager)
python3 vol.py -f suspicious_machine.raw windows.pslist

# 2. Find hidden processes (Rootkits unlinking from the active process list)
# Compare pslist (standard linked list) vs psscan (carving memory for process headers).
# If a process appears in psscan but NOT pslist -> IT IS HIDDEN / MALICIOUS.
python3 vol.py -f suspicious_machine.raw windows.psscan

# 3. View the Process Tree (Parent/Child relationships)
# Anomalies: `cmd.exe` spawning from `explorer.exe` is normal.
# `cmd.exe` spawning from `services.exe` or `spoolsv.exe` is highly suspicious.
# `svchost.exe` spawning from anything other than `services.exe` is malicious.
python3 vol.py -f suspicious_machine.raw windows.pstree

# 4. View detailed command-line arguments passed to running processes
# e.g., finding `powershell -enc JABzAD0ATgBlAHcALQBPAGIAagBl...`
python3 vol.py -f suspicious_machine.raw windows.cmdline
```

### Phase 3: Malicious Injection Detection

```bash
# Concept: Advanced malware injects itself into legitimate processes (Process Hollowing, 
# DLL Injection) to hide from defensive scrutiny.

# 1. Malfind (Malware Find)
# Scans memory for injected code (specifically, memory segments containing executable code 
# that are NOT backed by a physical file on disk). 
# Critical for finding Cobalt Strike beacons and shellcode!
python3 vol.py -f suspicious_machine.raw windows.malfind

# Warning: Malfind produces false positives (JIT compilers like .NET or browsers).
# Review the hex dump output: Look for "MZ" headers (4D 5A) starting the injected segment.

# 2. Dump the injected suspicious memory segment for reverse engineering
python3 vol.py -f suspicious_machine.raw windows.malfind --dump --pid 4452
# Resulting file (process.4452.0xXYZ.dmp) can be loaded into IDA Pro or Ghidra.
```

### Phase 4: Network Artifact Recovery

```bash
# Concept: Current and terminated network connections can reveal Command and Control (C2) IPs.

# 1. Retrieve Active and Terminated TCP/UDP Connections
python3 vol.py -f suspicious_machine.raw windows.netstat

# Compare the suspicious process PIDs found in Phase 2/3 with their active network connections.
# Example: If `notepad.exe` (PID 1234) has an established connection to a Russian IP on port 443, it is definitively compromised.

# 2. Check the historical DNS cache memory (Requires custom plugin or Vol2)
# Often reveals domains the machine queried recently before the dump occurred.
```

### Phase 5: Credential Extraction (Mimikatz in Memory)

```bash
# Concept: Passwords and NTLM hashes are temporarily stored in the LSASS.exe process memory.

# 1. Dump cached passwords from the registry (SAM and SYSTEM hives in RAM)
python3 vol.py -f suspicious_machine.raw windows.hashdump

# 2. Dump cleartext passwords and Kerberos tickets directly from LSASS (mimikatz wrapper)
python3 vol.py -f suspicious_machine.raw windows.lsadump.lsa
```

### Phase 6: Deep Forensic Artifacts

```bash
# 1. Extract the full Master File Table (MFT) from RAM to rebuild the filesystem
python3 vol.py -f suspicious_machine.raw windows.mftscan

# 2. View loaded DLLs for a suspected process (look for malicious unbacked DLLs)
python3 vol.py -f suspicious_machine.raw windows.dlllist --pid 4452

# 3. YARA Scanning
# Scan the entire memory dump for specific malware signatures
python3 vol.py -f suspicious_machine.raw windows.vadyarascan --yara-file lokibot.yara
```

## 🔵 Blue Team Detection & Defense
- Memory analysis is primarily a post-incident tool. However, defenders rely on Endpoint Detection and Response (EDR) platforms that perform miniature, real-time "malfind" checks (monitoring for `VirtualAlloc` calls with `PAGE_EXECUTE_READWRITE` permissions).
- **Credential Guard**: Windows 10/11 Enterprise feature utilizing Virtualization-Based Security (VBS) to isolate the LSASS process, completely defeating Phase 5 extraction techniques.

## Key Concepts
| Concept | Description |
|---------|-------------|
| RAM / Memory Dump | A complete, byte-for-byte snapshot of the physical RAM of a computer at a given instant |
| Process Hollowing | Malware technique where a legitimate process is started, paused, emptied, and replaced with malicious code |
| VAD | Virtual Address Descriptor; memory structures Windows uses to track memory allocated to processes |
| Fileless Malware | Malware that operates entirely in memory (RAM) and leaves no permanent executable file on the hard drive |

## Output Format
```
Incident Response Memory Forensics Report
=========================================
Asset ID: WIN-ACCTG-04
Date Acquired: 2024-X-X
Analysis Engine: Volatility 3

Executive Summary:
Analysis of the provided memory dump confirms the host was compromised via Fileless Malware (suspected Cobalt Strike Beacon).

Key Findings:
1. Anomalous Processes: Process `spoolsv.exe` (PID 3342) is running without `services.exe` as its parent, violating core Windows architecture. Parent process was identified as `powershell.exe` which terminated prior to the dump.
2. Code Injection: The `windows.malfind` plugin identified a hidden, executable memory page (`PAGE_EXECUTE_READWRITE`) at address `0x60000` inside PID 3342. The segment begins with an `MZ` header (Portable Executable) not backed by disk.
3. Network Traffic: `windows.netstat` confirms PID 3342 held an established HTTPS connection to `192.168.x.x:443`.
4. Credential Theft: Unrelated, `windows.hashdump` successfully extracted NTLM hashes for 5 standard users indicating lateral movement risk.

Forensic Action:
The injected shellcode at address `0x60000` was dumped to file (`pid.3342.dmp`) and submitted to the reverse engineering team for C2 configuration extraction.
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
- Volatility Foundation: [Volatility 3 Documentation](https://github.com/volatilityfoundation/volatility3)
- SANS FOR508: [Advanced Incident Response, Threat Hunting, and Digital Forensics](https://www.sans.org/cyber-security-courses/advanced-incident-response-threat-hunting-training/)
