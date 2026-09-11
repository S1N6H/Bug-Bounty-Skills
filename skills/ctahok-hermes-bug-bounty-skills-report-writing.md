---
name: report-writing
description: |
  Bug bounty and security report writing methodology. Templates for HackerOne,
  Bugcrowd, Intigriti, and Immunefi. CVSS 3.1 scoring, severity decision guide,
  evidence hygiene, and report quality checklist.
triggers:
  - write a security report
  - report this finding
  - how to report a bug
  - security report template
  - bug bounty report
  - cvss scoring
  - write up finding
category: security
---
# Security Report Writing

Adapted from Claude-BugHunter by ElementalSouls.

---

## Core Philosophy

> **Impact-first. Human tone. No theoretical language. Triagers are people.**

### The Most Important Rule
> **Never use "could potentially" or "could be used to" or "may allow".**
> Either it does the thing or it doesn't. If you haven't proved it, don't claim it.

```
BAD:  "This vulnerability could potentially allow an attacker to access user data."
GOOD: "An attacker can access any user's order history by changing the user_id
       parameter to the target user's ID. I confirmed this using two test accounts:
       attacker@test.com successfully retrieved victim@test.com's orders,
       including their shipping address and payment method last 4 digits."
```

---

## Title Formula

```
[Bug Class] in [Exact Endpoint/Feature] allows [attacker role] to [impact] [victim scope]
```

### Good Titles (Specific, Impact-First)
- `IDOR in /api/v2/invoices/{id} allows authenticated user to read any customer's invoice data`
- `Missing auth on POST /api/admin/users allows unauthenticated attacker to create admin accounts`
- `Stored XSS in profile bio field executes in admin panel — allows privilege escalation`
- `SSRF via image import URL parameter reaches AWS EC2 metadata service`
- `Race condition in coupon redemption allows same code to be used unlimited times`

### Bad Titles (Vague, Useless to Triager)
- `IDOR vulnerability found`
- `Broken access control`
- `XSS in user input`
- `Security issue in API`
- `Unauthorized access to user data`

---

## Report Structure

### Summary (1 Paragraph)
What the bug is, where it is, what an attacker can do.
Include: endpoint, method, parameter, data exposed, required access level.

### Vulnerability Details
- **Type:** OWASP category / bug class
- **CVSS 3.1 Score:** e.g., `6.5 (Medium) — AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`
- **Affected Endpoint:** Exact URL + method

### Steps to Reproduce
```
**Environment:**
- Attacker account: attacker@test.com
- Victim account: victim@test.com (ID: 456)
- Target: https://app.target.com

**Steps:**
1. Log in as attacker@test.com, obtain Bearer token
2. Send GET request to /api/v2/users/456/profile
3. Observe response contains victim's email, phone, and address
```

### Impact
Quantified and specific:
- What data is exposed / what action is possible
- How many users affected
- What an attacker can do with this

### Remediation Recommendation
1-2 sentences of concrete fix (not generic).

### Supporting Materials
- Screenshots with sensitive data redacted
- HTTP request/response (copy-paste ready)
- Video for complex chains (Intigriti prefers this)

---

## CVSS 3.1 Quick Scoring

### Typical Scores by Bug Class

| Bug | Typical CVSS | Severity |
|---|---|---|
| IDOR (read PII) | 6.5 | Medium |
| IDOR (write/delete) | 7.5 | High |
| Auth bypass → admin | 9.8 | Critical |
| Stored XSS (any user) | 5.4–8.8 | Med–High |
| SQLi (data exfil) | 8.6 | High |
| SSRF (cloud metadata) | 9.1 | Critical |
| Race condition (double spend) | 7.5 | High |
| GraphQL auth bypass | 8.7 | High |
| JWT none algorithm | 9.1 | Critical |
| RCE confirmed | 9.8–10.0 | Critical |
| ATO without interaction | 9.1 | Critical |
| MFA bypass (OTP brute) | 7.5 | High |
| File upload → RCE | 9.8 | Critical |

