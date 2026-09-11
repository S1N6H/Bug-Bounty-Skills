---
name: net-12-cicd
sequence: net-12
category: infrastructure
domain: net
description: "CI/CD pipeline security: GitHub Actions, GitLab CI, Jenkins — pipeline injection, artifact poisoning, secret exposure in build logs, self-hosted runner abuse, and deployment script manipulation."
wordlist_ref: "wordlists/network/net-53-cicd-pipeline/"
---

# Net 12 Cicd — Offensive Methodology

## Shortcut
1. Check Jenkins on 8080 (unauthenticated access, script console)
2. Check GitLab CI runner registration tokens
3. Check GitHub Actions for workflow injection
4. Check build artifacts for secrets

## Detection
```bash
# Jenkins unauthenticated
curl http://target.com:8080/script

# GitLab runner token
cat /etc/gitlab-runner/config.toml

# GitHub Actions inspect
# Check .github/workflows/*.yml for script injection
```


## Hacker Mindset

**CI/CD pipeline attacks: workflow injection via pull_request_target, self-hosted runner poisoning, OIDC trust abuse, artifact secret leakage.** Supply chain is the new frontier.

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

**Wordlist**: `wordlists/network/net-53-cicd-pipeline/` (1 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

