---
name: net-02-ldap-ad
sequence: net-02
category: infrastructure
domain: net
description: "LDAP and Active Directory security: anonymous LDAP queries, user enumeration, password spraying, kerberoasting, AS-REP roasting, ACL abuse, and domain privilege escalation."
wordlist_ref: "wordlists/network/net-07-ldap-ad/"
---

# Net 02 Ldap Ad — Offensive Methodology

## Shortcut
1. Check for anonymous LDAP bind on port 389/636
2. Enumerate users, groups, computers from AD
3. Password spray with common passwords
4. Kerberoast service accounts for offline cracking

## Hacker Mindset
**AD is a graph of trust relationships.** Every object has permissions on other objects. A single compromised workstation can escalate to Domain Admin via ACL abuse paths.

## Detection
```bash
# Anonymous LDAP query
ldapsearch -x -H ldap://target.com -b "dc=target,dc=com" "(objectClass=user)" sAMAccountName

# Password spray (slowly!)
kerbrute passwordspray -d target.com users.txt Fall2024!
```
## Chaining & Escalation

Chain this finding with others for higher impact. Combine low-severity findings into critical attack chains. Always think: what's the next step after this works?

## OOB Detection & Blind Confirmation

Use Burp Collaborator or Interactsh for blind detection. Always set up OOB before firing payloads. Time-based: inject sleep(5) and measure response delay.

## Bypass Techniques

| Filter/Block | Bypass |
|-------------|--------|
| WAF/Input validation | Encoding, case variation, alternative syntax |
| Rate limiting | IP rotation via X-Forwarded-For, endpoint mirror |
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

