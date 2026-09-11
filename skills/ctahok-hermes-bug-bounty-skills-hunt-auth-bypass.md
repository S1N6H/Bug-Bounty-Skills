---
name: hunt-auth-bypass
description: |
  Authentication bypass hunting methodology. 12+ bypass classes including
  parameter manipulation, HTTP method tampering, API version downgrade,
  direct access to admin endpoints, cookie manipulation, header injection,
  default credentials, path traversal to auth files, and brute force.
triggers:
  - hunt auth bypass
  - authentication bypass
  - login bypass
  - admin bypass
  - auth bypass techniques
  - bypass authentication
category: security
---
# Authentication Bypass Hunting

Adapted from Claude-BugHunter by ElementalSouls.

---

## 12 Auth Bypass Classes

### Class 1: Parameter Manipulation
Add/modify parameters in request:
```json
{"role": "admin"}
{"isAdmin": true}
{"group": "administrators", "account_type": "premium"}
{"admin": 1, "admin": true, "is_admin": true}
{"user_id": 1}
```

**Detection:** Check every request where user metadata is created or updated — registration, profile update, team creation.

### Class 2: HTTP Method Tampering
```bash
GET /admin/users → 403
Try:
POST /admin/users → 200
PUT /admin/users → 200
DELETE /admin/users → 200
PATCH /admin/users → 200
OPTIONS /admin/users → 200
HEAD /admin/users → 200
```

**Detection:** For every 403 endpoint, try all HTTP methods.

### Class 3: API Version Downgrade
```bash
/v3/admin/users → 403
/v2/admin/users → 403
/v1/admin/users → 200  # Older version, less auth
/admin/users → 200      # Unversioned endpoint, maybe unprotected
```

**Detection:** When a newer API version blocks you, try older and newer versions.

### Class 4: Direct Access to Admin Endpoints
```bash
/admin
/administrator
/administrator.php
/admin/login
/admin/dashboard
/console
/debug
/_internal
```
**Detection:** Brute-force common admin paths. Often the login is protected but the dashboard isn't once you know the path.

### Class 5: Cookie/Header Manipulation
```bash
Cookie: admin=true
Cookie: user_role=administrator
Cookie: is_admin=1
X-Admin: true
X-Role: admin
```

**Detection:** If you see a `role` or `admin` field ANYWHERE in the application, try injecting it as a header/cookie.

### Class 6: Path Traversal to Auth Files
```bash
GET /static/../admin/users
GET /media/..%2f..%2fadmin
GET /images/../../admin
GET /assets/%2e%2e/admin/dashboard
```

**Detection:** If static files or media are served without auth checks, try path traversal to admin pages.

### Class 7: Hidden Parameters
```bash
# Common auth-bypass parameters to add
?admin=true
?isAdmin=true
?is_admin=1
?role=admin
?userType=admin
?access=full
?level=admin
?override=1
?bypass=true
?debug=true
?test=true
```

### Class 8: JSONP / CORS Bypass
If an endpoint has CORS headers but requires auth, try:
```bash
curl -H "Origin: https://evil.com" -H "Cookie: session=abc" https://target.com/api/user/data
```
Check for `Access-Control-Allow-Origin: https://evil.com` AND `Access-Control-Allow-Credentials: true`.

### Class 9: Default Credentials
```bash
admin:admin
admin:password
admin:admin123
admin:password123
administrator:administrator
root:root
root:toor
test:test
guest:guest
user:user
```

**Look for:** Login pages on admin panels, router interfaces, or well-known applications.

### Class 10: Session-Based Bypass
```bash
# Session fixation
Attacker creates session, gets session ID
Forces victim to use that session ID
Victim logs in → attacker now has authenticated session

# Session not invalidated after logout
Login → get token → logout → use old token → still works (session not invalidated)
```

### Class 11: Response Manipulation
Some apps check auth on the CLIENT side (JS) or return misleading status codes:
- 403 with admin panel HTML in response body
- 401 with full admin data in response body
- 302 redirect to login but response body contains admin page
- JavaScript hides admin elements but doesn't block server-side access

**Check:** Always read the full response body, not just status code.

### Class 12: Insecure Direct Access to Internal APIs
```bash
# Internal or microservice APIs often have no auth
/internal/api/users
/_api/users
/api/internal/users
/rpc/UserService/GetAll
```

**Detection:** Check JS bundles for internal API routes that aren't meant for public consumption.

---

## Testing Methodology

### For Each Protected Endpoint:

1. **Remove auth header entirely** — what happens?
2. **Try all HTTP methods**
3. **Try older API version**
4. **Add admin parameters** to body and query string
5. **Add admin headers** (`X-Admin: true`, `X-Role: admin`)
6. **Add admin cookies** (`role=admin`)
7. **Try path traversal** from unprotected paths
8. **Check for default credentials** on login pages
9. **Check session handling** — reuse after logout, session fixation
10. **Check response body** even on 403/401 — admin data may be hidden in the response

### Registration Flow Bypass
```json
// Try registering with elevated privileges
POST /api/register
{"username": "test", "password": "pass", "role": "admin"}

// Try claiming an existing email
POST /api/register
{"username": "test", "email": "admin@target.com"}
```

---

## Validation

Before reporting auth bypass:
- [ ] Bypass works from fresh session (no prior cookies/cache)
- [ ] Bypass works from incognito / different browser
- [ ] Bypass grants access to authenticated data or functionality
- [ ] Impact clear: "Attacker can access admin panel without authentication"
