---
name: net-01-cloud
sequence: net-01
category: infrastructure
domain: net
description: "Cloud security (AWS/Azure/GCP): credential harvesting, IAM enumeration, privilege escalation, persistence, data exfiltration, and lateral movement across cloud providers."
wordlist_ref: "wordlists/network/net-26-cloud-iam/"
---

# Net 01 Cloud — Offensive Methodology

## Shortcut
1. Identify cloud provider from metadata/response headers
2. Enumerate identity: aws sts get-caller-identity / az account show
3. Map IAM permissions to privilege escalation paths
4. Find data stores (S3, Blob, GCS) and exfiltrate

## Hacker Mindset
**Cloud is a different game.** No shell required — API calls are your attack surface. IAM is the kill chain. One misconfigured role can escalate to full account control.

## Detection
```bash
# AWS identity
aws sts get-caller-identity
# Check S3
aws s3 ls s3://target-bucket --no-sign-request
# Check bucket policy
aws s3api get-bucket-policy --bucket target-bucket
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

**Wordlist**: `wordlists/network/net-26-cloud-iam/` (9 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

