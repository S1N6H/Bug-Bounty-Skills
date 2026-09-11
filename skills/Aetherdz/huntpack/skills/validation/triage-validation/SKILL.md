---
name: triage-validation
description: "Finding validation before report writing — 8-Question Gate, kill signals, never-submit list, chain table, CVSS ref. Use BEFORE any report. One wrong answer = kill. Protects N/A ratio."
---

# TRIAGE & VALIDATION

> One wrong answer = STOP. Kill it. N/A hurts your ratio.

## THE 8-QUESTION GATE

**Q1: Can attacker use this RIGHT NOW?** Fill: Setup → exact HTTP request → Result → Impact → Cost. Can't write a real request? → KILL.

**Q2: Impact on program's accepted list?** If exclusion → KILL.

**Q3: Root cause in-scope?** Production, not *.internal, not third-party. OOS → KILL.

**Q4: Requires unrealistic privileged access?** "Admin can do X" = centralization risk = KILL. Non-admin doing admin stuff = valid.

**Q5: Already known/accepted?** Search H1/Bugcrowd disclosed, GitHub, changelog. Design decision → KILL.

**Q6: Prove impact beyond "technically possible"?** SSRF → internal data, not DNS. SQLi → tables, not error. IDOR → other user's data, not 200. XSS → cookie theft, not alert(1). "Technically possible" only → DOWNGRADE.

**Q7: Known-invalid bug class?** Check NEVER SUBMIT list below. On list without chain → KILL.

**Q8: Identity check (auth findings only)?** IDOR works with A's session reading B's data (if no-auth reads → missing auth, not IDOR). Priv-esc low→high. Both sessions see same → no bug.

## NEVER SUBMIT (standalone)
Missing CSP/HSTS/SPF/DKIM/DMARC | GraphQL introspection alone | Banner/version without CVE | Clickjacking non-sensitive | Tabnabbing | CSV injection no RCE | CORS `*` without credential exfil | Logout CSRF | Self-XSS | Open redirect alone | OAuth client_secret in mobile app | SSRF DNS-only | Host header alone | Rate limit non-critical | Session not invalidated | Concurrent sessions | Internal IP error | Mixed content | SSL weak ciphers | Pre-account takeover.

## KILL SIGNALS
Reflected XSS w/ CSP blocking | SSRF DNS-only | IDOR own data | SQLi error-only | CORS `*` w/o credentials | Rate limit non-sensitive | Nuclei info template no PoC | MFA rate limit | Open redirect no OAuth | Auth bypass needs admin | XSS `alert(document.domain)` | SAML metadata no key

## CHAIN REQUIRED
Open redirect + OAuth redirect_uri → ATO | Clickjacking + sensitive action → Med | CORS wildcard + credentialed PII → High | CSRF + transfer/change email → High | Rate limit bypass + OTP brute → Med/High | SSRF DNS-only + internal data → Med | Host header + password reset → High | Prompt injection + IDOR → High | S3 listing + API keys → Med/High | Self-XSS + CSRF → Med | Subdomain takeover + OAuth → Critical | GraphQL introspection + auth bypass mutation → High

## EVIDENCE GATE (NEW — must have this before validation)
Every finding MUST have at least one evidence entry from the shared schema:
```yaml
evidence_id: "OBS-NNN"
type: "request"|"response"|"diff"
signal: specific observation (e.g., "user_b data in user_a response")
action: exact curl/request used
expected: what should happen
actual: what happened
confidence: 0.3-1.0
reproducible: true|false
```
No evidence entry → finding fails Q1 automatically → KILL.

## CVSS FAST (3.1 — CVSS 4.0 uses different metrics: CVSS 4.0 replaces AC/AV with new vectors, adds supplemental metrics. Use NIST NVD calculator or `cvss4.js` for 4.0.)
AV:Network=6.2→AC:Low=1.0→PR:None=0.85/Low=0.62/High=0.27→UI:None=0.85/Req=0.62→C:H=0.56/L=0.22→I:H=0.56/L=0.22→A:H=0.56/L=0.22→S:Unchanged=1.0/Changed=1.04 → Score = round(1.08×AV×AC×PR×UI×S × min(C×I×A×1.08, 10))

## KILL FAST
Can't fill Q1 in 5min → kill | >2 preconditions → kill | Nothing tangible → kill | Admin can do X → kill | Documented → kill | 30min no PoC → kill | No evidence_id → kill
