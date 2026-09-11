---
name: masscan
description: >
  此技能适用于用户询问关于 "masscan"、"执行大范围网络扫描"、
  "识别大型 CIDR 范围的开放端口"、"在 nmap 服务扫描前作为初步发现步骤" 的问题。
---

# Masscan

超高速 TCP SYN 扫描器，用于大规模端口发现。

## 快速开始

```bash
masscan 10.0.0.0/16 -p445 --rate=10000 -oG out.gnmap
masscan 10.0.0.0/8 -p0-1023 --rate=50000 -oX out.xml
masscan -iL targets.txt -p80,443,8080,445 --rate=10000
```

## 核心参数

| 参数 | 用途 |
|------|---------|
| `-p <ports>` | 端口列表/范围（如 `0-65535`、`80,443`） |
| `--rate <n>` | 每秒发包数（从低速开始） |
| `-oG / -oX / -oJ` | 输出格式：grepable / XML / JSON |
| `-iL <file>` | 从文件读取目标 |
| `--banners` | 抓取服务 banner |
| `--excludefile` | 排除指定 IP |
| `--adapter-ip` | 源 IP 地址 |
| `--router-mac` | 默认网关 MAC 地址 |

## 常见工作流

### 将结果导入 nmap
```bash
masscan 10.0.0.0/24 -p1-65535 --rate=5000 -oG masscan.out
grep "open" masscan.out | awk '{print $4}' | cut -d/ -f1 | sort -u > ports.txt
nmap -sV -p$(paste -sd, ports.txt) -iL hosts.txt
```

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | 扩展选项与调优说明 |
