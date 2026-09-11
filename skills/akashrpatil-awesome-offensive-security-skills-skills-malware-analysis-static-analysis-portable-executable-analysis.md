---
name: portable-executable-analysis
description: >
  Perform static reverse engineering and analysis on Windows Portable Executable (PE) files to identify
  malicious indicators without executing the file. Use this skill during Incident Response, malware
  triage, or threat hunting to safely extract metadata, imported APIs, exported functions, embedded
  strings, and packed indicators from suspicious Windows binaries (.exe, .dll, .sys).
domain: cybersecurity
subdomain: malware-analysis
category: Static Analysis
difficulty: intermediate
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0005, TA0002]
  techniques: [T1027, T1129, T1106]
platforms: [windows, linux]
tags: [malware-analysis, static-analysis, reverse-engineering, portable-executable, infosec, pe-headers, string-extraction]
tools: [peirates, pestudio, peid, strings, floss, capstone, python-pefile]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Portable Executable (PE) Analysis

## When to Use
- You receive a suspicious attachment (.exe, .dll, .scr) and need to verify if it is malicious without infecting a sandbox.
- When conducting static malware triage to determine the file's capabilities (e.g., does it have networking functions? Keylogging functions?).
- When trying to identify if a binary is "packed" (obfuscated/compressed) to evade antivirus signatures.
- To extract hardcoded Configuration Data, C2 (Command and Control) IP addresses, or Bitcoin wallets from ransomware or trojans.


## Prerequisites
- Isolated analysis environment (VM with snapshot capability)
- Sample file safely obtained and handled with appropriate precautions
- PE analysis tools (PE-bear, CFF Explorer, Detect It Easy) installed
- Disassembler/decompiler (Ghidra, IDA Free, or Binary Ninja) configured

## Workflow

### Phase 1: File Identification & Hashing

```bash
# Concept: Always identify the actual file type, as malware authors often disguise 
# executables with fake extensions (e.g., invoice.pdf.exe).

# 1. Generate Hashes to cross-reference with VirusTotal or Threat Intelligence
md5sum suspicious_file.bin
sha256sum suspicious_file.bin

# 2. Check the real file type using magic bytes
file suspicious_file.bin
# Output expected: PE32 executable (GUI) Intel 80386, for MS Windows
# Keep an eye out for UPX compressed warnings or unexpected compiled languages (.NET, Go).
```

### Phase 2: String Extraction & Obfuscation Checks

```bash
# Concept: Malware contains hardcoded text (API names, error messages, IPs).
# Extracting them statically is the fastest way to understand a program's intent.

# 1. Standard string extraction (ASCII and Unicode)
strings -a suspicious_file.bin > strings_ascii.txt
strings -el suspicious_file.bin > strings_unicode.txt

# 2. Search for common malicious patterns:
grep -i "http\|https\|ftp\|www" strings_ascii.txt      # Look for C2 domains
grep -i "cmd.exe\|powershell\|vssadmin" strings_ascii.txt # Look for execution / shadow copy deletion
grep -i "CurrentVersion\\Run" strings_ascii.txt        # Look for persistence mechanisms

# 3. Use FLOSS (FireEye Labs Obfuscated String Solver)
# If strings output is garbage, the strings are likely encoded (XOR'd) or packed.
# FLOSS automatically deobfuscates standard encryption routines statically.
floss suspicious_file.bin > deobfuscated_strings.txt
```

### Phase 3: PE Header Analysis

```bash
# Concept: The PE Header contains the blueprint for how Windows loads the file into memory.

# 1. Check Compilation Timestamps (pefile / pestudio)
# Is the timestamp in the future? Is it 1992? Attackers frequently spoof timestamps.
python3 -c "import pefile; pe = pefile.PE('suspicious_file.bin'); print(pe.FILE_HEADER.dump_dict())"

# 2. Analyze Sections (.text, .data, .rsrc)
# The .text section contains executable code. The .data contains initialized variables.
# - High Entropy (randomness > 7.0) in any section usually means it is packed or encrypted.
# - Virtual Size significantly larger than Raw Size means a payload will unpack itself into memory (classic packing indicator).

# Detect packers computationally:
# e.g., using PEiD or Detect It Easy (DIE) or Yara rules.
diec suspicious_file.bin # Automatically detects UPX, Themida, VMProtect, etc.
```

