---
name: net-13-advanced-database
sequence: net-13
category: infrastructure
domain: net
description: "Advanced database attacks: NoSQL injection in production databases, database link traversal, cross-database query, CDC (Change Data Capture) abuse, and database replication hijacking."
wordlist_ref: "wordlists/network/net-54-advanced-database/"
---

# Net 13 Advanced Database — Offensive Methodology

## Shortcut
1. Enumerate linked servers (MSSQL) or database links (Oracle)
2. Execute cross-database queries
3. Exploit CDC feeds for data access
4. Abuse replication for data manipulation

## Detection
```sql
-- MSSQL linked servers
EXEC sp_linkedservers

-- Oracle database links
SELECT * FROM all_db_links;
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

**Wordlist**: `wordlists/network/net-54-advanced-database/` (15 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

