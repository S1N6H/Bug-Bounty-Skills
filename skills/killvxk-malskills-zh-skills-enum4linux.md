---
name: enum4linux
description: >
  此技能适用于用户询问关于 "enum4linux"、"枚举 Windows 主机"、"Samba 共享"、"通过 SMB 查找用户"、"提取域信息"、"检查空会话访问" 的场景。通过空会话或凭据提取用户、共享、组、OS 信息和密码策略的 SMB 与 Windows/Samba 枚举工具。
---

# enum4linux

SMB 枚举工具 — 从 Windows/Samba 主机提取用户、共享、组和域信息。

## 快速开始

```bash
# 完整枚举（空会话）
enum4linux -a 192.168.1.10

# 带凭据
enum4linux -a -u admin -p password 192.168.1.10

# 现代重写版本（推荐使用 enum4linux-ng）
enum4linux-ng -A 192.168.1.10
```

## 参数（经典版）

| 参数 | 说明 |
|------|-------------|
| `-a` | 全量枚举：运行 `-U -S -G -P -r -o -n -i` |
| `-U` | 通过 RPC 获取用户列表 |
| `-M` | 机器列表 |
| `-S` | 共享枚举 |
| `-P` | 密码策略 |
| `-G` | 组枚举 |
| `-r` | 通过 RID 轮询获取用户列表 |
| `-R <range>` | RID 范围（默认 `500-550,1000-1050`） |
| `-u <user>` | 认证用户名 |
| `-p <pass>` | 认证密码 |
| `-d` | 调试模式 |
| `-v` | 详细输出 |
| `-o` | 获取 OS 信息 |
| `-i` | 打印机信息 |
| `-n` | Nmblookup 信息 |

## enum4linux-ng 参数（推荐）

| 参数 | 说明 |
|------|-------------|
| `-A` | 全量检查 |
| `-u <user>` | 用户名 |
| `-p <pass>` | 密码 |
| `-oJ <file>` | JSON 格式输出 |
| `-oY <file>` | YAML 格式输出 |
| `-t <n>` | 超时时间 |
| `--no-color` | 禁用彩色输出 |

## 常用工作流

```bash
# 无凭据的完整空会话枚举
enum4linux -a 10.10.10.100

# 带凭据的完整枚举
enum4linux -a -u "DOMAIN\user" -p "password" 10.10.10.100

# RID 轮询进行用户枚举
enum4linux -r -R 500-2000 10.10.10.100

# 使用 JSON 输出的现代方式
enum4linux-ng -A 10.10.10.100 -oJ output.json

# 仅枚举共享
enum4linux -S 10.10.10.100

# 提取密码策略
enum4linux -P 10.10.10.100
```

## 可提取的关键信息

- 域名/工作组名称及 OS 版本
- 用户账户（通过 RPC 和 RID 暴力破解）
- 共享（可写/可读）
- 组成员关系
- 密码策略（锁定阈值、复杂度要求）
- 打印机和会话信息

## 资源

| 文件 | 何时加载 |
|------|--------------|
| `references/smb-enumeration.md` | SMB 枚举技术、smbclient 命令、空会话利用 |
