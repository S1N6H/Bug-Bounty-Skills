---
name: net-14-ai-infra
sequence: net-14
category: infrastructure
domain: net
description: "AI infrastructure security: MLflow endpoints, model registries, training infrastructure, inference endpoints, Jupyter notebook access, and model theft vectors."
wordlist_ref: "wordlists/network/net-56-ai-infra/"
---

# Net 14 Ai Infra — Offensive Methodology

## Shortcut
1. Check MLflow on 5000 (experiments, models, runs)
2. Check Jupyter on 8888 (tokens, notebook access)
3. Check model serving endpoints (/invocations, /predict)
4. Check training infrastructure (Weights & Biases, Sagemaker)

## Detection
```bash
# MLflow
curl http://target.com:5000/api/2.0/mlflow/experiments/list

# Jupyter
curl http://target.com:8888/api/contents

# Model serving
curl http://target.com/invocations -d '{"inputs": "test"}'
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

**Wordlist**: `wordlists/network/net-56-ai-infra/` (2 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

