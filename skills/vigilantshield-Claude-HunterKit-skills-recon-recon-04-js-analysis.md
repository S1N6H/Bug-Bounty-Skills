---
name: recon-04-js-analysis
sequence: recon-04
category: recon
domain: recon
description: "JavaScript analysis for recon: endpoint extraction from JS bundles, API key hunting, secret scanning in source maps, and hidden parameter discovery from client-side code."
wordlist_ref: "wordlists/recon/recon-17-js-analysis/"
---

# Recon 04 Js Analysis — Offensive Methodology

## Shortcut
1. Gather all JS files from target (subdomain + paths)
2. Extract endpoints: grep for paths, URLs, routes
3. Extract secrets: API keys, tokens, internal URLs
4. Check source maps (.js.map) for full source code

## Detection
```bash
# Extract all JS URLs
katana -u https://target.com -jc | grep '\.js' | sort -u > js_files

# Extract endpoints
cat *.js | grep -oP '["''']/[a-zA-Z0-9_/{}.-]+["''']' | sort -u

# Source maps
curl -s https://target.com/app.js.map | python3 -c "import sys,json; d=json.load(sys.stdin); print('\n'.join(d.get('sources',[])))"
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

**Wordlist**: `wordlists/recon/recon-17-js-analysis/` (1 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

