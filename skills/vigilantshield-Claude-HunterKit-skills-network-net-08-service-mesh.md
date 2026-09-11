---
name: net-08-service-mesh
sequence: net-08
category: infrastructure
domain: net
description: "Service mesh security (Istio, Linkerd, Consul): sidecar proxy bypass, mTLS stripping, Envoy admin interface, mesh traffic interception, and service-to-service auth bypass."
wordlist_ref: "wordlists/network/net-46-service-mesh/"
---

# Net 08 Service Mesh — Offensive Methodology

## Shortcut
1. Check Envoy admin on 15000 (config dump, certs, clusters)
2. Check Istio Pilot on 8080 (service endpoints)
3. Test mTLS stripping — send plain HTTP
4. Enumerate mesh services via Envoy clusters

## Detection
```bash
# Envoy admin
curl http://127.0.0.1:15000/config_dump
curl http://127.0.0.1:15000/clusters
```


## Hacker Mindset

**Default mindset for skills without specific template.** Every security boundary is a hypothesis. Test it. If it breaks, that's the finding. Always escalate from single finding to chain.

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

**Wordlist**: `wordlists/network/net-46-service-mesh/` (5 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

