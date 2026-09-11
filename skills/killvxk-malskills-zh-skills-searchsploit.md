---
name: searchsploit
description: >
  此技能适用于用户询问关于"searchsploit"、"在漏洞研究和利用前阶段查找已发现 CVE 和软件版本的公开利用代码"。Exploit-DB 的离线 CLI 搜索工具。
---

# SearchSploit

离线 Exploit-DB 搜索 — 通过软件名称、版本或 CVE 查找公开利用代码。

## 快速开始

```bash
# 安装
apt install exploitdb

# 按产品搜索
searchsploit apache 2.4

# 按 CVE 搜索
searchsploit CVE-2021-41773

# 精确短语搜索
searchsploit -e "remote code execution"

# 复制利用代码到当前目录
searchsploit -m 50383
```

## 核心参数

| 参数 | 用途 |
|------|------|
| `-t TERM` | 仅搜索标题 |
| `-e TERM` | 精确匹配 |
| `-m ID` | 镜像/复制利用文件 |
| `-p ID` | 显示完整路径 |
| `-x ID` | 在分页器中查看利用代码 |
| `--cve CVE` | 按 CVE 搜索 |
| `-w` | 显示 Web URL（exploitdb.com） |
| `--nmap FILE` | 解析 Nmap XML 并查找利用代码 |
| `-u` | 更新本地数据库 |
| `--id` | 显示 EDB-ID |

## 常用工作流

**从 Nmap 扫描结果查找利用代码：**
```bash
nmap -sV target.com -oX scan.xml
searchsploit --nmap scan.xml
```

**查看并复制相关利用代码：**
```bash
searchsploit -x 50383     # 阅读
searchsploit -m 50383     # 复制到 ./
```

**更新本地数据库：**
```bash
searchsploit -u
```

## 资源文件

| 文件 | 加载时机 |
|------|----------|
| `references/` | 利用代码修改与编译说明 |
