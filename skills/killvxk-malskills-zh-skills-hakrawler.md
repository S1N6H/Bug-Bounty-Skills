---
name: hakrawler
description: >
  此技能适用于用户询问关于"hakrawler"、"爬取 Web 应用以在模糊测试前建立 URL 清单"、"对 Web 基础设施进行 OSINT 时"。快速 Go Web 爬虫，用于发现 URL、端点和 JavaScript 文件。
---

# Hakrawler

快速 Go Web 爬虫 — 发现 URL、JS 文件、表单和端点。

## 快速开始

```bash
go install github.com/hakluke/hakrawler@latest

# 爬取一个域名
echo https://target.com | hakrawler

# 深度 3，包含子域名
echo https://target.com | hakrawler -d 3 -subs

# 输出为 JSON
echo https://target.com | hakrawler -json

# 管道输入多个域名
cat domains.txt | hakrawler -d 2
```

## 核心参数

| 参数 | 用途 |
|------|------|
| `-d N` | 深度（默认：1） |
| `-subs` | 包含子域名 |
| `-u` | 仅输出唯一 URL |
| `-insecure` | 跳过 TLS 验证 |
| `-t N` | 线程数 |
| `-timeout N` | 每个请求的超时时间（秒） |
| `-H "K:V"` | 自定义请求头 |
| `-json` | JSON 输出 |
| `-scope REGEX` | 限制到匹配 URL 模式 |

## 常用工作流

**为模糊测试建立 URL 清单：**
```bash
echo https://target.com | hakrawler -d 3 -u | tee urls.txt
# 输入给 ffuf
ffuf -w urls.txt:URL -u URL -mc 200
```

**发现 JS 文件：**
```bash
echo https://target.com | hakrawler -d 2 | grep "\.js$"
```

**结合 httpx 进行存活检测：**
```bash
cat domains.txt | hakrawler | httpx -silent -mc 200
```

## 参考资源

| 文件 | 加载时机 |
|------|----------|
| `references/` | 范围过滤和 JS 分析技巧 |
