---
name: triage-validation
description: |
  The 7-Question Gate — kill bad findings before they waste everyone's time.
  Pre-submission triage, dedup checks, never-submit list, CVSS scoring guidance.
  Every candidate finding runs through this before any report is drafted.
triggers:
  - is this finding valid
  - should I submit this
  - triage this finding
  - validate this bug
  - check if this is a real bug
  - what severity is this
category: security
---
# Triage & Validation — The 7-Question Gate

## Core Principle
> **"One wrong answer = STOP this finding. Kill the finding. Move on to the next test class."**

This skill kills INDIVIDUAL FINDINGS, not the engagement. All other test classes remain pending.

> "N/A hurts your validity ratio. Informative is neutral. Only submit what passes all 7 questions."

---

## The 7-Question Gate (Ask in order, one wrong = STOP)

### Q1: Can an attacker use this RIGHT NOW, step by step?

Complete this template:
```
1. Setup: I need [own account / another user's ID / no account]
2. Request: [exact HTTP method, URL, headers, body — copy-paste ready]
3. Result: I can [read / modify / delete] [exact data shown in response]
4. Impact: The real-world consequence is [account takeover / PII read / money stolen]
5. Cost: Time: [X minutes], Capital: [$0 / $X subscription required]
```

**If you CANNOT write step 2 as a real HTTP request → KILL IT.**

### Q2: Is the impact on the program's accepted impact list?

Common tiers:
- **Critical**: Any-user ATO without interaction, RCE, SQLi with data exfil, admin auth bypass
- **High**: Mass PII exfil, privilege escalation, internal SSRF with data, stored XSS all users
- **Medium**: IDOR on specific user non-critical data, XSS on sensitive page requiring click
- **Low**: Non-sensitive info disclosure, clickjacking with PoC

**If your bug maps to a listed exclusion → KILL IT.**

### Q3: Is the root cause in an in-scope asset?

Confirm:
- Domain on in-scope list (not `*.internal.target.com`)
- Production asset (not staging/dev unless explicitly in scope)
- Not third-party service (not Stripe, Salesforce, Google Auth)

**If out-of-scope → KILL IT.**

### Q4: Does it require privileged access an attacker can't realistically get?

- "Admin can do X" = centralization risk = **KILL IT** (99% of programs)
- "Non-admin can do X that only admin should do" = valid
- Requires physical access / MFA device = usually invalid
- Requires compromised victim account = questionable, low severity

### Q5: Is this already known or accepted behavior?

Search:
1. Program's disclosed reports: Ctrl+F endpoint name + bug class
2. GitHub issues: `is:issue label:security ENDPOINT_NAME`
3. Changelog / CHANGELOG.md
4. API docs / design docs

**If acknowledged/design decision → KILL IT.**

### Q6: Can you prove impact beyond "technically possible"?

- XSS → show actual cookie theft/session hijack, not just `alert(1)`
- SSRF → hit internal endpoint returning data, not just DNS ping
- SQLi → show actual data exfil from real table, not just error message
- IDOR → show actual other-user's data, not just 200 status

**If only "technically possible" → DOWNGRADE severity, not kill.**

### Q7: Is this a known-invalid bug class?

Check NEVER SUBMIT list below. If on list without chain → **KILL IT.**

---

## NEVER SUBMIT LIST (Submitting these destroys your validity ratio)

- Missing CSP / HSTS / security headers
- Missing SPF / DKIM / DMARC
- GraphQL introspection alone (no auth bypass, no IDOR demonstrated)
- Banner / version disclosure without working CVE exploit
- Clickjacking on non-sensitive pages (no sensitive action PoC)
- Tabnabbing
- CSV injection (no actual code execution shown)
- CORS wildcard (*) without credential exfil proof of concept
- Logout CSRF
- Self-XSS (only exploits own account)
- Open redirect alone (no ATO or OAuth theft chain)
- OAuth client_secret in mobile app (known, expected)
- SSRF DNS callback only (no internal service access or data)
- Host header injection alone (no password reset poisoning chain)
- Rate limit on login/contact/search (Cloudflare covers it)
- Information disclosure of non-sensitive data (public emails, job titles)
- Reflected XSS requiring user to type malicious input (paste XSS)
- Mixed content warnings (no data intercepted)
- Missing cookie flags (Secure/HttpOnly) without demonstrated session theft
- Username enumeration via timing (controversial, most programs reject)
- Directory listing on non-sensitive directories
- OPTIONS/TRACE methods enabled (no demonstrated impact)
- TLS configuration issues (weak ciphers, old protocols) unless specifically in scope

### Conditional Kill (Chain Required)

These are not submittable alone, but CAN be chained:
- Open redirect → OAuth code theft → ATO = **report the chain**
- SSRF DNS → internal service access with data returned = **report the chain**
- CORS wildcard → credentialed data exfil PoC = **report the chain**
- Host header injection → password reset poisoning = **report the chain**

If you can't build the chain today → **KILL IT.**

---

## 4 Pre-Submission Gates (ALL 4 must PASS)

### Gate 0: Reality Check (30 seconds)
- [ ] Bug is REAL — confirmed with actual HTTP requests, not code reading alone
- [ ] Bug is IN SCOPE — checked program scope page explicitly
- [ ] Reproducible from scratch — can reproduce starting from fresh session
- [ ] Evidence ready — screenshot, response body, or video

### Gate 1: Impact Validation (2 minutes)
- [ ] Can answer: "What can attacker DO that they couldn't before?"
- [ ] Answer is more than "see non-sensitive data" (unless program pays for info disclosure)
- [ ] Real victim: another user's data, company's data, financial loss
- [ ] Not relying on victim doing something unlikely

### Gate 2: Deduplication Check (5 minutes)
- [ ] Searched HackerOne Hacktivity for this program + similar bug title/endpoint
- [ ] Searched GitHub issues for target repo
- [ ] Read most recent 5 disclosed reports for this program
- [ ] Not a "known issue" in their changelog or public docs
- [ ] Google: "TARGET_NAME ENDPOINT_NAME bug bounty"

### Gate 3: Report Quality (10 minutes)
- [ ] Title: [Bug Class] in [Endpoint] allows [actor] to [impact]
- [ ] Steps to Reproduce: copy-pasteable HTTP request
- [ ] Evidence: screenshot/video of actual impact (not just 200 status)
- [ ] Severity: matches CVSS 3.1 score AND program's severity definitions
- [ ] Remediation: 1-2 sentences of concrete fix
- [ ] NEVER used "could potentially" or "may allow"

---

## CVSS 3.1 Quick Scoring

### Typical Scores by Bug Class

| Bug | Typical CVSS | Severity |
|-----|-------------|----------|
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

**Critical (P1)**
- Full account takeover of any user without interaction
- Remote code execution
- SQLi with ability to dump/modify entire DB
- Auth bypass to admin panel
- SSRF to cloud metadata → IAM credentials exfil

**High (P2)**
- Mass PII exposure (email, phone, SSN, payment data)
- Privilege escalation from user to admin
- SSRF reaching internal services (data returned)
- Stored XSS executing for all users of sensitive feature
- Payment bypass / financial loss without limit

**Medium (P3)**
- IDOR on specific user's non-critical data
- Reflected XSS on sensitive page requiring user interaction
- CSRF on sensitive action with clear impact
- Subdomain takeover with demonstrated impact

**Low (P4) / Informational**
- Missing security headers
- Internal IP disclosure
- Stack traces in debug mode
- Information disclosure of non-sensitive data
- Clickjacking on non-sensitive pages
