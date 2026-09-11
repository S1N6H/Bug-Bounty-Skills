---
name: feroxbuster
description: >
  此技能适用于用户询问关于 "feroxbuster"、"递归枚举 Web 目录"、"发现隐藏文件/端点"、"对 Web 应用进行模糊测试"、"需要 gobuster 原生不支持的深度递归扫描" 的场景。用 Rust 编写的快速递归 Web 内容发现工具。
---

# Feroxbuster

递归、快速内容发现工具 — 支持 JavaScript 渲染的应用，并自动递归进入发现的目录。

## 快速开始

```bash
# 基础扫描
feroxbuster -u http://example.com -w /usr/share/wordlists/dirb/common.txt

# 带扩展名
feroxbuster -u http://example.com -w common.txt -x php,html,txt

# 不递归（平铺扫描）
feroxbuster -u http://example.com -w common.txt --no-recursion
```

## 核心参数

| 参数 | 说明 |
|------|-------------|
| `-u <url>` | 目标 URL |
| `-w <wordlist>` | 字典文件（用 `-` 从 stdin 读取） |
| `-x <ext>` | 逗号分隔的文件扩展名 |
| `-t <n>` | 线程数（默认 50） |
| `-d <n>` | 递归深度（默认 4，0 = 无限制） |
| `--no-recursion` | 禁用递归 |
| `-s <codes>` | 匹配的状态码（默认 `200,204,301,302,307,308,401,403,405`） |
| `-C <codes>` | 过滤/排除的状态码 |
| `-S <size>` | 按响应大小过滤 |
| `-W <words>` | 按词数过滤 |
| `-L <lines>` | 按行数过滤 |
| `-H <header>` | 自定义 HTTP 请求头 |
| `-b <cookie>` | Cookie 值 |
| `-k` | 禁用 TLS 验证 |
| `-r` | 跟随重定向 |
| `--proxy <url>` | HTTP/SOCKS5 代理 |
| `-o <file>` | 输出文件 |
| `-q` | 静默模式（无进度条） |
| `--json` | JSON 格式输出 |
| `--auto-tune` | 出错时自动降速 |
| `--smart-auto-tune` | 仅在 429/503 时降速 |

## 过滤示例

```bash
# 过滤掉 404 和 302
feroxbuster -u http://target.com -w common.txt -C 404,302

# 按响应大小过滤（隐藏 0 字节响应）
feroxbuster -u http://target.com -w common.txt -S 0

# 仅显示 200 响应
feroxbuster -u http://target.com -w common.txt -s 200
```

## 常用工作流

```bash
# 带扩展名的递归扫描，输出到文件
feroxbuster -u https://target.com -w raft-medium.txt -x php,bak,conf -o results.txt

# API 端点发现（以 JSON 为主）
feroxbuster -u https://api.target.com -w api-endpoints.txt -x json -H "Accept: application/json"

# 带认证的扫描
feroxbuster -u https://target.com -w common.txt -H "Authorization: Bearer TOKEN"

# 通过代理（Burp）
feroxbuster -u http://target.com -w common.txt --proxy http://127.0.0.1:8080 -k

# 快速激进扫描
feroxbuster -u http://target.com -w big.txt -t 100 --no-recursion -d 1

# 从文件扫描多个 URL
feroxbuster --stdin -w common.txt < urls.txt
```

## 交互式控制

运行时按键：
- `Enter` — 显示当前状态
- `s` — 停止特定 URL 的扫描
- `q` / `Ctrl+C` — 退出

## 资源

| 文件 | 何时加载 |
|------|--------------|
| `references/filters.md` | 详细过滤参数组合、基于大小/词数/行数的噪声过滤 |
