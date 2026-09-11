---
name: web2-vuln-classes
description: Complete reference for 24 web2 bug classes — root causes, detection patterns, bypass tables, exploit techniques, and real paid examples. Covers IDOR, auth bypass, XSS, SSRF (11 bypass methods), SQLi, business logic, race conditions, OAuth/OIDC, file upload (10 bypasses), GraphQL, LLM/AI, SSTI, subdomain takeover, API misconfig (mass assignment, JWT, prototype pollution, CORS), ATO taxonomy, HTTP smuggling, cache poisoning, MFA bypass, SAML, error disclosure/debug endpoints, CSS injection, LFI→RCE (php://filter, iconv chains, log poisoning, .user.ini), and insecure deserialization (PHP phar chains, Java ysoserial, Python pickle, Node node-serialize). Use when hunting a specific vuln class or studying what makes bugs pay.
---

# WEB2 BUG CLASSES — 24 Classes

Root cause, pattern, bypass table, chaining opportunity, real paid examples.

> **Auth-required classes** (🔐): the ones below need **at least one logged-in
> session** loaded into the hunt to be testable. Use `hunt.py --auth-file
> .private/T.json` or `--cookie/--bearer` flags — every recon/scan tool then
> inherits the headers automatically. *(`hunt.py` is an optional wrapper; if it's
> not installed, pass the session by hand — `httpx/ffuf/katana/curl -H "Cookie:…"`
> / `-H "Authorization: Bearer …"`.)* For IDOR/BOLA/priv-esc, load **two
> sessions** (low- and high-priv) and diff. See `docs/auth-sessions.md`.
>
> 🔐 IDOR · Broken Auth/Access Control · Mass Assignment · OAuth/OIDC · JWT ·
> GraphQL field-level auth · LLM/AI chatbot IDOR · MFA (rate-limit + response
> manipulation tests) · ATO chains · SSRF behind login
>
> The MFA workflow-skip and SAML signature-stripping probes intentionally
> stay **unauthenticated** even when a session is loaded — that's the
> attack premise.

---

## ROUTING TABLE

| Bug Class | Reference File |
|-----------|---------------|
| 1. IDOR — Insecure Direct Object Reference | `reference/01-idor.md` |
| 2. Broken Auth / Access Control | `reference/02-broken-auth.md` |
| 3. XSS — Cross-Site Scripting | `reference/03-xss.md` |
| 4. SSRF — Server-Side Request Forgery | `reference/04-ssrf.md` |
| 5. Business Logic | `reference/05-business-logic.md` |
| 6. Race Conditions | `reference/06-race-conditions.md` |
| 7. SQL Injection | `reference/07-sql-injection.md` |
| 8. OAuth / OIDC Bugs | `reference/08-oauth-oidc.md` |
| 9. File Upload | `reference/09-file-upload.md` |
| 10. GraphQL-Specific | `reference/10-graphql.md` |
| 11. LLM / AI Features | `reference/11-llm-ai.md` |
| 12. API Security Misconfiguration | `reference/12-api-security.md` |
| 13. ATO — Account Takeover Taxonomy | `reference/13-ato.md` |
| 14. SSTI — Server-Side Template Injection | `reference/14-ssti.md` |
| 15. Subdomain Takeover | `reference/15-subdomain-takeover.md` |
| 16. Cloud / Infra Misconfigs | `reference/16-cloud-infra.md` |
| 17. HTTP Request Smuggling | `reference/17-http-smuggling.md` |
| 18. Cache Poisoning / Web Cache Deception | `reference/18-cache-poisoning.md` |
| 19. MFA / 2FA Bypass | `reference/19-mfa-bypass.md` |
| 20. SAML / SSO Attacks | `reference/20-saml.md` |
| 21. Error Disclosure / Debug Endpoints | `reference/21-error-disclosure.md` |
| 22. CSS Injection | `reference/22-css-injection.md` |
| 23. LFI / File Inclusion -> RCE | `reference/23-lfi-rce.md` |
| 24. Insecure Deserialization | `reference/24-insecure-deserialization.md` |
| False Positive Guidance Per Class | `reference/false-positive-guidance.md` |
| Report Templates Per Class | `reference/report-templates.md` |
