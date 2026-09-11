---
name: semgrep-custom-rule-writing
description: >
  Write custom Semgrep rules to identify organization-specific logic flaws, improper 
  cryptography usage, or missing authorization checks during source code review. 
  This skill focuses on moving beyond default rulesets to locate complex vulnerabilities.
domain: cybersecurity
subdomain: bug-hunting
category: Source Code Analysis
difficulty: intermediate
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0001, TA0007]
  techniques: [T1190]
platforms: [code]
tags: [semgrep, sast, source-code-review, static-analysis, custom-rules, bug-hunting]
tools: [semgrep, code-editor]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Semgrep Custom Rule Writing

## When to Use
- During a white-box penetration test or source code review when looking for bespoke vulnerabilities that generic SAST tools fail to detect.
- To codify and hunt for organization-specific anti-patterns (e.g., calling an internal API without passing the authentication context).


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Understanding Semgrep Patterns

```yaml
# Concept: Semgrep syntax rules:
  - id: simple-eval-detection
    pattern: eval(...)
    message: "Avoid using eval() as it can lead to code injection."
    languages: [javascript, python]
    severity: ERROR
```

### Phase 2: Utilizing Metavariables

```yaml
# rules:
  - id: python-exec-with-variable
    pattern: exec($X)
    message: "Using exec() on variable $X is dangerous."
    languages: [python]
    severity: WARNING
```

### Phase 3: Pattern-Inside and Pattern-Not (Contextual Matching)

```yaml
# rules:
  - id: missing-auth-check-flask
    patterns:
      - pattern-inside: |
          @app.route(...)
          def $FUNC(...):
            ...
      - pattern: return $RENDER(...)
      - pattern-not-inside: |
          @login_required
          def $FUNC(...):
            ...
      - pattern-not-inside: |
          if current_user.is_authenticated:
            ...
    message: "Flask route missing @login_required or explicit authentication check."
    languages: [python]
    severity: ERROR
```

### Phase 4: Testing Rules via Semgrep CLI

```bash
# # semgrep --config custom-rules.yml src/
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Identify Pattern ] --> B{Write Rule ]}
    B -->|Yes| C[Test Rule ]
    B -->|No| D[Refine Scope ]
    C --> E[Execute Scan ]
```

## 🔵 Blue Team Detection & Defense
- **CI/CD Integration Pipeline Validation**: **Centralized Rule Repositories**: **Developer Education**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Semgrep Custom Rule Writing — Assessment Report
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
- Semgrep: [Writing Rules Documentation](https://semgrep.dev/docs/writing-rules/rule-syntax/)
- GitHub Security Lab: [Using Semgrep to find vulnerabilities](https://securitylab.github.com/research/semgrep-rule-writing/)
