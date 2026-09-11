---
name: recon-02-osint-methodology
sequence: recon-02
category: recon
domain: recon
description: "Structured OSINT methodology framework: target definition, source selection, collection workflows, data correlation, timeline reconstruction, and reporting for systematic OSINT campaigns."
wordlist_ref: "wordlists/recon/recon-17-js-analysis/"
---

# Recon 02 Osint Methodology — Offensive Methodology

## Shortcut
1. Define target scope (domain, org, person, crypto, geo)
2. Select categories based on scope
3. Work top-down; pivot on discovered artifacts
4. Log findings with URL + timestamp + screenshot

## Hacker Mindset
**Methodology beats tools.** Having every OSINT tool means nothing without a workflow. Follow the data, not the tool list.

## Detection
```python
# JS endpoint extraction
cat bundle.js | grep -oP '"[^"]*api[^"]*"' | sort -u
```
## Chaining & Escalation

Chain this finding with others for higher impact. Combine low-severity findings into critical attack chains. Always think: what's the next step after this works?

## OOB Detection & Blind Confirmation

Use Burp Collaborator or Interactsh for blind detection. Always set up OOB before firing payloads. Time-based: inject sleep(5) and measure response delay.

## Bypass Techniques

| Filter/Block | Bypass |
|-------------|--------|
| WAF/Input validation | Encoding, case variation, alternative syntax |
| Rate limiting | IP rotation via X-Forwarded-For, endpoint mirror |
| Blacklist | Alternative syntax, polyglot payloads |

## Tools

- Burp Suite
- curl / httpx
- Nuclei templates
- Custom Python scripts

## Wordlist Invocation

**Wordlist**: `wordlists/recon/recon-17-js-analysis/` (1 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

