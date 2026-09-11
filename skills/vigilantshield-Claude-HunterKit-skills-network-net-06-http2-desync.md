---
name: net-06-http2-desync
sequence: net-06
category: infrastructure
domain: net
description: "HTTP/2 desync and HTTP/3 protocol attacks: H2.CL smuggling, H2.TE smuggling, HPACK bomb, Rapid Reset DoS, and protocol downgrade attacks."
wordlist_ref: "wordlists/network/net-44-http2-desync/"
---

# Net 06 Http2 Desync — Offensive Methodology

## Shortcut
1. Check if target supports HTTP/2 (ALPN negotiation)
2. Test H2.CL: downgrade to HTTP/1.1 with smuggled headers
3. Test Rapid Reset: rapid stream cancellation for DoS
4. Test HPACK bomb: small compressed header expands to large

## Detection
```bash
# Check HTTP/2 support
curl -sI --http2 https://target.com

# HTTP/2 smuggling test
python3 h2csmuggler.py -x https://target.com
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

**Wordlist**: `wordlists/network/net-44-http2-desync/` (6 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

