---
name: net-07-serverless
sequence: net-07
category: infrastructure
domain: net
description: "Serverless security (AWS Lambda, Azure Functions, GCP Cloud Functions): event injection, environment variable theft, cold start bypass, function URL discovery, and IAM role abuse via Lambda."
wordlist_ref: "wordlists/network/net-45-serverless-faas/"
---

# Net 07 Serverless — Offensive Methodology

## Shortcut
1. Discover function URLs (subdomains, API Gateway paths)
2. Test event injection in Lambda triggers (S3, SQS, DynamoDB)
3. Extract environment variables from function
4. Abuse Lambda IAM role for cloud lateral movement

## Detection
```bash
# Invoke function with malicious event
aws lambda invoke --function-name target-function --payload '{"Records":[{"body":"test"}]}' output.json
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

**Wordlist**: `wordlists/network/net-45-serverless-faas/` (7 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

