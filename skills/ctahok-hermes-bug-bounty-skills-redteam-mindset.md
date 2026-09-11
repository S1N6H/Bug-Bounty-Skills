---
name: redteam-mindset
description: |
  Red team mindset and discipline for extended engagements. Covers authorization
  permanence, self-throttling anti-patterns, real-engagement cadence per live host,
  marker discipline, and the critical difference between red team and bug bounty
  testing.
triggers:
  - red team methodology
  - red team mindset
  - how to think like a red teamer
  - security assessment discipline
  - bug bounty vs red team
  - penetration testing mindset
category: security
---
# Red Team Mindset

Adapted from Claude-BugHunter by ElementalSouls.

---

## Core Philosophy

> **Red team scope = "gain access, prove impact". Bug bounty / WAPT scope = "find a bug, write a report".**

These produce DIFFERENT decisions at every blocker. Internalize the difference before starting.

---

## Primary Directive (Read Twice)

### Authorization is Permanent
- Authorization given at engagement start covers the entire engagement
- Do not insert mid-engagement permission gates
- Asking the user mid-loop after they chose a path is a stall, not a check

### Discipline Rules Are About Correctness, Not Throttling
- All discipline rules answer: "is this signal actually a finding?"
- None answer: "should I send the next probe?" — answer is always yes unless scope exhausted

### "Stop at PoC" Means Stop Escalating, Not Stop Testing
- Don't keep escalating class X after confirming impact
- But classes Y, Z, and the rest must still be tested

---

## Self-Throttling Anti-Patterns (Flag Immediately)

1. **Asking "want me to continue?"** mid-run after user chose full engagement — just continue
2. **Stopping at first-class-returning-401/403** — there are 12+ auth-bypass classes to try
3. **"Interesting constant token, not chased"** — constant tokens are LEADS, not artifacts
4. **Reading robots.txt and NOT reading Disallow lines** — every Disallow is a probe target
5. **Treating soft-404 as "noted"** — a 37KB body inside 404 status is leaking data
6. **"OpenAPI exposed → finding logged"** with only 4 of N endpoints probed — probe them all
7. **Volume framed as a problem** — 3,000 well-tagged requests is normal cadence
8. **Skill-gap-as-stop-condition** — if no skill exists for something, do it manually

---

## Real-Engagement Cadence (Per Live Host)

Before declaring a host complete, you must have done:

### Path Probe (Minimum)
```
/admin, /api, /login, /.git, /.env, /server-status, /swagger,
/openapi.json, /docs, /actuator, /healthz, /metrics, /debug,
/trace, /env, /heapdump, /threaddump, /robots.txt, /sitemap.xml,
/.well-known/*, common-CMS-paths
```

### Recon Checklist
- [ ] `robots.txt` content READ — every `Disallow` becomes a probe target
- [ ] `sitemap.xml` content READ — every entry becomes a probe target
- [ ] JS bundles harvested — grepped with FULL secret-regex catalogue (Firebase, AWS, GCP, JWT, Stripe, GitHub, high-entropy strings, route extraction)
- [ ] Source-map variant paths checked: `/*.js.map`, `/static/js/*.js.map`, `/_next/static/*.js.map`
- [ ] For every form: full SQLi marker-discipline sweep, auth-bypass sweep, CSRF, parameter pollution, mass-assignment, race condition
- [ ] For every API endpoint: HTTP method tampering, content-type tampering, JWT attacks, prototype pollution, race conditions
- [ ] For every SaaS tenant: vendor-specific check matrix

### If You've Done Less Than This Per Host, You Have Not Finished the Host

---

## Marker Discipline

**Marker discipline is about WHICH payloads (synthetic, identifiable, recoverable).**
**Never about HOW MANY** — hardened targets need MORE probes.

- Use unique markers per test to identify which parameter triggered a callback
- Always clean up test artifacts (created accounts, uploaded files, modified data)
- For SQLi, use BENCHMARK/SLEEP markers that don't modify data
- For blind XSS/SSRF, use unique subdomains per injection point

---

## Mindset Corrections

### The Blocker is Data, Not the Stop Sign
If a finding can't be reproduced on recheck, investigate the delta:
1. Original PoC artifacts are forever — capture BEFORE recheck
2. Diff the response — body size, headers, cookies, response time
3. The deployed mitigation is itself a finding (IR responsiveness)
4. Try alternative vectors
5. Document both states: "vulnerable at T0, mitigated at T0+30min"

**Never retract a finding on first reproducibility failure. Investigate why.**

### Sister-App Pattern Recognition
If you confirm a vulnerability on `/app-a/`:
- Same backend, same code template → `/app-b/`, `/app-c/`, `/app-d/` are all probable
- Test them with the SAME payload
- Also check: mobile API, partner API, internal API

### What-If Experiments
For every endpoint, ask:
- What if I change the HTTP method?
- What if I remove the auth header?
- What if I send duplicate parameters?
- What if I send negative numbers?
- What if I send extremely long values?
- What if I send special characters?
- What if I call this endpoint before the pre-requisite step?

---

## Red Team vs Bug Bounty Decision Matrix

| Decision Point | Red Team | Bug Bounty |
|---|---|---|
| Hygiene findings (EoL, missing headers) | Report as observation | KILL (not impact-demonstrated) |
| Recon data (subdomains, open ports) | Include in deliverable | Only if leads to real finding |
| "Could theoretically..." chains | Explore, try to exploit | KILL (no impact) |
| Chained vs individual findings | Report the chain | Report the chain (pays more) |
| Stop at PoC | Stop escalating, keep testing other classes | Stop escalating, move to validate |
| Engagement length | Extended (days/weeks) | Per-target (hours) |
