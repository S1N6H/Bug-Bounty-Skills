---
name: security-knowledge
description: OWASP Top 10, CWE patterns, and security best practices reference
---

# Security Knowledge Base

Reference information for OWASP Top 10, CWE patterns, and security testing methodology.

## OWASP Top 10 (2021) Quick Reference

### A01: Broken Access Control
- **Description**: Users acting outside intended permissions. IDOR, privilege escalation, missing authorization checks, CORS misconfiguration.
- **Common CWEs**: CWE-200 (Information Exposure), CWE-284 (Improper Access Control), CWE-285 (Improper Authorization), CWE-352 (CSRF), CWE-639 (IDOR)
- **Detection**: Manual code review, nuclei templates, authorization testing with different user roles
- **Tools**: semgrep (auth patterns), nuclei (CORS/IDOR templates), manual testing
- **Fix patterns**: Deny by default, implement RBAC, validate ownership on every request, use anti-CSRF tokens

### A02: Cryptographic Failures
- **Description**: Weak cryptography, plaintext secrets, missing TLS, insecure random number generation, weak hashing.
- **Common CWEs**: CWE-259 (Hard-coded Password), CWE-327 (Broken Crypto), CWE-328 (Weak Hash), CWE-330 (Insufficient Randomness), CWE-311 (Missing Encryption)
- **Detection**: Static analysis for weak crypto functions, secret scanning, TLS configuration checks
- **Tools**: semgrep (crypto rules), trufflehog (secrets), trivy (TLS configs), nmap (SSL scan)
- **Fix patterns**: Use strong algorithms (AES-256, SHA-256+), TLS 1.2+, proper key management, bcrypt/argon2 for passwords

### A03: Injection
- **Description**: SQL injection, XSS, command injection, LDAP injection, expression language injection.
- **Common CWEs**: CWE-20 (Input Validation), CWE-74 (Injection), CWE-78 (OS Command Injection), CWE-79 (XSS), CWE-89 (SQL Injection)
- **Detection**: SAST for unsanitized input in queries/commands, DAST for reflected/stored injection
- **Tools**: semgrep (injection patterns), sqlmap (SQLi), dalfox (XSS), nuclei (injection templates)
- **Fix patterns**: Parameterized queries, input validation, output encoding, CSP headers, avoid eval/exec

### A04: Insecure Design
- **Description**: Missing threat modeling, insecure design patterns, insufficient rate limiting, missing business logic validation.
- **Common CWEs**: CWE-256 (Plaintext Storage of Password), CWE-501 (Trust Boundary Violation), CWE-522 (Insufficiently Protected Credentials)
- **Detection**: Architecture review, design pattern analysis, business logic testing
- **Tools**: Manual review (Claude), semgrep (design anti-patterns)
- **Fix patterns**: Threat modeling, secure design patterns, defense in depth, principle of least privilege

### A05: Security Misconfiguration
- **Description**: Default configurations, unnecessary features enabled, missing security headers, verbose error messages, open cloud storage.
- **Common CWEs**: CWE-16 (Configuration), CWE-200 (Information Exposure), CWE-209 (Error Message Information Leak), CWE-548 (Directory Listing)
- **Detection**: Configuration file analysis, HTTP header inspection, default credential checks
- **Tools**: nuclei (misconfig templates), nmap (service enumeration), ffuf (directory listing), semgrep (config patterns)
- **Fix patterns**: Hardened configs, disable debug mode, security headers (HSTS, CSP, X-Frame-Options), remove defaults

### A06: Vulnerable and Outdated Components
- **Description**: Using components with known CVEs, outdated libraries, unsupported frameworks.
- **Common CWEs**: CWE-937 (Using Components with Known Vulns), CWE-1035 (Using Components with Known Vulns)
- **Detection**: Dependency scanning, SCA (Software Composition Analysis)
- **Tools**: trivy (CVE scanning), npm audit, pip-audit, semgrep (outdated API usage)
- **Fix patterns**: Regular dependency updates, automated vulnerability scanning in CI/CD, remove unused dependencies, use LTS versions

### A07: Identification and Authentication Failures
- **Description**: Weak passwords, missing MFA, credential stuffing, session fixation, improper session management.
- **Common CWEs**: CWE-255 (Credentials Management), CWE-287 (Improper Authentication), CWE-307 (Brute Force), CWE-384 (Session Fixation), CWE-798 (Hard-coded Credentials)
- **Detection**: Auth flow analysis, session management testing, credential scanning
- **Tools**: trufflehog (hard-coded creds), hydra (brute force), semgrep (auth patterns), nuclei (default creds)
- **Fix patterns**: Strong password policies, MFA, secure session management, rate limiting, account lockout

### A08: Software and Data Integrity Failures
- **Description**: Insecure deserialization, CI/CD pipeline attacks, unsigned updates, supply chain attacks.
- **Common CWEs**: CWE-345 (Insufficient Verification), CWE-353 (Missing Integrity Check), CWE-502 (Deserialization of Untrusted Data)
- **Detection**: Code review for deserialization, CI/CD config review, dependency integrity checks
- **Tools**: semgrep (deserialization patterns), trivy (supply chain), manual review
- **Fix patterns**: Input validation before deserialization, signed artifacts, integrity verification, SRI for CDN resources

### A09: Security Logging and Monitoring Failures
- **Description**: Missing audit logs, logs not monitored, sensitive data in logs, insufficient alerting.
- **Common CWEs**: CWE-117 (Log Injection), CWE-223 (Omission of Security-relevant Info), CWE-532 (Information in Log Files), CWE-778 (Insufficient Logging)
- **Detection**: Log analysis, monitoring configuration review
- **Tools**: semgrep (logging patterns), manual review
- **Fix patterns**: Log security events, centralized logging, avoid logging sensitive data, implement alerting

### A10: Server-Side Request Forgery (SSRF)
- **Description**: Fetching remote resources without validating user-supplied URLs, accessing cloud metadata, internal service scanning.
- **Common CWEs**: CWE-918 (SSRF)
- **Detection**: Code review for URL fetching, DAST for SSRF payloads
- **Tools**: semgrep (SSRF patterns), nuclei (SSRF templates), manual testing
- **Fix patterns**: URL allowlisting, block internal/metadata IPs, validate schemes, use network segmentation

## Severity Classification

| Severity | CVSS Range | Description | Example |
|----------|-----------|-------------|---------|
| Critical | 9.0-10.0 | Immediate exploitation risk, full system compromise | RCE, auth bypass, exposed admin |
| High | 7.0-8.9 | Significant impact, exploitation likely | SQLi, stored XSS, credential leak |
| Medium | 4.0-6.9 | Moderate impact, requires some conditions | Reflected XSS, CSRF, info disclosure |
| Low | 0.1-3.9 | Minor impact, limited exploitation | Missing headers, verbose errors |
| Info | 0.0 | Informational, no direct security impact | Technology fingerprint, open ports |

## Tool-to-OWASP Mapping

| Tool | Primary OWASP Categories |
|------|-------------------------|
| trufflehog | A02, A07 |
| semgrep | A03, A04, A05, A07, A08, A10 |
| trivy | A06 |
| npm audit / pip-audit | A06 |
| nmap | A05 (recon) |
| nuclei | A01, A03, A05, A07, A10 |
| sqlmap | A03 |
| dalfox | A03 |
| ffuf | A01, A05 |
| hydra | A07 |
| photon | Recon (information gathering) |
