---
name: massdns
description: >
  此技能适用于用户询问关于 "massdns"、"拥有大量子域名列表并需要使用公共解析器快速批量解析"、
  "高性能 DNS 批量解析" 的问题。
---

# MassDNS

高速批量 DNS 解析器 — 每分钟可解析数百万个子域名。

## 快速开始

```bash
git clone https://github.com/blechschmidt/massdns
cd massdns && make

# 解析子域名列表
./bin/massdns -r resolvers.txt -t A subdomains.txt -o S -w resolved.txt

# 使用内置解析器列表
./bin/massdns -r lists/resolvers.txt -t A subdomains.txt -o S > resolved.txt
```

## 核心参数

| 参数 | 用途 |
|------|---------|
| `-r FILE` | 解析器列表文件 |
| `-t TYPE` | DNS 类型（A/AAAA/MX/NS/CNAME） |
| `-o FORMAT` | 输出格式（S=简单, J=JSON, L=列表） |
| `-w FILE` | 将输出写入文件 |
| `-s N` | 并发解析器数量 |
| `--root` | 使用根服务器进行 NS 查询 |
| `--verify-ip` | 验证 A 记录 IP |

## 常见工作流

**子域名枚举流水线：**
```bash
# 用 subfinder 生成候选列表
subfinder -d target.com -silent -o subs.txt

# 用 massdns 解析
./bin/massdns -r lists/resolvers.txt -t A subs.txt -o S | grep -v NXDOMAIN > live.txt
```

**提取存活 IP：**
```bash
cat resolved.txt | grep " A " | awk '{print $3}' | sort -u > ips.txt
```

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | 解析器列表来源和速率调优 |
