---
name: web2-recon
description: Web2 recon pipeline — subdomain enumeration (subfinder, Chaos API, assetfinder), live host discovery (dnsx, httpx), URL crawling (katana, waybackurls, gau), directory fuzzing (ffuf), JS analysis (LinkFinder, SecretFinder), continuous monitoring (new subdomain alerts, JS change detection, GitHub commit watch). Use when starting recon on any web2 target or when asked about asset discovery, subdomain enum, or attack surface mapping.
---

# WEB2 RECON PIPELINE

Full asset discovery from nothing to a prioritized URL list ready for hunting.

## THE 5-MINUTE RULE

If a target shows nothing interesting after 5 minutes of recon, move on. See `reference/5-minute-rule.md` for kill signals.

## ROUTING TABLE

| Topic | Reference |
|-------|-----------|
| Setup (one-time) | `reference/setup.md` |
| The 5-Minute Rule | `reference/5-minute-rule.md` |
| Standard Recon Pipeline | `reference/standard-pipeline.md` |
| Attack Surface Triage | `reference/attack-surface-triage.md` |
| JS Analysis (SecretFinder, LinkFinder) | `reference/js-analysis.md` |
| Directory Fuzzing (ffuf) | `reference/directory-fuzzing.md` |
| Target Scoring — Go / No-Go | `reference/target-scoring.md` |
| Tech Stack Detection (+ CVE correlation) | `reference/tech-stack-detection.md` |
| Continuous Monitoring Setup | `reference/continuous-monitoring.md` |
| Port Scanning | `reference/port-scanning.md` |
| Secret Scanning in JS Bundles | `reference/secret-scanning.md` |
| GitHub Dorking | `reference/github-dorking.md` |
| 30-Minute Recon Protocol | `reference/30-minute-protocol.md` |
| **CDN/WAF Detection** (قبل الاختبار) | `reference/cdn-waf-detection.md` |
| **ASN Discovery** (وسّع السطح) | `reference/asn-discovery.md` |
| **Subdomain Boost** (alterx + puredns) | `reference/subdomain-boost.md` |
| **SSL + Favicon Recon** (tlsx + shodan) | `reference/ssl-favicon-recon.md` |
| **HTTP Smuggling Check** (في الـ recon) | `reference/http-smuggling-check.md` |
