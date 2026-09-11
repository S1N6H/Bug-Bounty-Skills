---
name: recon-05-openapi-enum
sequence: recon-05
category: recon
domain: recon
description: "OpenAPI/Swagger enumeration: spec file discovery, endpoint extraction, parameter identification, auth scheme detection, and API surface mapping from spec files."
wordlist_ref: "wordlists/recon/recon-32-openapi-active-enum/"
---

# Recon 05 Openapi Enum — Offensive Methodology

## Shortcut
1. Probe for spec files: /swagger.json, /openapi.json, /api-docs
2. Parse discovered spec for all endpoints, methods, parameters
3. Identify auth schemes per endpoint
4. Map unauthenticated endpoints as attack surface

## Detection
```bash
# Spec discovery
curl -s https://target.com/swagger.json -o /dev/null -w "%{http_code}"
curl -s https://target.com/openapi.json -o /dev/null -w "%{http_code}"
curl -s https://target.com/api/docs -o /dev/null -w "%{http_code}"

# Parse spec
curl -s https://target.com/openapi.json | jq '.paths | keys'
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

**Wordlist**: `wordlists/recon/recon-32-openapi-active-enum/` (15 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

