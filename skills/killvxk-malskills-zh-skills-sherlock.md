---
name: sherlock
description: >
  此技能适用于用户询问关于"sherlock"、"在 OSINT 侦察过程中基于发现的用户名进行横向关联，绘制目标在各平台的数字足迹"。在 400+ 个社交网络上搜索用户名。
---

# Sherlock

跨 400+ 个社交平台的用户名追踪工具。

## 快速开始

```bash
pip install sherlock-project

# 搜索单个用户名
sherlock username

# 搜索多个用户名
sherlock user1 user2 user3

# 输出到文件
sherlock username --output results.txt

# JSON 格式输出
sherlock username --json
```

## 核心参数

| 参数 | 用途 |
|------|------|
| `--timeout N` | 每个站点的超时时间（默认：60s） |
| `--print-found` | 仅显示已找到的账户 |
| `--print-all` | 显示全部结果（包括未找到） |
| `--output FILE` | 保存结果 |
| `--json` | JSON 格式 |
| `--site NAME` | 仅搜索指定站点 |
| `--csv` | CSV 格式输出 |
| `-x XLSX` | Excel 格式输出 |

## 常用工作流

**从泄露数据追踪用户名：**
```bash
sherlock johndoe_83 --print-found --output johndoe_found.txt
```

**多个用户名变体搜索：**
```bash
sherlock "john.doe" johndoe john_doe jdoe --print-found
```

**针对特定站点查询：**
```bash
sherlock johndoe --site twitter --site github --site linkedin
```

## 资源文件

| 文件 | 加载时机 |
|------|----------|
| `references/` | 用户名变体生成技术 |
