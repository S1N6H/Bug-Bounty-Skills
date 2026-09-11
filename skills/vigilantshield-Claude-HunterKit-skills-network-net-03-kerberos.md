---
name: net-03-kerberos
sequence: net-03
category: infrastructure
domain: net
description: "Kerberos attacks: kerberoasting, AS-REP roasting, golden/silver ticket, pass-the-ticket, delegation abuse (unconstrained/constrained/resource-based), and Kerberos relay."
wordlist_ref: "wordlists/network/net-08-kerberos/"
---

# Net 03 Kerberos — Offensive Methodology

## Shortcut
1. Enumerate SPNs for kerberoasting
2. Request TGS for service accounts → crack offline
3. Check for AS-REP roastable accounts (no pre-auth)
4. Check delegation configurations for lateral movement

## Detection
```bash
# Kerberoast (Linux)
impacket-GetUserSPNs -request -dc-ip 10.0.0.1 target.com/user

# AS-REP roast
impacket-GetNPUsers -request -dc-ip 10.0.0.1 target.com/

# Check delegation
impacket-findDelegation target.com/user
```


## Hacker Mindset

**Default mindset for skills without specific template.** Every security boundary is a hypothesis. Test it. If it breaks, that's the finding. Always escalate from single finding to chain.

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

**Wordlist**: `wordlists/network/net-08-kerberos/` (1 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

