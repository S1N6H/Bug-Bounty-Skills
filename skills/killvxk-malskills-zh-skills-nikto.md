---
name: nikto
description: >
  此技能适用于用户询问关于 "nikto"、"在深度手动测试前快速进行 Web 服务器侦察以识别低挂果实、服务器 banner 和默认内容"、
  "Web 服务器漏洞扫描" 的问题。
---

# Nikto

Web 服务器漏洞与配置错误扫描器。

## 快速开始

```bash
nikto -h http://target.com
nikto -h https://target.com -ssl
nikto -h target.com -p 8443 -o nikto.txt -Format txt
```

## 核心参数

| 参数 | 用途 |
|------|---------|
| `-h <host>` | 目标主机/URL |
| `-p <port>` | 端口（默认 80/443） |
| `-ssl` | 强制使用 SSL |
| `-id <user:pass>` | HTTP 基本认证 |
| `-useproxy <proxy>` | 通过代理路由流量 |
| `-Tuning <n>` | 扫描调优位掩码 |
| `-o <file>` | 输出文件 |
| `-Format <fmt>` | csv / txt / xml / html |

## 调优值

| 值 | 含义 |
|-------|---------|
| 1 | 有趣的文件 |
| 2 | 配置错误 |
| 3 | 信息泄露 |
| 4 | XSS 注入 |
| 8 | 命令执行 |
| 9 | SQL 注入 |

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | 插件列表、认证绕过技术 |
