---
name: net-04-k8s
sequence: net-04
category: infrastructure
domain: net
description: "Kubernetes security: API server enumeration, kubelet exec, RBAC abuse, service account token theft, etcd access, pod escape, and container breakout."
wordlist_ref: "wordlists/network/net-25-container-k8s/"
---

# Net 04 K8S — Offensive Methodology

## Shortcut
1. Probe K8s API on 6443/443: kubectl get nodes
2. Check kubelet on 10250: authenticated exec
3. Find service account tokens: /var/run/secrets/kubernetes.io/serviceaccount/token
4. Check etcd on 2379 for cluster secrets

## Hacker Mindset
**K8s is an API, not a shell.** Every kubectl command is an API call. If you can reach the API server, you can control the cluster. Service account tokens are the keys to the kingdom.

## Detection
```bash
# API server
curl -k https://target.com:6443/api/v1/nodes

# Kubelet exec
curl -k https://target.com:10250/run/default/nginx/nginx -d "cmd=id"

# Service account token
cat /var/run/secrets/kubernetes.io/serviceaccount/token
```
## Chaining & Escalation

Chain this finding with others for higher impact. Combine low-severity findings into critical attack chains. Always think: what's the next step after this works?

## OOB Detection & Blind Confirmation

Use Burp Collaborator or Interactsh for blind detection. Always set up OOB before firing payloads. Time-based: inject sleep(5) and measure response delay.

## Bypass Techniques

| Filter/Block | Bypass |
|-------------|--------|
| WAF/Input validation | Encoding, case variation, alternative syntax |
| Rate limiting | IP rotation via X-Forwarded-For, endpoint mirror |
| Blacklist | Alternative syntax, polyglot payloads |

## Tools

- Burp Suite
- curl / httpx
- Nuclei templates
- Custom Python scripts

## Wordlist Invocation

**Wordlist**: `wordlists/network/net-25-container-k8s/` (2 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

