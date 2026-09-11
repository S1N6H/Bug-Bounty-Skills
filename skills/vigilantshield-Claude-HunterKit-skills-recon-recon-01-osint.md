---
name: recon-01-osint
sequence: recon-01
category: recon
domain: recon
description: "Comprehensive OSINT methodology: domain recon, email harvesting, social media profiling, GitHub/code leaks, Shodan/Censys enumeration, breach data, employee profiling, infrastructure mapping, cryptocurrency tracing, geospatial intelligence."
wordlist_ref: "wordlists/recon/recon-16-tech-fingerprint/"
---

# Recon 01 Osint — Offensive Methodology

## Shortcut
1. Start with domain → subdomains → IPs → technologies
2. Pivot to email → social media → employee profiles
3. Check breaches → GitHub leaks → paste sites
4. Scan infrastructure: Shodan, Censys, certificate transparency

## Hacker Mindset
**OSINT is about pivots.** One email leads to a social profile leads to a GitHub repo leads to credentials. Every artifact is a pivot point.

## Detection
```bash
# Subdomain discovery
subfinder -d target.com | tee subs
httpx -l subs -o alive

# Technology fingerprinting
nuclei -l alive -t technologies/

# GitHub leaks
gitdorker -d target.com -o output
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

**Wordlist**: `wordlists/recon/recon-16-tech-fingerprint/` (2 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

