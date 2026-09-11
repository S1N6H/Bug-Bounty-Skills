---
name: net-09-observability
sequence: net-09
category: infrastructure
domain: net
description: "Observability stack attacks: Prometheus, Grafana, Jaeger, ELK, Datadog agents — unauthenticated metric exposure, dashboard access, trace data leakage, and log injection."
wordlist_ref: "wordlists/network/net-47-observability-stack/"
---

# Net 09 Observability — Offensive Methodology

## Shortcut
1. Check Prometheus on 9090 (query API, targets)
2. Check Grafana on 3000 (default creds, dashboards)
3. Check Jaeger on 16686 (trace data — reveals service topology)
4. Check Elasticsearch on 9200 (data access)

## Detection
```bash
# Prometheus
curl http://target.com:9090/api/v1/targets

# Grafana default creds
curl http://target.com:3000/api/admin/stats

# Jaeger
curl http://target.com:16686/api/traces
```


## Hacker Mindset

**Observability stacks (Prometheus, Grafana, Jaeger, ELK) expose internal topology.** Unauthenticated metric endpoints reveal service names, versions, and configurations.

## Chaining & Escalation

Chain this finding with others for higher impact. Combine low-severity findings into critical attack chains. Always think: what's the next step after this works?

## OOB Detection & Blind Confirmation

Use Burp Collaborator or Interactsh for blind detection. Always set up OOB before firing payloads. Time-based: inject sleep(5) and measure response delay.

## Bypass Techniques

| Filter/Block | Bypass |
|-------------|--------|
| WAF block | Encoding, case variation, comment injection |
| Input sanitization | Double encoding, Unicode, null bytes |
| Rate limiting | X-Forwarded-For rotation, HTTP/2 multiplex |
| Blacklist | Alternative syntax, polyglot payloads |

## Tools

- Burp Suite
- curl / httpx
- Nuclei templates
- Custom Python scripts

## Wordlist Invocation

**Wordlist**: `wordlists/network/net-47-observability-stack/` (1 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

