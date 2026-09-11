---
name: domain-scoped-hunting
description: "Discipline layer for ANY vuln hunt — the part our knowledge skills lack. Load AFTER you have selected a specific vuln domain (SQLi, IDOR, SSRF, business logic...). Forces: Domain declaration → Boundaries → Pivot Hints (where to go when blocked) → Exit Evidence (positive needs verified proof; negative needs min_attempts + honest 'not found under current evidence' language). Anti-fabrication: fingerprints/CVEs are never evidence of exploitability. NOT a knowledge reference (use web2-vuln-classes / business-logic-hunter for WHAT to test) — this is HOW to stay disciplined while hunting."
---

# DOMAIN-SCOPED HUNTING — DISCIPLINE LAYER

Adapted from VulnClaw's redteam-*-detail-pack structure (Domain → Boundaries → Pivot Hints → Exit Evidence). Every vuln-hunt skill we own tells you WHAT to test. This one governs HOW you stay inside the domain, where to pivot when blocked, and — critically — when and how you are ALLOWED to exit. Load only after a vuln domain is already selected.

## 1. DECLARE THE DOMAIN (30 seconds, mandatory)

Write one line: the exact vuln class you are hunting, its variants, and its allowed test surface.

```
DOMAIN: SQLi (union | boolean-blind | time-blind | error-based | stacked | second-order)
SURFACE: <target> — only this host/app/codebase
VARIANTS IN SCOPE: <list>
VARIANTS OUT OF SCOPE: <list — e.g. no OOB exfil if no collaborator>
```

If you cannot write this line, you have NOT selected a domain — go back to routing. Do not "hunt generally."

## 2. BOUNDARIES (hard rules — violate = abort this hunt)

- Never exceed the current target, host, IP, app, or codebase boundary.
- No destructive actions (DROP/TRUNCATE/delete data) unless the program explicitly authorizes them.
- No fabrication: never invent, exaggerate, or "complete" evidence that does not exist.
- Never declare task complete without evidence.
- Fingerprint of a component / public CVE / library version ≠ exploitable vulnerability. It is a candidate, never a finding.
- Missing authorization paperwork must NOT block planning — use a TARGET placeholder and continue; do not stall asking for auth docs you were already given.
- No brute-force / credential spraying inside a recon-class domain.

## 3. PIVOT HINTS (when blocked — the money section)

Do NOT repeat the same failed payload variant. Escalate through these ladders instead:

| Blocked by | Pivot ladder |
|---|---|
| WAF / keyword filter | encoding bypass (double URL-encode, Unicode) → comment splitting (`/**/`) → case mixing → inline comments → then change position |
| Input point refuses injection | move payload to OTHER positions: headers (X-Forwarded-For, User-Agent), cookies, JSON fields, path segments |
| All entry points clean | fall back to parent knowledge base and re-route the whole test direction (you may be in the wrong domain) |
| Rate limited | slow down → rotate UA → switch tool → continue, do not brute-force the limit |
| Direct connection blocked | historical DNS, mail headers, certificate transparency for the real origin IP |

The universal ladder: `encoding → position change → parameter change → different technique → fall back to parent`. Track which rung you are on; never camp on rung 1.

## 4. EXIT EVIDENCE — the part that kills false positives

### Positive exit (claiming the vuln is real) — REQUIRED:
- **verified-level evidence** for: the vulnerability being real, its impact, and anything going into a report.
- **supported-level evidence** for key conclusions.
- Artifact must state: source, target, time, observation, and the judgment basis.

Per-vuln-class reproduction artifacts must include:
- The COMPLETE request (with the exact payload) — copy-paste, not paraphrase.
- The corresponding response (the marker that proves success: leaked data / error / time delta).
- Variant label (e.g. union / boolean-blind) + one-line impact statement.

### Negative exit (no vuln found) — REQUIRED:
- Minimum attempts for a negative result: **3** (distinct techniques, not 3x the same payload).
- Record the paths tried + why each failed.
- Output **"not found under current evidence"** — NEVER "confirmed not vulnerable." Absence of proof is not proof of absence.

### Anti-hallucination gate (from VulnClaw constraint_policy + evidence pipeline):
A claimed finding is ONLY valid if its marker appears **verbatim** in the tool/request output you actually captured. If the evidence is paraphrased, reconstructed, or "the server would have..." — it is not evidence. Kill it.

## 5. DOMAIN COMPLETION CHECKLIST

Before leaving a domain (positive or negative):
- [ ] Domain line declared at start
- [ ] Boundaries respected (no scope creep, no destructive ops)
- [ ] Pivot ladder used — at least one rung change when blocked
- [ ] Positive: verified evidence artifact (request+response+marker) exists
- [ ] Negative: ≥3 distinct attempts, paths recorded, "not found under current evidence" language used
- [ ] No fingerprint/CVE claimed as vulnerability
- [ ] Next domain OR parent re-route decision recorded

## CROSS-REF
- Knowledge (WHAT to test): `web2-vuln-classes`, `business-logic-hunter`, `api-security`
- Finding gates (after this): `false-positive-killer` → `triage-validation` → `report-writing`
- Model building (before this): `application-model-builder`
- Multi-account discipline: always compare two+ accounts (A/B) to surface authorization gaps
- Evidence schema: log every observation as request/response pairs (see `false-positive-killer`)
