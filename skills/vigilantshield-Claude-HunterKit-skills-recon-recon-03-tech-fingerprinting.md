---
name: recon-03-tech-fingerprinting
sequence: recon-03
category: recon
domain: recon
description: "Technology fingerprinting: web server detection, framework identification, CMS detection, WAF identification, load balancer detection, and version enumeration via response analysis."
wordlist_ref: "wordlists/recon/recon-16-tech-fingerprint/"
---

# Recon 03 Tech Fingerprinting — Offensive Methodology

## Shortcut
1. Send baseline request to target
2. Analyze response headers (Server, X-Powered-By, Set-Cookie)
3. Probe known paths for frameworks (/wp-admin, /laravel, /api/docs)
4. Check WAF via known bypass payloads

## Detection
```bash
# Server header
curl -sI https://target.com | grep -i '^server:\|^x-powered-by:\|^set-cookie:'

# Framework paths
curl -s https://target.com/wp-admin/ -o /dev/null -w "%{http_code}"
curl -s https://target.com/.env -o /dev/null -w "%{http_code}"
```


## Hacker Mindset

**Default mindset for skills without specific template.** Every security boundary is a hypothesis. Test it. If it breaks, that's the finding. Always escalate from single finding to chain.

## Chaining & Escalation

Chain this finding with others for higher impact. Combine low-severity findings into critical attack chains. Always think: what's the next step after this works?

## OOB Detection & Blind Confirmation

Use Burp Collaborator or Interactsh for blind detection. Always set up OOB before firing payloads. Time-based: inject sleep(5) and measure response delay.

## Bypass Techniques

| Filter/Block | Bypass |
|-------------|--------|
| WAF block | Encoding, case variation, comment injection |
| Input sanitization | Double encoding, Unicode, null bytes |
| Rate limiting | X-Forwarded-For rotation, HTTP/2 multiplex |
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

