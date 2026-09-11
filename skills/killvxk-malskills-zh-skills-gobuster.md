---
name: gobuster
description: >
  此技能适用于用户询问关于 "gobuster"、"枚举 Web 目录"、"发现隐藏路径"、"通过 DNS 暴力破解子域名"、"发现 Web 服务器上的虚拟主机" 的场景。用 Go 编写的目录、DNS 子域名和虚拟主机暴力破解工具。
---

# Gobuster

基于 Go 的暴力破解工具，支持目录、DNS 和虚拟主机枚举。

## 快速开始

```bash
# 目录暴力破解
gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt

# DNS 子域名枚举
gobuster dns -d example.com -w /usr/share/wordlists/subdomains.txt

# 虚拟主机发现
gobuster vhost -u http://example.com -w /usr/share/wordlists/subdomains.txt
```

## 模式

| 模式 | 说明 |
|------|-------------|
| `dir` | 目录/文件枚举 |
| `dns` | DNS 子域名暴力破解 |
| `vhost` | 虚拟主机发现 |
| `fuzz` | 通用模糊测试（URL 路径/参数） |
| `s3` | 枚举开放的 S3 存储桶 |
| `gcs` | Google Cloud Storage 存储桶 |

## Dir 模式参数

| 参数 | 说明 |
|------|-------------|
| `-u <url>` | 目标 URL |
| `-w <wordlist>` | 字典路径 |
| `-t <n>` | 线程数（默认 10） |
| `-x <ext>` | 文件扩展名（如 `php,html,txt`） |
| `-s <codes>` | 允许的状态码（默认 `200,204,301,302,307,401,403`） |
| `-b <codes>` | 黑名单状态码 |
| `-r` | 跟随重定向 |
| `-k` | 跳过 TLS 验证 |
| `-H <header>` | 自定义请求头（如 `"Authorization: Bearer TOKEN"`） |
| `-c <cookie>` | 添加 Cookie |
| `--timeout <duration>` | HTTP 超时（如 `10s`） |
| `-o <file>` | 输出文件 |
| `-q` | 静默模式（不显示横幅） |
| `--no-error` | 抑制错误输出 |

## DNS 模式参数

| 参数 | 说明 |
|------|-------------|
| `-d <domain>` | 目标域名 |
| `-w <wordlist>` | 字典 |
| `-r <resolver>` | 自定义 DNS 解析器 |
| `--wildcard` | 检测到通配符 DNS 时强制继续 |

## 常用工作流

```bash
# 带扩展名的目录枚举，输出到文件
gobuster dir -u https://target.com -w common.txt -x php,html,bak -o dirs.txt -q

# 带认证的目录枚举
gobuster dir -u https://target.com -w common.txt -H "Authorization: Bearer <token>"

# 递归式：对发现的目录继续枚举
gobuster dir -u https://target.com/api/ -w api-endpoints.txt -x json

# 使用自定义解析器的 DNS 枚举
gobuster dns -d target.com -w subdomains-top1m.txt -r 8.8.8.8 -t 50

# 虚拟主机发现（为不匹配结果追加域名）
gobuster vhost -u http://target.com -w subdomains.txt --append-domain
```

## 推荐字典

- `/usr/share/wordlists/dirb/common.txt` — 通用目录
- `/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt` — 综合列表
- `SecLists/Discovery/Web-Content/raft-medium-directories.txt` — raft 列表
- `SecLists/Discovery/DNS/subdomains-top1million-5000.txt` — DNS 枚举

## 资源

| 文件 | 何时加载 |
|------|--------------|
| `references/wordlists.md` | 按模式和目标类型推荐的字典 |
