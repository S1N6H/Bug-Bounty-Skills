---
name: api-18-websocket-protocol
sequence: api-18
category: protocol
domain: api
description: "WebSocket protocol-level attacks: subprotocol negotiation bypass, WS->HTTP smuggling, ping/pong flood DoS, continuation frame DoS, and compression bomb via permessage-deflate."
wordlist_ref: "wordlists/web/web-19-websocket/"
---

# WebSocket Protocol — API Offensive Methodology

## Quick Workflow

1. Fuzz subprotocol negotiation during handshake
2. Test HTTP request smuggling over upgraded WS connection
3. Send malformed frames (continuation without end, ping floods)
4. Test permessage-deflate with compression bombs

---

## Protocol Attacks

### Subprotocol Injection

```http
GET /ws HTTP/1.1
Host: target.com
Sec-WebSocket-Protocol: admin, internal, debug
```

### WS Smuggling

After upgrade, send HTTP-like data through WS to proxy confusion.

### DoS Vectors

- **Continuation frames**: Send many fragments without final fragment → OOM
- **Ping floods**: Rapid ping/pong exhausts server
- **Compression bomb**: Small compressed message expands to gigabytes

---





## Hacker Mindset

**WebSocket auth is checked once (at connection), not per-message.** If you can establish a WS connection, you can send any message until the connection drops.

**CSWSH (Cross-Site WebSocket Hijacking) is the WS equivalent of CSRF.** If there's no Origin check, any website can open a WS connection to your target and send messages as the victim.



## Chaining & Escalation

### Direct Escalation
This vulnerability can often be escalated directly. Test for RCE, data access, or privilege escalation depending on context.

### Chain with Other Skills
| Partner Vulnerability | Chain Effect |
|----------------------|--------------|
| SSRF | Use SSRF to reach internal services through this vuln |
| XSS | Stolen sessions amplify account-level findings |
| IDOR/BOLA | Find more data to exploit via authorization gaps |

### Amplification
Race conditions, parallel requests, and HTTP/2 single-packet attacks can amplify impact by 10-50x.



## OOB Detection & Blind Confirmation

### Blind Confirmation
Always set up OOB detection before testing. Use:
- **Burp Collaborator** — built into Burp Suite Pro
- **Interactsh** — OOB detection server (https://app.interactsh.com)
- **Canarytokens** for callback detection

### Timing Side-Channel
If OOB is blocked, use time-based detection:
- Inject `sleep(5)` or equivalent
- Compare response times between baseline and injected requests
- 5s+ delay = vulnerability confirmed



## Tools

- Burp Suite (manual testing + Intruder)
- curl / httpx
- Nuclei templates


## Bypass Techniques

| Filter/Block | Bypass |
|-------------|--------|
| WAF/Input validation | Encoding, case variation, alternative syntax |
| Rate limiting | IP rotation via X-Forwarded-For, HTTP/2 multiplex |
| Blacklist | Alternative syntax, polyglot payloads |
| Blacklist bypass | Unicode, double encoding, null bytes |

## Wordlist Invocation

When testing this vulnerability, invoke the wordlist payloads manually:

**Wordlist**: `wordlists/web/web-19-websocket/`

**Files**:
- `wordlists/web/web-19-websocket/payloads/xss/` — staged exploit payloads (low → med → high)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)
4. Always establish a baseline response before running time-based payloads

**Tools**: curl, httpx, Burp Suite, or any HTTP client

## References

- CVE-2023-44487 (HTTP/2 multiplex), CVE-2024-27316 (WS smuggling)
