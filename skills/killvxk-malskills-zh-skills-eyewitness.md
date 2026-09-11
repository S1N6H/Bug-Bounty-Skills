---
name: eyewitness
description: >
  此技能适用于用户询问关于 "eyewitness"、"可视化枚举 Web 服务"、"对 URL/主机列表截图"、"生成 Web 资产视觉清单"、"创建已发现 Web 界面报告" 的场景。对 Web 服务截图并生成 HTML 报告的工具。
---

# EyeWitness

对 Web 服务截图并生成包含分类结果的 HTML 报告。

## 快速开始

```bash
# 从 URL 列表截图
eyewitness -f urls.txt --web

# 从 nmap XML 截图
eyewitness -x nmap_scan.xml --web

# 指定输出目录
eyewitness -f urls.txt --web -d output/eyewitness
```

## 核心参数

| 参数 | 说明 |
|------|-------------|
| `-f <file>` | 含 URL/主机的输入文件 |
| `-x <xml>` | Nmap XML 输出文件 |
| `--web` | HTTP 截图（默认） |
| `--rdp` | RDP 截图 |
| `--vnc` | VNC 截图 |
| `-d <dir>` | 输出目录 |
| `--no-prompt` | 跳过交互式提示 |
| `--timeout <n>` | 每个目标超时时间（默认 7s） |
| `--threads <n>` | 线程数（默认 10） |
| `--delay <n>` | 请求间延迟 |
| `--proxy-ip <ip>` | 代理 IP |
| `--proxy-port <port>` | 代理端口 |
| `--resolve` | 解析 IP 地址 |
| `--add-http-headers <h>` | 添加自定义请求头 |
| `--user-agent <ua>` | 自定义 User-Agent |
| `--prepend-https` | 在输入前添加 https:// |
| `--prepend-http` | 在输入前添加 http:// |
| `--active-scan` | 主动指纹识别 |
| `--jitter <n>` | 截图间随机抖动 |

## 常用工作流

```bash
# 对子域名列表截图
cat subs.txt | sed 's/^/http:\/\//' > urls.txt
eyewitness -f urls.txt --web -d report/ --no-prompt

# 从 nmap 扫描结果生成报告
nmap -sV -p 80,443,8080,8443 -oX scan.xml 192.168.1.0/24
eyewitness -x scan.xml --web -d web_report/ --no-prompt

# 同时截取 HTTP 和 HTTPS
eyewitness -f hosts.txt --prepend-http --prepend-https --web -d out/

# 对内网进行 RDP 截图
eyewitness -f hosts.txt --rdp -d rdp_report/
```

## 输出内容

EyeWitness 生成：
- `report.html` — 带 HTTP 请求头的分类截图报告
- `Matches/` — 感兴趣的分类（登录页、Cisco、Citrix 等）
- `Screenshots/` — 原始截图图片

## 资源

| 文件 | 何时加载 |
|------|--------------|
| `references/report-structure.md` | HTML 报告结构、分类说明、与其他工具集成 |
