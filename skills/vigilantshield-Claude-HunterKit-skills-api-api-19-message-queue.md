---

name: api-19-message-queue
sequence: api-19
category: protocol
domain: api
description: "Message queue security testing skill. Covers AMQP/RabbitMQ, Kafka, Redis Pub/Sub, and MQTT injection, queue poisoning, message replay, and authorization bypass in message broker systems. Use when testing message queue integrations."
wordlist_ref: "wordlists/api/api-25-message-queue/"
---

# Message Queue Security — Offensive Testing Methodology

## Quick Workflow

1. Identify attack surface and entry points specific to this vulnerability class
2. Run detection probes to confirm vulnerability presence
3. Escalate with bypass techniques if initial probes are blocked
4. Confirm exploitation and assess impact
5. Document findings with proof of concept and suggest remediation

---

## Purpose
Test message queue and event-driven API security — Kafka topic access control bypass,
RabbitMQ management API exposure, Redis pub/sub interception, SQS/SNS misconfiguration,
message injection, and consumer authentication bypass.

## OWASP API Mapping
- API2:2023 Broken Authentication
- API5:2023 Broken Function Level Authorization
- API8:2023 Security Misconfiguration

## Vulnerability Classes

### 1. Kafka Topic Access Control Bypass
**Attack:** Access topics without authorization (no ACLs configured).


**High-risk Kafka topics:**
```
payments.*, transactions.*, orders.*
user.events, auth.events, audit.*
internal.*, admin.*
```

### 2. RabbitMQ Management API Exposure
**Attack:** RabbitMQ management UI accessible without auth or with default credentials.

```
GET http://target.com:15672/api/queues  → list all queues
GET http://target.com:15672/api/exchanges
GET http://target.com:15672/api/connections
GET http://target.com:15672/api/vhosts
```

**Default credentials:** `guest:guest`, `admin:admin`, `rabbitmq:rabbitmq`

**Sensitive operations:**
```
# Read all messages from queue
GET /api/queues/%2F/payment_queue/get {"count": 100, "requeue": true}

# Publish malicious message
POST /api/exchanges/%2F/amq.default/publish
{"payload": "INJECTED_EVENT", "routing_key": "payment_processed"}
```

### 3. Redis Pub/Sub Eavesdropping
**Attack:** Subscribe to Redis channels to intercept messages.


### 4. SQS/SNS Misconfiguration
**Attack:** Access SQS queues or SNS topics with overly permissive IAM policies.


### 5. Message Injection / Poisoning
**Attack:** Inject malicious messages into queues.


### 6. Dead Letter Queue Data Exposure
**Attack:** Dead letter queues (DLQ) accumulate failed messages including sensitive data.

```
# AWS SQS DLQ
GET /queues?QueueNamePrefix=dlq
# Read all failed events → may include full request bodies with PII/credentials

# Kafka consumer group lag → stranded messages → accessible if DLQ readable
```

### 7. Schema Registry Abuse
**Attack:** Inject malicious Avro/Protobuf schema to affect message serialization.

```
POST /subjects/payments-value/versions
{"schema": "{\"type\":\"record\",\"fields\":[{\"name\":\"inject\",\"default\":\"MALICIOUS\"}]}"}
# Schema registry accepts → new consumers use injected schema
```

---

# Detect MQ technology
# Probe common MQ management ports
# RabbitMQ default creds
## Attack Surface (Parameter Matrix)

| Surface | MQ Tests |
|---------|----------|
| Kafka bootstrap port | Topic ACL bypass, message read |
| RabbitMQ management API | Default creds, queue read |
| Redis port | No-auth access, pub/sub |
| SQS queue URLs | IAM policy misconfiguration |
| SNS topic ARNs | Unauthorized subscription |
| Schema registry | Schema injection |
| Dead letter queues | Sensitive message exposure |

---

## HackerOne Report Patterns

**Pattern 1: RabbitMQ guest:guest in production (H1 Critical)**
Management API on port 15672 with default `guest:guest` → read all queues → read all messages including payment events.

**Pattern 2: Kafka no ACLs → all topics readable (H1 Critical)**
No Kafka ACLs → subscribe to `payments.*` topic → all transaction data readable.

**Pattern 3: Redis no auth → KEYS * (H1 Critical)**
Redis on port 6379 without requirepass → KEYS * → full data dump including sessions, cache, pub/sub.

**Pattern 4: Public SQS queue → payment event interception (H1 Critical)**
SQS queue policy `"Principal": "*"` → anyone reads payment processing queue → GDPR violation.

---

## Zero-Day Research Hooks

### Novel MQ Vectors
- Kafka Connect REST API: if exposed, allows creating connectors → SSRF via JDBC connector URL
- Schema registry AVRO injection: malicious AVRO schema → deserialization gadget chain in consumers
- MSK (managed Kafka) IAM auth bypass: misconfigured trust policy → cross-account access
- NATS.io cluster: NATS server without auth → subscribe to all subjects
- Pulsar admin REST API: Apache Pulsar admin API without auth → full tenant control

---

## False Positive Mitigation
- Default creds: confirm actual data returned (not test environment)
- Topic read: confirm actual sensitive data in messages
- Redis: confirm data contains real information (not empty cache)
- NEVER emit on single signal

---




## Hacker Mindset

**Look for the edge cases.** Vulnerabilities live in the gap between what the developer assumed and what the framework actually does. Test every boundary: empty values, nulls, arrays, negative numbers, Unicode, very long strings.

**Blind detection always needs OOB.** If you can't see the output, set up a callback. No OOB = no confirmation.

**Chaining turns low/med into critical.** A single path traversal is medium. Path traversal + log file + admin session = RCE. Always think about what comes next.



## Chaining & Escalation

### Direct Escalation
This vulnerability can often be escalated directly. Test for RCE, data access, or privilege escalation depending on context.

### Chain with Other Skills
| Partner Vulnerability | Chain Effect |
|----------------------|--------------|
| SSRF | Use SSRF to reach internal services through this vuln |
| XSS | Stolen sessions amplify account-level findings |
| IDOR/BOLA | Find more data to exploit via authorization gaps |

### Amplification
Race conditions, parallel requests, and HTTP/2 single-packet attacks can amplify impact by 10-50x.



## OOB Detection & Blind Confirmation

### Blind Confirmation
Always set up OOB detection before testing. Use:
- **Burp Collaborator** — built into Burp Suite Pro
- **Interactsh** — OOB detection server (https://app.interactsh.com)
- **Canarytokens** for callback detection

### Timing Side-Channel
If OOB is blocked, use time-based detection:
- Inject `sleep(5)` or equivalent
- Compare response times between baseline and injected requests
- 5s+ delay = vulnerability confirmed



## Tools

- Burp Suite (manual testing + Intruder)
- curl / httpx
- Nuclei templates

## Wordlist Invocation

When testing this vulnerability, invoke the wordlist payloads manually:

**Wordlist**: `wordlists/api/api-25-message-queue/`

**Files**:
- `wordlists/api/api-25-message-queue/payloads/sqli/` — staged exploit payloads (low → med → high)

**Workflow**:
1. Start with `low` stage payloads — minimal risk probes
2. If signals detected, escalate to `med` stage
3. Use `high` only after confirmation (OOB/time-based where applicable)
4. Always establish a baseline response before running time-based payloads

**Tools**: curl, httpx, Burp Suite, or any HTTP client

