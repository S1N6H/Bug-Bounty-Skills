---
name: sublist3r
description: >
  此技能适用于用户询问关于 "sublist3r"、"通过公开搜索引擎和威胁情报平台被动枚举子域名"。使用 OSINT 来源（Google、Bing、Baidu、DNSDumpster、VirusTotal、ThreatCrowd）进行子域名枚举的工具。
---

# Sublist3r

通过 OSINT 进行被动子域名枚举 —— 支持搜索引擎、DNSDumpster、VirusTotal 等来源。

## 快速开始

```bash
pip install sublist3r

# 基础子域名枚举
sublist3r -d target.com

# 启用暴力破解
sublist3r -d target.com -b -w wordlist.txt

# 保存输出
sublist3r -d target.com -o subdomains.txt

# 详细模式（显示来源）
sublist3r -d target.com -v
```

## 核心参数

| 参数 | 用途 |
|------|---------|
| `-d DOMAIN` | 目标域名 |
| `-b` | 启用暴力破解 |
| `-w FILE` | 暴力破解字典文件 |
| `-p PORTS` | 检测发现主机上的指定端口 |
| `-v` | 详细模式（显示每个来源） |
| `-t N` | 线程数（默认 10） |
| `-o FILE` | 输出文件 |
| `-e ENGINES` | 以逗号分隔的搜索引擎列表 |

## 使用的来源

Google · Bing · Yahoo · Baidu · Ask · Netcraft · DNSDumpster · VirusTotal · ThreatCrowd · SSL 证书 · PassiveDNS

## 常用工作流

**仅被动模式（隐蔽性高）：**
```bash
sublist3r -d target.com -o passive_subs.txt
```

**主动暴力破解 + 被动枚举组合：**
```bash
sublist3r -d target.com -b -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -o all_subs.txt
```

**通过管道传给解析器：**
```bash
sublist3r -d target.com -o subs.txt
cat subs.txt | dnsx -silent -a -resp > live.txt
```

## 参考资源

| 文件 | 何时加载 |
|------|--------------|
| `references/` | 搜索引擎 API 密钥及字典来源 |
