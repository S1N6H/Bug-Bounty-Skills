---
name: net-05-database
sequence: net-05
category: infrastructure
domain: net
description: "Database service attacks: exposed databases (MySQL, PostgreSQL, MongoDB, Redis, Elasticsearch), default credentials, CVE exploitation, SQL injection via protocol, and data exfiltration."
wordlist_ref: "wordlists/network/net-21-database-services/"
---

# Net 05 Database — Offensive Methodology

## Shortcut
1. Scan for exposed database ports (3306, 5432, 27017, 6379, 9200)
2. Try default credentials
3. Check for unauthenticated access
4. Dump databases

## Detection
```bash
# Check for unauthenticated Redis
redis-cli -h target.com -p 6379 info

# Check for unauthenticated Elasticsearch
curl -s https://target.com:9200/_cat/indices

# Try default creds for MySQL
mysql -h target.com -u root -p'root'
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

**Wordlist**: `wordlists/network/net-21-database-services/` (15 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

