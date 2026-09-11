---
name: web-application-recon-and-enumeration
description: >
  Perform comprehensive web application reconnaissance and enumeration including subdomain discovery,
  directory bruteforcing, technology fingerprinting, port scanning, and content discovery. Use this skill
  as the first step in any bug bounty or web penetration test to map the target's attack surface before
  exploitation. Covers passive and active recon, JavaScript analysis, and API endpoint enumeration.
domain: cybersecurity
subdomain: bug-hunting
category: Recon & Enumeration
difficulty: beginner
estimated_time: "1-3 hours"
mitre_attack:
  tactics: [TA0043]
  techniques: [T1595, T1592, T1590]
platforms: [linux, windows, macos]
tags: [reconnaissance, enumeration, subdomain-discovery, directory-bruteforce, web-recon, bug-bounty, asset-discovery, attack-surface]
tools: [subfinder, httpx, nuclei, ffuf, dirsearch, nmap, amass, gau, waybackurls]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Web Application Recon & Enumeration

## When to Use
- As the FIRST STEP in any bug bounty or web application pentest engagement
- When you need to map the target's complete attack surface
- When discovering subdomains, hidden endpoints, and technologies
- When building a target profile before vulnerability testing


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Passive Subdomain Enumeration

```bash
# subfinder — fast passive subdomain discovery
subfinder -d target.com -all -o subdomains.txt

# amass — comprehensive passive enumeration
amass enum -passive -d target.com -o amass_subs.txt

# assetfinder
assetfinder --subs-only target.com >> subdomains.txt

# Merge and deduplicate
cat subdomains.txt amass_subs.txt | sort -u > all_subs.txt
echo "[+] Total unique subdomains: $(wc -l < all_subs.txt)"
```

### Phase 2: DNS Resolution & HTTP Probing

```bash
# Resolve live subdomains
cat all_subs.txt | httpx -silent -status-code -title -tech-detect -o live_hosts.txt

# Check which hosts respond on interesting ports
cat all_subs.txt | httpx -ports 80,443,8080,8443,3000,5000,8000,9090 -silent -o all_ports.txt

# Quick Nmap for service detection
nmap -sV -sC -p 21,22,80,443,3306,5432,8080,8443 -iL live_ips.txt -oA nmap_scan
```

### Phase 3: Technology Fingerprinting

```bash
# Wappalyzer-style detection (httpx already does this with -tech-detect)
# Additional: Nuclei technology detection
nuclei -l live_hosts.txt -t technologies/ -o tech_results.txt

# whatweb for detailed fingerprinting
whatweb -i live_hosts.txt --log-brief=whatweb_results.txt

# Check for known CMS
# WordPress: /wp-admin, /wp-content, /xmlrpc.php
# Drupal: /core/CHANGELOG.txt, /user/login
# Joomla: /administrator, /api/index.php
```

### Phase 4: Directory & Content Discovery

```bash
# ffuf — fast fuzzer
ffuf -u https://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt \
  -mc 200,301,302,403 -o ffuf_dirs.json

# API endpoint discovery
ffuf -u https://target.com/api/FUZZ -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt \
  -mc 200,401,403 -o api_endpoints.json

# Backup file discovery
ffuf -u https://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-large-files.txt \
  -e .bak,.old,.zip,.tar.gz,.sql,.env,.git -mc 200 -o backups.json
```

### Phase 5: Historical Data & JavaScript Analysis

```bash
# Wayback Machine URLs
echo "target.com" | waybackurls | sort -u > wayback_urls.txt

# GAU (GetAllUrls)
echo "target.com" | gau --threads 5 | sort -u > gau_urls.txt

# Extract JavaScript files
cat wayback_urls.txt gau_urls.txt | grep "\.js$" | sort -u > js_files.txt

# Analyze JS for endpoints, secrets, API keys
cat js_files.txt | while read url; do
  curl -s "$url" | grep -oP '(api|endpoint|url|secret|key|token|password)\s*[:=]\s*["\x27][^"\x27]+["\x27]'
done > js_secrets.txt

# LinkFinder for endpoint extraction from JavaScript
python3 linkfinder.py -i https://target.com -d -o endpoints.html
```

### Phase 6: Vulnerability Scanning

```bash
# Nuclei — fast vulnerability scanner
nuclei -l live_hosts.txt -t cves/ -t exposures/ -t misconfiguration/ \
  -severity critical,high,medium -o nuclei_vulns.txt

# Check for common misconfigurations
nuclei -l live_hosts.txt -t misconfiguration/ -o misconfig.txt

# Check exposed panels and default credentials
nuclei -l live_hosts.txt -t default-logins/ -o default_creds.txt
```


