---
name: false-positive-killer
description: "Proof-based finding validation. Re-tests from clean state, compares responses, eliminates theoretical bugs, assigns confidence scores. Use BEFORE triage-validation to protect N/A ratio. NOT for report writing (use report-writing after this gate passes)."
---

# FALSE POSITIVE KILLER — Proof-Based Methodology

The goal is not to find vulnerabilities. The goal is to eliminate false positives and prove impact. A finding without proof is not a vulnerability.

## THE 10 GOLDEN RULES

### RULE 1: EVIDENCE FIRST
Never claim a finding until you can answer all four: What did you see (raw response)? How did you verify (exact command/tool)? What is the evidence (actual output)? Is there an alternative explanation (WAF, CDN, SPA catch-all, caching)?

Write evidence before conclusion. Example: "Observed `Access-Control-Allow-Origin: *` on endpoint X. Not yet proven that sensitive data is accessible. CORS wildcard present — impact pending browser PoC."

### RULE 2: CONFIDENCE LEVEL SYSTEM
| Level | Meaning | Action |
|-------|---------|--------|
| Confirmed | Reproduced from zero state, multiple signals, clear impact | Ready for triage |
| High | Strong evidence but one variable unverified | Improve and retest |
| Medium | Plausible but needs more testing | Investigate |
| Low | Single signal, could be coincidence | Do NOT report |
| False Positive | Proved wrong or harmless | Kill immediately |

Confirmed requires: reproduction steps + expected vs actual + impact. High requires: two independent signals + no alternative explanation.

### RULE 3: 200 OK ≠ LEAK — VALIDATE CONTENT
Single most common error. A 200 on /.git/config or /.env doesn't mean the file exists.
- Check Content-Type first: `text/html` = SPA catch-all (FP), `application/json` = real (check body), `text/plain` = investigate.
- If body starts with `<!DOCTYPE`, `<html>`, or contains SPA framework markers — it's a FALSE POSITIVE regardless of status code.
- .git/config REAL body: `[core]`, `repositoryformatversion`, `[remote "origin"]`. FALSE: `<html>`, React/Next/Vue bootstrap.

### RULE 4: CORS IS NOT A VULNERABILITY — PROVE IMPACT
Three-question gate: Does the endpoint return sensitive data? Are credentials supported (`access-control-allow-credentials: true`)? Can you read the response from a different origin (requires browser PoC, not curl)?

| Scenario | Verdict |
|----------|---------|
| `*` but no credentials + no sensitive data | Medium — misconfiguration |
| Specific origin but no sensitive data | Low — needs chain |
| `*` + credentials + sensitive data | High — confirmed |
| Only observed via curl, no browser PoC | Medium — not exploitable |

### RULE 5: JWT IS NOT A VULNERABILITY — ANALYZE FIRST
Decode → check expiry → check claims (sub, role, scope) → determine purpose (session token? anonymous analytics identifier? CSRF token? feature flag?) → assess sensitivity.

Anonymous analytics tokens (anonUserToken) with no auth value = INFO, not a leak.

### RULE 6: EXPLOIT BEFORE REPORTING
High/Critical findings must have: reproduction steps (prerequisites, exact request, expected result, actual result with evidence) + impact assessment (what can attacker do, realistic worst-case). Without this, severity is auto-downgraded one level.

### RULE 7: CORRECT SCANNING SEQUENCE
Recon → Fingerprinting → Asset Discovery → Endpoint Discovery → Parameter Discovery → Auth Mapping → Authorization Testing → Input Validation → Impact Validation → Report.
DO NOT JUMP TO EXPLOITATION BEFORE AUTH MAPPING.

### RULE 8: TWO-SIGNAL REQUIREMENT
Never report based on single signal alone:
- Status 200 alone ≠ .git leak (need body matching `[core]`)
- Header match alone ≠ CORS vuln (need sensitive data + credentials + browser PoC)
- Regex match alone ≠ JWT leak (need valid session + auth claims)

### RULE 9: SEVERITY RATING FRAMEWORK
Map impact to severity, not finding type to severity.
- Critical: ATO (proven), RCE (no auth), mass data access (1000+ records)
- High: IDOR with sensitive data, privesc (user→admin), auth bypass
- Medium: Stored XSS (realistic), CORS with PoC + data, business logic flaw
- Low: Missing security header, non-sensitive info disclosure, open redirect (no token leak)
- Info: Technology disclosure, JWT (anonymous/expired), CORS (no proven impact)

## PER-CLASS KILL TABLE

| Class | Kill Test |
|-------|-----------|
| SQLi (boolean) | `' OR 1=1--` ≠ `' OR 1=2--` → same page = WAF reflection, not SQLi |
| SQLi (time) | Baseline latency first, repeat 3x. Baseline also slow = network jitter |
| SSRF (blind) | DNS-only during render = link pre-fetch. Need HTTP hit from target's egress |
| IDOR | Confirm body is ANOTHER user's data, from fresh session/IP. CDN-cached copy = FP |
| Race condition | Check final ledger — 2x 200 but 1 recorded change = server serialized |
| Stored XSS | Must execute in victim context. Reflected-but-inert = FP |
| GraphQL | Introspection-on is often intended/Info. Bug only if per-field authz also broken |
| Rate limit | Confirm guessed value WORKED (login/OTP accepted). Cloudflare 200s ≠ app accepted |
| File upload | Fetch stored URL and prove EXECUTION, not storage. Displayed-as-text = FP |
| Open redirect | Low/Info unless it leaks auth token/OAuth code |
| JWT forgery | Send with NO token — still 200 = auth isn't JWT-based, not forgery bug |

Full per-class detail: `web2-vuln-classes/reference/false-positive-guidance.md`

## EVIDENCE SCHEMA LINK (NEW — record every kill)

Every decision (kill or confirm) must record:
```yaml
evidence_id: "OBS-NNN"
finding: "GET /api/orders IDOR candidate"
kill_reason: "WAF block_page on 3 payloads" | "same data A and B" | "unique constraint"
confidence: 0.3-1.0
stop_condition_met: "3 consecutive 403s" | "score < 40" | "intended behavior"
```

Kill reasons that trigger automatic path cancellation:
- "A and B sessions return identical data"
- "3 consecutive 403/401 with no bypass"
- "DB UNIQUE constraint violation"
- "Confirmed intended behavior in docs"
- "WAF block page on 3 different approaches"

## INTEGRATION

Load at START of any session. After confirmation, pass findings to `triage-validation` for 7-Question Gate. Only findings passing BOTH reach `report-writing`.

## FINAL GATE

Before any report: 1) Do I have at least two independent signals? 2) Have I ruled out alternative explanations (WAF, CDN, SPA, caching)? 3) Can I reproduce from zero state? If no to any → kill.
