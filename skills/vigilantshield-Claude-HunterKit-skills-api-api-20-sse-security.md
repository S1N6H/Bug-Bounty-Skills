---
name: api-20-sse-security
sequence: api-20
category: protocol
domain: api
description: "Server-Sent Events (SSE) security testing: event stream interception, cross-origin SSE via CORS misconfig, connection injection, and data leakage via event ID enumeration."
wordlist_ref: "wordlists/api/api-30-sse-security/"
---

# SSE (Server-Sent Events) — API Offensive Methodology

## Quick Workflow

1. Find EventSource /events endpoints in page source
2. Test CORS on SSE endpoint — cross-origin read possible
3. Enumerate event IDs for data leakage
4. Test connection injection via custom event types

---

## Detection

### Unsafe CORS on SSE

```javascript
new EventSource('https://target.com/events', {withCredentials: true})
```

If `Access-Control-Allow-Origin: *` → cross-origin read.

### Event ID Enumeration

```
GET /api/events?lastEventId=100
GET /api/events?lastEventId=200
```

---





## Hacker Mindset

**Look for the edge cases.** Vulnerabilities live in the gap between what the developer assumed and what the framework actually does. Test every boundary: empty values, nulls, arrays, negative numbers, Unicode, very long strings.

**Blind detection always needs OOB.** If you can't see the output, set up a callback. No OOB = no confirmation.

**Chaining turns low/med into critical.** A single path traversal is medium. Path traversal + log file + admin session = RCE. Always think about what comes next.



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

**Wordlist**: `wordlists/api/api-30-sse-security/`

**Files**:
- `wordlists/api/api-30-sse-security/payloads/ssrf/` — staged exploit payloads (low → med → high)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)
4. Always establish a baseline response before running time-based payloads

**Tools**: curl, httpx, Burp Suite, or any HTTP client

## References

- HTML5 SSE spec
- CVE-2023-29149 (SSE data leakage)
