---
name: recon-06-crawl-deep
sequence: recon-06
category: recon
domain: recon
description: "Deep web crawling: JS-driven SPA crawling, hidden endpoint discovery, form extraction, parameter fuzzing, directory brute-force, hidden admin panel discovery, and complete attack surface enumeration."
wordlist_ref: "wordlists/recon/"
---

# Recon 06 Crawl Deep — Offensive Methodology

## Quick Workflow
1. Crawl target - extract all client-side routes, APIs, forms, params
2. JS-render if SPA - crawl routes that only appear after JS execution
3. Fuzz for hidden paths - admin panels, staging, dev endpoints
4. Extract all input vectors - forms, URL params, headers, cookies, WebSocket

---

## Hacker Mindset
**Surface area is the attack area.** Every endpoint you don't know about is a bug waiting to be found. Hidden admin panels, staging environments, and debug endpoints are the highest-value findings.

---

## Detection

### Passive Crawling
```bash
# Basic crawl with katana
katana -u https://target.com -d 3 -o crawl.txt

# Extract all forms
cat crawl.txt | grep -i "form\|input\|select\|textarea"

# Extract API endpoints
cat crawl.txt | grep -i "api\|v1\|v2\|graphql\|rest\|swagger"
```

### SPA Crawling (JS-rendered routes)
```bash
# Use chromedp or puppeteer to crawl SPA
# Extract routes from JS bundles
grep -oP '["'\'']/[a-zA-Z0-9_/{}.-]+["'\'']' bundle.js | sort -u

# Hidden SPA routes
# Look for: /dashboard, /admin, /settings, /profile
```

### Directory Bruteforce
```bash
# Common paths
for path in admin dashboard api v1 v2 internal debug test dev staging; do
  code=$(curl -s -o /dev/null -w "%{http_code}" https://target.com/$path)
  [ "$code" != "404" ] && echo "FOUND: $path -> $code"
done

# 403 ≠ 404 — means exists but locked, potential auth bypass
# 200 with redirect to login — means authenticated route exists
```

### Parameter Discovery
```bash
# Hidden parameters
# Common: id, user_id, admin, debug, test, token, secret, key, file, url, path

# Test each param for reflection and injection
```

---

## Wordlist Invocation

**Workflow:**
1. Crawl all reachable URLs (depth 2-5)
2. Extract forms, endpoints, params from each page
3. Fuzz for hidden directories (admin, dev, api, test)
4. Report full surface map

**Tools:** curl, httpx, katana, grep, jq, chrome-devtools MCP

## Chaining
- Hidden admin panel → auth bypass → full admin access
- Staging endpoint → CVE exploitation → RCE
- Debug endpoint → information disclosure → pivoting
- SPA route → IDOR on client-side ID → mass assignment
