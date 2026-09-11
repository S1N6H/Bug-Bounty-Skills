---
name: recon-07-waf-detection
sequence: recon-07
category: recon
domain: recon
description: "WAF detection and fingerprinting: identify WAF type, detect blocking thresholds, fingerprint block pages, map bypassable endpoints, identify WAF ruleset for targeted bypass."
wordlist_ref: "wordlists/recon/"
---

# Recon 07 Waf Detection — Offensive Methodology

## Quick Workflow
1. Send baseline request → record normal response
2. Send malicious-looking request → check if blocked/dropped
3. Fingerprint WAF type from block page, headers, response pattern
4. Map which endpoints have WAF vs which don't
5. Feed WAF type to bypass modules

---

## Hacker Mindset
**WAF is a maze, not a wall.** Every WAF has bypasses — different rulesets for different endpoints, different parsing vs the backend. Your job is to find the parsing gap.

---

## Detection

### WAF Fingerprinting
```bash
# Baseline normal request
curl -sI https://target.com

# Trigger WAF with malicious payload
curl -s "https://target.com/?q=<script>alert(1)</script>" -o /dev/null -w "Status: %{http_code}\nHeaders: %{header_json}\n"

# Check for block pages
curl -s "https://target.com/?q=../../../etc/passwd" | head -20
```

### WAF Indicators
| Indicator | Likely WAF |
|-----------|-----------|
| `x-sucuri-id` or `x-sucuri-cache` | Sucuri/CloudProxy |
| `x-served-by: cloudflare` | Cloudflare |
| `x-powered-by: AWS Lambda` + 403 | AWS WAF |
| `server: AkamaiGHost` | Akamai Kona |
| `x-waf-event` or `x-waf-detail` | ModSecurity |
| `x-cache: hit from cloudfront` + 403 | AWS WAF + CloudFront |
| Block page with Imperva logo | Imperva Incapsula |
| `Server: ATS` or `x-tinyproxy` | StackPath/Edge |
| Block page with reCAPTCHA | Cloudflare WAF/Challenge |

### Endpoint WAF Mapping
```bash
# Test same payload on different endpoints
# /api/ endpoint might have weaker WAF than /login/
# /graphql might not have WAF at all
# /internal/ or /v2/ might be unprotected

for endpoint in login signup api graphql internal v2 admin; do
  curl -s "https://target.com/$endpoint?q=<script>alert(1)</script>" -o /dev/null -w "$endpoint: %{http_code}\n"
done
```

### WAF vs Backend Parsing Gap
```shell
# WAF may parse: first param wins
# Backend may parse: last param wins
curl "https://target.com/?q=safe&q=<script>alert(1)</script>"

# WAF see: q=safe (safe)
# Backend see: q=<script>alert(1)</script> (executes)
```

---

## Wordlist Invocation
No wordlist needed for recon-07. Detection is response-analysis driven.

**Tools:** curl, httpx

## Chaining
- WAF type identified → web-36-waf-bypass for precise bypass technique
- WAF-gap endpoint found → direct injection without obstruction
- Certain bypass technique always works → chain with: SQLi, XSS, RCE, SSTI
- No WAF on endpoint → direct exploitation path
