---
name: net-11-auth-federation
sequence: net-11
category: infrastructure
domain: net
description: "Auth federation security (SAML, OAuth, OIDC, ADFS, Okta): federation metadata exposure, IdP confusion, token replay, cross-domain trust abuse, and SSO bypass."
wordlist_ref: "wordlists/network/net-52-auth-federation/"
---

# Net 11 Auth Federation — Offensive Methodology

## Shortcut
1. Check federation metadata endpoints: /FederationMetadata/2007-06/FederationMetadata.xml
2. Discover OAuth/OIDC endpoints: /.well-known/openid-configuration
3. Test IdP confusion: forge tokens from one IdP to access another
4. Test token replay across services

## Detection
```bash
# ADFS metadata
curl https://target.com/FederationMetadata/2007-06/FederationMetadata.xml

# OIDC config
curl https://target.com/.well-known/openid-configuration
```


## Hacker Mindset

**Auth federation: SAML metadata, OIDC discovery, IdP confusion, token replay.** Federation metadata endpoints are often publicly accessible and reveal trust relationships.

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

**Wordlist**: `wordlists/network/net-52-auth-federation/` (2 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