### ⚡ OPSEC & Anti-Detection for Bug Bounty

> Never get rate-limited or blocked before you find the bug.

- **Request Timing**: Add 200-500ms jitter between automated requests — never burst
- **User-Agent Rotation**: Use realistic browser UA strings, not tool defaults
- **IP Rotation**: Use residential proxies for long engagements, not datacenter IPs
- **Session Preservation**: Test in authenticated context to avoid WAF triggers on unauthenticated rapid probing
- **Avoid Scanner Signatures**: Strip nuclei/ffuf/sqlmap markers from requests; triagers check for low-effort automation
- **Incremental Fuzzing**: Start with 50 requests/minute, increase only after confirming no rate limiting


### 🌐 Modern Recon Pipeline (8-Phase Cycle — 2026 Standard)

> **Source**: Jason Haddix, NahamSec, and InsiderPHD (Katie Paxton-Fear) methodologies

**Phase 1 — ASN Discovery**: `bgp.he.net` → Find all owned IP ranges via ASN
**Phase 2 — Apex Domain Discovery**: `tenantdomains.sh` → Microsoft tenant correlation
**Phase 3 — Acquisition Intel**: Traxon/Pitchbook → Find M&A targets = fresh attack surface
**Phase 4 — Cloud SSL Recon**: Caduceus/Gungnir → Scan AWS/GCP/Azure IPs for SSL metadata
**Phase 5 — Port Scanning**: ASNmap → Nabu → Nmap cascade for service enumeration
**Phase 6 — Passive Shodan Dorking**: Karma → Pre-identified vulns without sending packets
**Phase 7 — Subdomain Aggregation**: SubFinder + Beebot + Chaos + Amass (parallel, with API keys)
**Phase 8 — "The One-Liner"**:
```bash
cat apexes.txt | subfinder | httpx -sc -title -cl -web-server -asn -l 15 \
  -ports 80,8080,443,8443,4443,8888 -o output.csv
```

**Premium Intel Sources (Top 1% Use These):**
- GitHub CFOR (Cross-Fork Object References) — Find developer personal repos with leaked secrets
- Cisco Umbrella passive DNS — 10-20% more subdomains than public sources
- CT Log monitoring via Gungnir — Real-time new certificate alerts
- Shodan InternetDB API — Instant port+banner data without scanning

## 🔵 Blue Team Detection
- **Asset inventory**: Maintain a current inventory of all subdomains and services
- **Rate limiting**: Detect and block rapid enumeration attempts
- **Honeypot subdomains**: Create decoy subdomains and alert on access
- **DNS monitoring**: Alert on subdomain enumeration patterns

## Output Format
```
Reconnaissance Report
======================
Target: target.com
Subdomains: 342 discovered, 187 live
Open Ports: 22(SSH), 80(HTTP), 443(HTTPS), 8080(HTTP-Alt)
Technologies: nginx/1.18, PHP/8.1, WordPress 6.4, MySQL 8.0
CMS: WordPress (outdated plugins detected)
API Endpoints: 45 discovered (/api/v1/*, /api/v2/*)
Sensitive Files: .env exposed, .git directory accessible
JavaScript Secrets: 3 API keys found in JS files
```


## 💰 Industry Bounty Payout Statistics (2024-2025)

| Company/Platform | Total Paid | Highest Single | Year |
|-----------------|------------|---------------|------|
| **Google VRP** | $17.1M | $250,000 (CVE-2025-4609 Chrome sandbox escape) | 2025 |
| **Microsoft** | $16.6M | (Not disclosed) | 2024 |
| **Google VRP** | $11.8M | $100,115 (Chrome MiraclePtr Bypass) | 2024 |
| **HackerOne (all programs)** | $81M | $100,050 (crypto firm) | 2025 |
| **Meta/Facebook** | $2.3M | up to $300K (mobile code execution) | 2024 |
| **Crypto.com (HackerOne)** | $2M program | $2M max | 2024 |
| **1Password (Bugcrowd)** | $1M max | $1M (highest Bugcrowd ever) | 2024 |
| **Samsung** | $1M max | $1M (critical mobile flaws) | 2025 |

**Key Takeaway**: Google alone paid $17.1M in 2025 — a 40% increase YoY. Microsoft paid $16.6M.
The industry is paying more, not less. Average critical bounty on HackerOne: $3,700 (2023).


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- OWASP: [Web Security Testing Guide — Information Gathering](https://owasp.org/www-project-web-security-testing-guide/)
- Bug Bounty Methodology: [Nahamsec Recon Guide](https://github.com/nahamsec/Resources-for-Beginner-Bug-Bounty-Hunters)
