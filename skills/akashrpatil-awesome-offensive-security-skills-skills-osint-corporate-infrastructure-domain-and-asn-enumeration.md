---
name: domain-and-asn-enumeration
description: >
  Identify and map the external corporate footprint of a target organization. Use this skill
  at the absolute beginning of an engagement (Reconnaissance) to identify all registered domains,
  subdomains, IP ranges, and Autonomous System Numbers (ASNs) owned by the target. This skill forms
  the foundation for all subsequent external penetration testing and attack surface management.
domain: cybersecurity
subdomain: osint
category: Corporate Infrastructure
difficulty: beginner
estimated_time: "1-3 hours"
mitre_attack:
  tactics: [TA0043]
  techniques: [T1590.001, T1590.002, T1590.005, T1590.004]
platforms: [linux]
tags: [osint, reconnaissance, asm, domains, asn, subdomains, whois, intel-gathering]
tools: [amass, subfinder, bgpview, whois, crt.sh, theharvester]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Domain & ASN Enumeration

## When to Use
- Phase 1 of External Penetration Tests / Bug Bounty hunting.
- When mapping the Attack Surface of a large enterprise or conglomerate.
- When tracking mergers and acquisitions (discovering newly acquired, potentially insecure infrastructure).
- Before conducting vulnerability scanning, to ensure you know *every* asset the target owns.


## Prerequisites
- Target organization name, domain, or individual identifier
- OSINT framework tools installed (theHarvester, Maltego, Recon-ng)
- Understanding of operational security to avoid alerting the target
- Legal authorization for the intelligence gathering scope

## Workflow

### Phase 1: ASN (Autonomous System Number) Discovery

```bash
# Concept: Large organizations have their own ASNs, representing huge blocks of IP addresses.
# We want to map these to find infrastructure they host themselves vs cloud hosting.

# 1. Start with the main domain or company name via BGPView API or Hurricane Electric (bgp.he.net)
curl -s "https://api.bgpview.io/search?query_term=tesla" | jq

# 2. Extract ASNs provided in the response (e.g., AS394380)

# 3. Use Amass to map ASNs to IP ranges
amass intel -asn 394380

# 4. Alternatively, use whois to lookup the organization name
whois -h whois.radb.net -- '-i origin AS394380' | grep -Eo "([0-9.]+){4}/[0-9]+"

# This gives you the CIDR blocks (e.g., 216.239.32.0/19) owned directly by the company.
```

### Phase 2: Reverse WHOIS and Domain Discovery

```bash
# Concept: We have the main domain (target.com). Now we want to find OTHER root domains 
# owned by the same company (target.net, target-holdings.com, acquired-startup.com).

# 1. Extract WHOIS registrant email or organization name from the main domain
whois target.com | grep "Registrant Organization\|Registrant Email"
# Result: Registrant Organization: Target Corp

# 2. Perform Reverse WHOIS (who owns domains matching this Org/Email?)
# Use Amass Intel module
amass intel -org "Target Corp"
amass intel -whois -d target.com

# 3. Use Crunchbase and Wikipedia to manually search for Subsidaries and Acquisitions.
# Add these root domains to your target list.
```

### Phase 3: Subdomain Enumeration (Passive)

```bash
# Concept: Find thousands of subdomains (dev.target.com, api.target.com) without sending
# a single packet to the target's actual servers. Rely on third-party data.

# 1. Certificate Transparency Logs (crt.sh)
# Organizations must register TLS/SSL certs publicly.
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > subdomains_crt.txt

# 2. Use Subfinder (Rapid passive enumeration using multiple APIs)
subfinder -d target.com -all -silent > subdomains_subfinder.txt

# 3. Use theHarvester for search engine scraping
theHarvester -d target.com -b google,bing,linkedin,twitter -f target_harvest.html
```

### Phase 4: Subdomain Enumeration (Active & Bruteforce)

```bash
# Concept: Actively query a massive list of potential subdomains against DNS resolvers
# to see which ones actually resolve to an IP address.

# 1. Powerful active enumeration mapping with Amass
amass enum -active -d target.com -brute -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-110000.txt -o amass_active.txt

# Note: Amass can take a long time. For pure speed, Puredns or Massdns is preferred.
# 2. Fast resolution with Puredns
puredns resolve combined_subdomains.txt -r public_resolvers.txt -w resolved_subdomains.txt
```

### Phase 5: Result Compiling & Port Scanning Prep

```bash
# We now have a list of all root domains, combined subdomains, and ASNs (CIDR blocks).

# 1. Clean and deduplicate lists
cat subdomains_*.txt | sort | uniq > final_subdomains.txt

# 2. Resolve final subdomains to IP addresses
cat final_subdomains.txt | httpx -silent -rt -ip

# These IPs and CIDR bounds are now ready for Phase 2: Mass Port Scanning (e.g., using Naabu or Masscan).
```

## 🔵 Blue Team / Defensive Perspective
- **Attack Surface Management (ASM)**: The blue team must continuously run these exact same procedures to know their exposure. You cannot secure what you do not know you own.
- **Dangling DNS**: Periodically review DNS records. If a subdomain points to an expired AWS S3 bucket or unrenewed Heroku app, it is a critical Subdomain Takeover vulnerability.
- **WHOIS Privacy**: Use WHOIS Privacy protection where legally applicable to slow down Reverse WHOIS reconnaissance.

## Key Concepts
| Concept | Description |
|---------|-------------|
| ASN | Autonomous System Number; uniquely identifies a network routing domain on the internet |
| CIDR | Classless Inter-Domain Routing; a method for allocating IP addresses and IP routing (e.g., a "/24" block) |
| Certificate Transparency | Publicly accessible logs of all issued SSL/TLS certificates |
| Active vs Passive Recon | Active touches the target's servers. Passive asks third parties about the target without touching them. |

## Output Format
```
OSINT Infrastructure Intel Report
=================================
Target Organization: MegaCorp Industries

1. Autonomous Systems Identified: 
- AS12345 (MegaCorp US) -> Maps to 192.168.0.0/22
- AS67890 (MegaCorp EU) -> Maps to 10.0.0.0/24

2. Root Domains Identified (Via Reverse WHOIS):
- megacorp.com
- megacorp.net
- acquired-startup.io
- megacorp-staging.com

3. Subdomain Discovery Statistics:
- Certificate Logs (crt.sh): 432
- Passive Scraping (Subfinder): 856
- Active DNS Bruteforce (Amass): 120
- Total Unique Resolvable Subdomains: 1,024

Next Steps Approved: Initiate targeted port scanning against the 1,024 resolved endpoints and 2 identified CIDR blocks.
```

## 🛡️ Remediation & Mitigation Strategy
- **Input Validation:** Sanitize and strictly type-check all inputs.
- **Least Privilege:** Constrain component execution bounds.


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- OWASP: [OSINT Framework](https://osintframework.com/)
- ProjectDiscovery: [Subfinder](https://github.com/projectdiscovery/subfinder)
- OWASP Amass: [Amass GitHub](https://github.com/owasp-amass/amass)
