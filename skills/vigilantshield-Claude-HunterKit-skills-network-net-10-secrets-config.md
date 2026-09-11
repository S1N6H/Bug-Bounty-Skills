---
name: net-10-secrets-config
sequence: net-10
category: infrastructure
domain: net
description: "Secret and config exposure: cloud credential files (~/.aws, ~/.azure), config files with embedded secrets, environment variable leakage, Docker/Compose secrets, and CI/CD credential exposure."
wordlist_ref: "wordlists/network/net-50-secrets-config/"
---

# Net 10 Secrets Config — Offensive Methodology

## Shortcut
1. Check cloud credential files: ~/.aws/credentials, ~/.azure/accessTokens.json
2. Check common config files: .env, config.json, config.yaml
3. Check Docker env: /proc/self/environ
4. Check CI/CD artifacts: .npmrc, .netrc, .git-credentials

## Detection
```bash
cat ~/.aws/credentials
cat ~/.azure/accessTokens.json
cat .env
cat /proc/self/environ
```


## Hacker Mindset

**Secrets exposure: cloud credentials files, .env, CI/CD artifacts, Docker env, git history.** One exposed .aws/credentials = full cloud account compromise.

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

**Wordlist**: `wordlists/network/net-50-secrets-config/` (2 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

