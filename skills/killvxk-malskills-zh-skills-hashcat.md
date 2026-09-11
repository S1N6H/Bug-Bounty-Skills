---
name: hashcat
description: >
  此技能适用于用户询问关于"hashcat"、"破解密码哈希，从 NTLM/Net-NTLMv2/Kerberos/bcrypt/MD5/SHA 哈希中恢复密码"、"执行字典攻击"、"基于规则的攻击"、"对捕获的哈希进行掩码暴力破解"。支持 300+ 种哈希类型的 GPU 加速离线密码破解工具。
---

# Hashcat

GPU 加速离线哈希破解器 — 进攻性操作中密码恢复的标准工具。

## 快速开始

```bash
# 对 NTLM 哈希进行字典攻击
hashcat -a 0 -m 1000 hashes.txt rockyou.txt

# 基于规则的字典攻击
hashcat -a 0 -m 1000 hashes.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule

# 掩码暴力破解（8 位，大写字母 + 数字）
hashcat -a 3 -m 1000 hashes.txt ?u?u?u?u?d?d?d?d
```

## 攻击模式

| 模式 | 参数 | 说明 |
|------|------|------|
| 字典攻击 | `-a 0` | Dictionary attack |
| 组合攻击 | `-a 1` | 合并两个字典 |
| 暴力破解 | `-a 3` | 掩码/字符集暴力破解 |
| 规则攻击 | `-a 0 -r` | 字典 + 变换规则 |
| 混合攻击 | `-a 6/-a 7` | 字典 + 掩码 或 掩码 + 字典 |

## 常见哈希类型 (`-m`)

| 哈希 | 模式 | 来源 |
|------|------|------|
| NTLM | `1000` | Windows SAM / NTDS dump |
| Net-NTLMv1 | `5500` | Responder 捕获 |
| Net-NTLMv2 | `5600` | Responder 捕获 |
| Kerberos 5 TGS (RC4) | `13100` | Kerberoasting |
| Kerberos 5 AS-REP | `18200` | AS-REP roasting |
| MD5 | `0` | Web 应用、其他 |
| SHA1 | `100` | Web 应用、其他 |
| SHA256 | `1400` | 通用 |
| bcrypt | `3200` | Linux /etc/shadow |
| SHA512crypt | `1800` | Linux /etc/shadow |
| WPA-PMKID | `22000` | WiFi |

## 掩码字符

| 掩码 | 字符集 |
|------|--------|
| `?l` | 小写字母 a-z |
| `?u` | 大写字母 A-Z |
| `?d` | 数字 0-9 |
| `?s` | 特殊字符 |
| `?a` | 所有可打印字符（`?l?u?d?s`） |
| `?b` | 所有字节 0x00-0xFF |

## 核心参数

| 参数 | 说明 |
|------|------|
| `-a <n>` | 攻击模式 |
| `-m <n>` | 哈希类型 |
| `-w <n>` | 工作负载：1=低，2=默认，3=高，4=极限 |
| `-O` | 优化内核（更快，密码长度有限制） |
| `--force` | 忽略 GPU 警告 |
| `-r <file>` | 规则文件 |
| `--increment` | 递增掩码长度 |
| `--increment-min <n>` | 最小掩码长度 |
| `--increment-max <n>` | 最大掩码长度 |
| `-o <file>` | 输出已破解的哈希 |
| `--outfmt <n>` | 输出格式：2=hash:plain，3=plain |
| `--show` | 从 potfile 显示已破解哈希 |
| `--status` | 实时状态 |
| `--restore` | 恢复上一个会话 |
| `-S` | 慢速候选（用于规则） |

## 常用工作流

```bash
# NTLM 配合 rockyou + best64 规则
hashcat -a 0 -m 1000 ntlm.txt rockyou.txt -r best64.rule -O

# Net-NTLMv2（Responder 捕获）
hashcat -a 0 -m 5600 netntlm.txt rockyou.txt -r best64.rule

# Kerberoasting TGS
hashcat -a 0 -m 13100 kerberoast.txt rockyou.txt -r one-rule-to-rule-them-all.rule

# AS-REP roasting
hashcat -a 0 -m 18200 asrep.txt rockyou.txt

# 掩码暴力破解：8 位，任意可打印字符
hashcat -a 3 -m 1000 hashes.txt -1 ?a ?1?1?1?1?1?1?1?1 --increment --increment-min 6

# 字典 + 掩码组合（混合攻击）
hashcat -a 6 -m 1000 hashes.txt rockyou.txt ?d?d?d

# 显示已破解密码
hashcat -m 1000 hashes.txt --show
```

## 参考资源

| 文件 | 加载时机 |
|------|----------|
| `references/rules-and-masks.md` | 规则文件参考、掩码示例、字典推荐、哈希提取命令 |
