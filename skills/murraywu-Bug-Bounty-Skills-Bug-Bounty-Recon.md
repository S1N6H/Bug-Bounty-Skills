# Bug-Bounty-Recon - 信息收集自动化指南

**来源**: Bug Bounty 课程学习提取
**版本**: 1.0
**创建时间**: 2026-04-02

---

## 功能描述

提供信息收集 (Recon) 方法论、工具使用指南、自动化脚本。

**⚠️ 仅用于授权测试**

---

## Recon 流程

### 阶段 1: 子域名枚举
```bash
# Amass
amass enum -d target.com

# subfinder
subfinder -d target.com -o subs.txt

# sublist3r
python sublist3r.py -d target.com -o subs.txt

# 合并去重
cat *.txt | sort -u > final_subs.txt
```

### 阶段 2: 端口扫描
```bash
# Nmap
nmap -sV -sC -oA scan target.com

# Masscan (快速)
masscan -p1-65535 target.com --rate 1000

# naabu
naabu -list subs.txt -o ports.txt
```

### 阶段 3: HTTP 探测
```bash
# httpx
cat subs.txt | httpx -title -tech-detect -status-code -o httpx.txt

# 筛选存活
cat httpx.txt | grep "200 OK"
```

### 阶段 4: 目录发现
```bash
# FFuF
ffuf -w wordlist.txt -u https://target.com/FUZZ -o results.txt

# dirsearch
dirsearch -u https://target.com -e php,js,html

# feroxbuster
feroxbuster -u https://target.com -w wordlist.txt
```

### 阶段 5: 参数发现
```bash
# Param Miner (Burp 扩展)

# waybackurls
cat subs.txt | waybackurls | tee urls.txt

# gau
gau target.com | tee urls.txt

# 提取带参数的 URL
cat urls.txt | grep "?" | sort -u > params.txt
```

### 阶段 6: 技术栈识别
```bash
# whatweb
whatweb target.com

# Wappalyzer (浏览器扩展)

# BuiltWith (网站查询)
```

### 阶段 7: 敏感信息
```bash
# GitHub 搜索
site:github.com target.com password
site:github.com target.com api_key

# gitGraber
python gitGraber.py -q target.com

# 检查 JS 文件
cat urls.txt | grep ".js" | xargs -I {} curl {} | grep -E "api|key|secret"
```

---

## 推荐工具

| 工具 | 用途 |
|------|------|
| Amass | 子域名枚举 |
| subfinder | 被动子域名发现 |
| Nmap | 端口扫描 |
| httpx | HTTP 探测 |
| FFuF | 目录爆破 |
| waybackurls | 历史 URL |
| nuclei | 漏洞扫描 |
| SecLists | 字典集合 |

---

## 自动化脚本模板

```bash
#!/bin/bash
# recon.sh - 基础 Recon 脚本

TARGET=$1

echo "[*] Starting recon for $TARGET"

# 子域名
echo "[*] Enumerating subdomains..."
subfinder -d $TARGET -o subs.txt

# HTTP 探测
echo "[*] Probing HTTP..."
cat subs.txt | httpx -title -status-code -o httpx.txt

# 目录扫描
echo "[*] Scanning directories..."
ffuf -w wordlist.txt -u https://$TARGET/FUZZ -o dirs.txt

echo "[*] Recon complete!"
```

---

## 字典资源

- **SecLists**: https://github.com/danielmiessler/SecLists
- **AssetNote Wordlists**: https://wordlists.assetnote.io/
- **dirb**: /usr/share/dirb/wordlists/

---

## 注意事项

1. **速率限制**: 避免触发 WAF/IPS
2. **合法授权**: 确保有测试授权
3. **记录保存**: 保存所有发现
4. **去重**: 合并多个工具结果

---

## 安全声明

⚠️ **仅用于授权测试**
❌ 禁止用于未授权扫描

---

*Bug-Bounty-Recon v1.0 | 2026-04-02*