### Severity Decision Guide

**Critical (P1):**
- Full ATO of any user without interaction
- Remote code execution
- SQLi with ability to dump/modify entire DB
- Auth bypass to admin panel
- SSRF to cloud metadata → IAM credentials exfil

**High (P2):**
- Mass PII exposure (email, phone, SSN, payment data)
- Privilege escalation from user to admin
- SSRF reaching internal services (data returned)
- Stored XSS executing for all users of sensitive feature
- Payment bypass / financial loss without limit

**Medium (P3):**
- IDOR on specific user's non-critical data
- Reflected XSS on sensitive page requiring user interaction
- CSRF on sensitive action with clear impact
- Subdomain takeover with demonstrated impact

**Low (P4) / Informational:**
- Missing security headers
- Internal IP disclosure
- Stack traces in debug mode
- Clickjacking on non-sensitive pages

---

## Evidence Hygiene

### What Must Be Redacted
- Session cookies (`authn`, `session`, `sid`, `__Secure-id`)
- `Authorization` headers (Bearer tokens, JWT)
- `Cookie` request header values for session-bearing cookies
- Other users' PII (names, emails, phones, addresses)
- Your CSRF tokens bound to your session

### What to Leave Visible
- Trace IDs (`x-datadog-trace-id`, `x-request-id`)
- Server / framework headers
- Field existence and shape in JSON
- Your test account UID/email
- Endpoint URL and HTTP method
- Response body shape (with PII values blanked)

### Redaction Protocol
1. Before screenshotting: collapse Network panel headers, hide Burp's Request panel
2. After screenshotting: search for cookie name substring → black-bar if present
3. For response body PII: replace values with empty strings or [REDACTED]

### HAR File Sanitization
```bash
# Remove cookies and auth headers from HAR files
cat export.har | jq '
  .log.entries |= map(
    (.request.headers |= map(
      if .name | ascii_downcase | IN("cookie","authorization","x-csrf-token")
      then .value = "" else . end
    )) |
    (.response.headers |= map(
      if .name | ascii_downcase | IN("set-cookie")
      then .value = "" else . end
    ))
  )
' > export.sanitized.har
```

---

## Platform-Specific Templates

### HackerOne
```
## Summary
[One paragraph: bug, location, impact, required access level]

## Vulnerability Details
**Type:** [Bug class]
**CVSS 3.1 Score:** [Score] — [Vector]
**Affected Endpoint:** [Method] [URL]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Impact
[What attacker can do, quantified]

## Recommended Fix
[1-2 sentences]

## Supporting Materials
[Screenshot/video]
```

### Bugcrowd
- **Required:** VRT Category (e.g., `Broken Access Control > IDOR > P2`)
- **Required:** Expected vs Actual Behavior section
- **Required:** Severity Justification paragraph
- Structured, less narrative than H1

### Intigriti
- Title: `[Bug Class]: [One-line impact]`
- **PoC video valued much more than screenshot** — record with Loom
- CVSS 3.1 or 4.0 standard

### Immunefi
- **PoC-first** — working Foundry/Hardhat code is primary deliverable
- Economic impact with numbers: "attacker can drain $X in Y transactions"
- Contract, function, root cause with code snippet

---

## Report Quality Checklist

Before submitting:
- [ ] Title follows formula: [Bug Class] in [Endpoint] allows [actor] to [impact]
- [ ] Steps to Reproduce: copy-pasteable HTTP request
- [ ] Evidence: screenshot/video of actual impact (not just 200 status)
- [ ] Severity matches CVSS 3.1 score AND program's severity definitions
- [ ] Remediation: 1-2 sentences of concrete fix
- [ ] NEVER used "could potentially" or "may allow"
- [ ] PII and session cookies redacted from evidence
- [ ] Test account password rotated after submission
