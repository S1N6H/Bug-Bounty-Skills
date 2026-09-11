---
name: dotdotpwn
description: >
  此技能适用于用户询问关于 "dotdotpwn"、"测试 HTTP、FTP 和 TFTP 服务中的路径遍历和 LFI 漏洞" 的场景。针对 Web 服务器和应用程序的目录遍历漏洞模糊测试工具。
---

# DotDotPwn

目录遍历模糊测试工具 — 测试 HTTP、FTP、TFTP 的路径遍历漏洞。

## 快速开始

```bash
apt install dotdotpwn

# HTTP 遍历
dotdotpwn -m http -h target.com -x 80

# 指定 URL 的 HTTP 遍历
dotdotpwn -m http -h target.com -U "http://target.com/page?file=TRAVERSAL"

# FTP 遍历
dotdotpwn -m ftp -h target.com -x 21 -u user -p pass
```

## 核心参数

| 参数 | 说明 |
|------|---------|
| `-m MODULE` | 模块：http/http-url/ftp/tftp/payload |
| `-h HOST` | 目标主机 |
| `-x PORT` | 目标端口 |
| `-U URL` | 含 TRAVERSAL 占位符的 URL |
| `-u USER` | 用户名（FTP） |
| `-p PASS` | 密码（FTP） |
| `-f FILE` | 目标文件（如 `/etc/passwd`） |
| `-d N` | 遍历深度（默认：6） |
| `-t N` | 请求间隔时间（毫秒） |
| `-q` | 静默模式 |
| `-s` | 找到第一个后停止 |

## 常用工作流

**使用自定义路径的 HTTP-URL 遍历：**
```bash
dotdotpwn -m http-url -h target.com -U "http://target.com/download.php?file=TRAVERSAL" -f /etc/passwd -d 8 -q
```

**Windows 目标：**
```bash
dotdotpwn -m http -h target.com -f "windows/system32/cmd.exe" -d 6
```

## 资源

| 文件 | 何时加载 |
|------|--------------|
| `references/` | 编码绕过与 Windows 路径说明 |
