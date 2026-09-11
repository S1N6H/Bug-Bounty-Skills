---
name: recon-09-security-headers
sequence: recon-09
category: recon
domain: recon
description: "Security header analysis: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, Feature-Policy, Cache-Control, CORS, and other security-relevant headers."
wordlist_ref: "wordlists/recon/"
---

# Recon 09 Security Headers — Offensive Methodology

## Quick Workflow
1. Fetch all endpoints → collect all security headers
2. Grade each header: present+correct, present+weak, missing
3. For CSP: analyze directive strength
4. For CORS: test misconfiguration
5. Report actionable findings (missing = bug, weak = bug)

---

## Hacker Mindset
**Missing security headers are free bugs.** No HSTS means SSL stripping. No X-Frame-Options means clickjacking. Weak CSP means XSS is game on. These are the easiest findings with the lowest false-positive rate.

---

## Detection

### Header Collection
```bash
# Collect ALL response headers
curl -sI https://target.com

# Check all important security headers
curl -sI -D - https://target.com -o /dev/null | grep -iE "strict-transport-security|content-security-policy|x-frame-options|x-content-type-options|x-xss-protection|referrer-policy|permissions-policy|feature-policy|cache-control|access-control-allow-origin|set-cookie" 
```

### Header Analysis Matrix
| Header | Correct | Weak | Missing = Risk |
|--------|---------|------|---------------|
| Strict-Transport-Security | `max-age=31536000; includeSubDomains` | `max-age=<1yr` or no `includeSubDomains` | SSL stripping, MITM |
| X-Frame-Options | `DENY` or `SAMEORIGIN` | `ALLOW-FROM` (deprecated) | Clickjacking |
| X-Content-Type-Options | `nosniff` | absent | MIME sniffing, file upload RCE |
| Content-Security-Policy | strict directives (see below) | `unsafe-inline`, `unsafe-eval` | XSS |
| Referrer-Policy | `no-referrer` or `same-origin` | `unsafe-url` | Referrer leakage |
| Permissions-Policy | all restricted | absent, or geolocation/mic allowed | Feature abuse |
| Cache-Control | `no-store` for sensitive | `public` for sensitive | Sensitive data cached |

### CSP Deep Analysis
```bash
# Extract CSP
csp=$(curl -sI https://target.com | grep -i content-security-policy | sed 's/.*: //I')

# Check for unsafe directives
echo "$csp" | grep -q "unsafe-inline" && echo "WARN: unsafe-inline - XSS possible"
echo "$csp" | grep -q "unsafe-eval" && echo "WARN: unsafe-eval - DOM XSS possible"
echo "$csp" | grep -q "https://" && echo "Check CSP whitelist - open redirect?" 

# CSP whitelist bypass check
# If CSP includes: script-src https://*.google.com
# Attacker can host on: https://sites.google.com/attacker
```

### CORS Test
```bash
# Test if CORS allows arbitrary origins
curl -sI -H "Origin: https://evil.com" https://target.com/ | grep -i "access-control-allow-origin"

# If response includes: Access-Control-Allow-Origin: https://evil.com
# AND: Access-Control-Allow-Credentials: true
# THEN: CORS vulnerability confirmed
```

### Multi-Endpoint Scan
```bash
# Scan different endpoints — headers vary per route!
for path in "" api graphql login admin; do
  echo "=== /$path ==="
  curl -sI "https://target.com/$path" | grep -iE "strict-transport|csp|x-frame|x-content|x-xss|referrer"
done
```

---

## Wordlist Invocation
No wordlist needed for recon-09. Detection is response-analysis driven.

**Tools:** curl, grep

## Chaining
- Missing CSP → XSS is exploitable
- Weak CSP with whitelisted CDN → script injection via CDN → XSS
- No X-Frame-Options → clickjacking → phishing
- No HSTS → SSL strip → credential theft
- CORS misconfig → data exfiltration
- Missing Cache-Control → sensitive data in browser cache
