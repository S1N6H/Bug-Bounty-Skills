---
name: recon-08-auth-mapping
sequence: recon-08
category: recon
domain: recon
description: "Authentication surface mapping: detect auth schemes (JWT, OAuth, SAML, session, API keys), map protected vs public endpoints, identify role-based access patterns, fingerprint SSO providers, discover MFA/2FA presence."
wordlist_ref: "wordlists/recon/"
---

# Recon 08 Auth Mapping — Offensive Methodology

## Quick Workflow
1. Classify all endpoints as auth, unauth, or role-dependent
2. Identify auth type per endpoint: JWT, OAuth, SAML, session cookie, API key
3. Map role/privilege structure
4. Detect MFA/2FA, SSO, federation providers
5. Feed auth profile to auth-orchestrator for launch decisions

---

## Hacker Mindset
**Auth is the largest attack surface.** Every auth mechanism is a complex state machine — and every state machine has edge cases. Find the edge cases: token confusion, mixed auth, downgrade, implicit trust.

---

## Detection

### Auth Scheme Detection
```bash
# Check response headers for auth indicators
curl -sI https://target.com/ | grep -i "authorization\|www-authenticate\|set-cookie\|x-auth"

# Check for JWT in cookies
curl -sI https://target.com/ | grep -i "set-cookie" | grep -i "jwt\|token\|bearer"

# Check for OAuth endpoints
curl -s "https://target.com/.well-known/oauth-authorization-server" -w "%{http_code}"
curl -s "https://target.com/.well-known/openid-configuration" -o /dev/null -w "%{http_code}"
```

### Auth Type Indicators
| Indicator | Auth Type |
|-----------|-----------|
| `Authorization: Bearer eyJ...` | JWT |
| `Authorization: Bearer <opaque>` | API Key or Opaque Token |
| `Authorization: Basic <base64>` | HTTP Basic Auth |
| `Set-Cookie: sessionid=...` | Session Cookie |
| `WWW-Authenticate: Negotiate` | NTLM/Kerberos |
| `?code=` in callback URL | OAuth Authorization Code |
| SAMLRequest/SAMLResponse params | SAML |
| `/authorize`, `/oauth/token`, `/callback` | OAuth 2.0 |
| `X-API-Key:` header | API Key Auth |
| `/.well-known/openid-configuration` | OIDC |

### Public vs Protected Mapping
```bash
# Test auth-required endpoints WITHOUT credentials
# 401/403 = authenticated endpoint
# 200 = public access

endpoints=("/admin" "/api/users" "/dashboard" "/profile" "/settings" "/api/v1")
for ep in "${endpoints[@]}"; do
  code_noauth=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$ep")
  echo "$ep (no auth): $code_noauth"
done
```

### Role Enumeration
```bash
# Create user A, user B with different roles
# Access user A endpoints with user B token
# Look for vertical/horizontal privilege escalation

# Common role names to fuzz
# roles: admin, user, moderator, superadmin, editor, viewer, manager
```

### SSO/Federation Detection
```bash
# SAML metadata endpoints
curl -s "https://target.com/Saml2/acs" -w "%{http_code}"
curl -s "https://target.com/Saml2/metadata" -w "%{http_code}"

# OIDC endpoints
curl -s "https://target.com/.well-known/openid-configuration" | jq '.'
```

---

## Wordlist Invocation
No wordlist needed for recon-08. Detection is response-analysis driven.

**Tools:** curl, httpx, jq

## Chaining
- Public endpoint with sensitive data → immediate IDOR/BOLA
- JWT on public endpoint → JWT alg:none attack
- Mixed auth (JWT + cookie) → confusion attack
- SSO without MFA → credential stuffing risk
- No auth on admin endpoint → full admin access
- OAuth without PKCE → authorization code interception
