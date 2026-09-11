---
name: subfinder
description: >
  此技能适用于用户询问关于 "subfinder"、"查找子域名"、"枚举攻击面"、"发现隐藏主机"、"在不直接接触目标的情况下被动探测目标域名基础设施"。使用 40+ OSINT 来源的被动子域名枚举工具。
---

# Subfinder

快速被动子域名枚举工具 —— ProjectDiscovery 工具集的一部分。

## 快速开始

```bash
# 枚举某域名的子域名
subfinder -d example.com

# 输出到文件
subfinder -d example.com -o subs.txt

# 静默模式（仅输出子域名，不显示横幅）
subfinder -d example.com -silent
```

## 核心参数

| 参数 | 说明 |
|------|-------------|
| `-d <domain>` | 目标域名 |
| `-dL <file>` | 从文件读取域名列表 |
| `-o <file>` | 输出文件 |
| `-oJ` | JSON 格式输出 |
| `-silent` | 仅输出子域名 |
| `-t <n>` | 线程数（默认 10） |
| `-timeout <n>` | 每个来源的超时时间（秒） |
| `-all` | 使用所有来源（速度较慢，结果更多） |
| `-recursive` | 递归枚举 |
| `-active` | 对结果进行主动 DNS 验证 |
| `-v` | 详细输出 |

## API 密钥配置

在 `~/.config/subfinder/provider-config.yaml` 中配置 API 密钥：

```yaml
shodan:
  - YOUR_SHODAN_KEY
virustotal:
  - YOUR_VT_KEY
censys:
  - YOUR_CENSYS_ID:YOUR_SECRET
binaryedge:
  - YOUR_KEY
```

不配置 API 密钥时，subfinder 仍可使用免费来源（crt.sh、hackertarget 等）。

## 常用工作流

```bash
# 枚举 + 通过管道传给 httpx 检测存活主机
subfinder -d example.com -silent | httpx -silent

# 递归枚举
subfinder -d example.com -recursive -silent -o all_subs.txt

# 从文件批量处理多个域名
subfinder -dL domains.txt -silent -o subs.txt

# 使用所有来源以获取最大覆盖率
subfinder -d example.com -all -silent

# JSON 输出，便于自动化处理
subfinder -d example.com -oJ -o subs.json
```

## 参考资源

| 文件 | 何时加载 |
|------|--------------|
| `references/providers.md` | 支持的被动来源完整列表及 API 密钥配置说明 |
