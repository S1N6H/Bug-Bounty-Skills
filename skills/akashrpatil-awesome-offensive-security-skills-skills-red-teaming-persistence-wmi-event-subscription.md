---
name: wmi-event-subscription
description: >
  [DEPRECATED: This skill has been consolidated into wmi-event-subscriptions.]
  For WMI Event Subscription persistence techniques, use the comprehensive
  wmi-event-subscriptions skill which covers all trigger types (startup, logon,
  process launch, time-based), multiple consumer types (CommandLine, ActiveScript),
  full cleanup procedures, and OPSEC considerations.
domain: cybersecurity
subdomain: red-teaming
category: Persistence
difficulty: expert
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0003]
  techniques: [T1546.003]
platforms: [windows]
tags: [wmi, persistence, deprecated, see-wmi-event-subscriptions]
tools: [powershell]
version: "2.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# WMI Event Subscription — CONSOLIDATED

> **⚠️ This skill has been consolidated.** The canonical, comprehensive version is:
> **`red-teaming/persistence/wmi-event-subscriptions`**
>
> That skill includes:
> - 4 trigger types (startup, user logon, process launch, time-based)
> - 2 consumer types (CommandLineEventConsumer, ActiveScriptEventConsumer)
> - Full OPSEC guidance and cleanup procedures
> - Comprehensive Blue Team detection via Sysmon Event IDs 19/20/21
> - Decision flowchart for choosing the right approach

## When to Use
Use `wmi-event-subscriptions` instead of this skill. This entry exists for backward compatibility.

## Prerequisites
- See the `wmi-event-subscriptions` skill for full prerequisites

## Workflow
### Phase 1: Redirect to Canonical Skill
Refer to `red-teaming/persistence/wmi-event-subscriptions` for the complete workflow.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Consolidated Skill | This was merged with two other WMI skills into a single comprehensive `wmi-event-subscriptions` skill |

### Proof of Concept (PoC)
```bash
# Standard payload injection format
curl -X POST https://target/api -d 'exploit=true'
```

## 🔵 Blue Team
- Deploy robust WAF rules to detect anomalies.
- Monitor logs for unusual access patterns.

## 🛡️ Remediation & Mitigation Strategy
- **Input Validation:** Sanitize and strictly type-check all inputs.
- **Least Privilege:** Constrain component execution bounds.


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- See `red-teaming/persistence/wmi-event-subscriptions` for all references

- [Mitre ATT&CK Reference](https://attack.mitre.org/techniques/T1546/003/)