### Phase 4: Import / Export Analysis (IAT / EAT)

```bash
# Concept: Programs import functions from Windows DLLs to interact with the OS.
# The Import Address Table (IAT) is the list of requested functions.
# A small IAT (e.g., only LoadLibrary and GetProcAddress) is the #1 indicator of a packed file.

# Using Python Pefile to list imports:
```
```python
import pefile
pe = pefile.PE('suspicious_file.bin')
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    print(entry.dll.decode('utf-8'))
    for imp in entry.imports:
        print('\t', hex(imp.address), imp.name.decode('utf-8') if imp.name else '<ordinal>')
```
```bash

# Analyze capabilities based on imports:
# - Networking: WININET.dll (InternetOpen, InternetReadFile), WS2_32.dll (socket, connect)
# - Keylogging: USER32.dll (SetWindowsHookEx, GetAsyncKeyState)
# - Injection: KERNEL32.dll (VirtualAllocEx, WriteProcessMemory, CreateRemoteThread)
# - Anti-Debugging: KERNEL32.dll (IsDebuggerPresent, OutputDebugString)
```

### Phase 5: Resource Extraction

```bash
# Concept: Malware often hides secondary payloads (like drivers or the actual malicious shellcode)
# inside the Resource (.rsrc) section (Icon, Dialogs, Version Info).

# 1. List Resources
# pestudio or Resource Hacker (Windows GUI) are excellent for this.

# 2. Extract anomalous resources (e.g., a "binary" resource nested inside an Icon file)
# If extracted, repeat Phase 1-4 on the new binary.
```

## 🔵 Blue Team Detection & Defense
- **Yara Rules**: Use Yara to scan endpoints for specific PE byte sequences, imported API clusters, or hardcoded strings identified during static analysis.
- **Import Hashing (ImpHash)**: Calculate the MD5 hash of the malware's Import Address Table. Even if attackers change the code to alter the file's primary SHA256 hash, their ImpHash often remains identical, allowing immediate clustering of malware families.
- **Endpoint Detection**: EDR solutions hook into the precise Windows APIs (e.g., `CreateRemoteThread`) identified during IAT analysis to block process injection dynamically.

## Key Concepts
| Concept | Description |
|---------|-------------|
| PE File | Portable Executable; the standard file format for executables, object code, and DLLs in Windows |
| IAT | Import Address Table; maps function calls to their physical addresses in standard Windows DLLs |
| Packer | Software that compresses or encrypts a binary to avoid static detection, requiring it to unpack itself in memory |
| ImpHash | Import Hash; a unique fingerprint based on the specific order and combination of functions a PE imports |
| FLOSS | A reverse engineering tool that automatically decodes obfuscated strings statically |

## Output Format
```
Static Malware Analysis Triage
==============================
File: invoice_urgent.exe
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
File Type: PE32 executable (GUI) Intel 80386

Indicators of Compromise (IOCs):
- Packed: YES. Entropy of .text section is 7.5. IAT contains only LoadLibraryA and GetProcAddress. DetectItEasy flags 'UPX 3.96'.
- Suspicious Imports (Post-Deobfuscation via FLOSS):
  - VirtualAllocEx, WriteProcessMemory (Process Injection)
  - InternetOpenUrlA (C2 Command structure)
- Extracted Networking Strings:
  - hxxp://malicious-c2-domain[.]com/gate.php
  - Mozilla/5.0 (Windows NT 10.0; Win64; x64)

Summary Assessment: HIGHLY MALICIOUS. Dropper/Downloader masking as a document. Attempts process hollowing and reaches out to a hardcoded command server. Do not execute in production.
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
- Mandiant: [FLOSS String Deobfuscator](https://github.com/mandiant/flare-floss)
- PE Format Documentation: [Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format)
- PeStudio: [Static Triage Tool](https://www.winitor.com/)
