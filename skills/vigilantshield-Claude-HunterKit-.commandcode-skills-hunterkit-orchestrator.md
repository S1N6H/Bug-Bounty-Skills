---
name: claude-hunterkit-orchestrator
description: "Master orchestrator for claude-hunterKit — 148 offensive security skills. RED TEAM recon-first pipeline: deep recon → decision matrix → targeted exploit → chain & escalate. 31 escalation paths, 8 stop conditions."
---

# claude-hunterKit Orchestrator — RED TEAM MODE

Recon-first conditional agent launch pipeline for 148 offensive security skills.

## RED TEAM MINDSET

Every finding is a PRIMITIVE, not a report entry.
- XSS = session hijack vector
- SQLi = database exfil pipeline
- SSRF = cloud metadata extraction tunnel
- JWT = admin access via alg:none

Chain LOW/MEDIUM primitives into CRITICAL impact.

## Pipeline

```
PHASE 0: Categorize target → route to domain orchestrator
PHASE 1a: Network/Stack recon (recon-01,02,03)
PHASE 1b: Surface mapping (recon-04,05,06)
PHASE 1c: Defense analysis (recon-07,08,09,10,11)
PHASE 2: Consult recon-decision-matrix.yaml → match 40+ signals → select agents
PHASE 3: Targeted exploit on matched skills (confirm → escalate → exfil)
PHASE 4: Chain & escalate via 31 escalation paths
PHASE 5: Report findings — impact-first, chain-primitive
```

**Cardinal rule:** Complete ALL of Phase 1 before launching ANY vuln agent.

## Stop Conditions (call these DONE)

- full_account_takeover_confirmed
- pii_breach_>_1000_records
- rce_confirmed_on_production
- cloud_iam_keys_extracted
- internal_network_pivot_confirmed
- database_dump_completed
- admin_privilege_escalation_confirmed
- source_code_repository_accessed

## Domain Routing

| Target Type | Directory | Launch Strategy |
|-------------|-----------|----------------|
| Web app | skills/web/_orchestrator/ | Phase 1 recon → decision matrix → 51 web skills |
| API | skills/api/_orchestrator/ | Phase 1 recon → signal-to-agent → 35 API skills |
| AI/LLM | skills/ai/ | Start with ai-02 for endpoint discovery → 24 skills |
| Network/Infra | skills/network/ | Start with net-01 or net-04 → 21 skills |
| Cloud | skills/cloud/ | Use cloud-02 for full depth → 2 skills |
| Auth | skills/auth/_orchestrator/ | Phase 1 auth recon → matched scheme → 3 skills |
| Recon | skills/recon/ | 11 recon skills — run all before deciding |
| Bug Bounty | bugbounty/bugbounty-master/ | Full workflow from recon to report |

## Decision Matrix

`skills/_hunter/recon-decision-matrix.yaml` contains 40+ signal rules mapping recon findings to specific vuln agents. Launch ONLY agents whose signals match. 31 escalation paths for chaining primitives into critical impact.

## Key Attack Chains

```
SQLi → RCE (web-37) → internal pivot
SSRF → Cloud metadata (cloud-01) → IAM keys
XSS → Session hijack (web-12) → OAuth theft → ATO
JWT → alg:none → Admin access → User enum
IDOR → BOLA (api-04) → Mass data exposure
GraphQL introspection → Schema dump → Auth bypass
File Upload → Webshell → RCE
Prompt Injection → System prompt leak → API keys
```

## Quick Reference

```bash
# List all skills in a domain
ls skills/web/
ls skills/api/

# Read recon decision matrix
cat skills/_hunter/recon-decision-matrix.yaml

# Check escalation paths
grep "from:" skills/_hunter/recon-decision-matrix.yaml

# Search for a vuln class
grep -rl "ssrf" skills/*/SKILL.md
```
